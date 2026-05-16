import json
import logging
import os
from functools import lru_cache

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError, PartialCredentialsError
from flask import Flask, render_template, request

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # Elastic Beanstalk and other production environments usually provide
    # environment variables directly, so python-dotenv is only a local helper.
    pass


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_AWS_REGION = "us-east-1"
DEFAULT_MODEL_ID = "amazon.nova-micro-v1:0"
PROMPT_PREFIX = "Correct the grammar of the following text while preserving its meaning:"


class GrammarCorrectionError(Exception):
    """Raised when the grammar correction request cannot be completed."""


def create_app():
    """Create and configure the Flask application."""
    flask_app = Flask(__name__)
    flask_app.config["MAX_INPUT_CHARS"] = int(os.getenv("MAX_INPUT_CHARS", "5000"))

    @flask_app.route("/", methods=["GET", "POST"])
    def index():
        corrected_text = ""
        error_message = ""
        original_text = ""

        if request.method == "POST":
            original_text = request.form.get("text", "").strip()

            if not original_text:
                error_message = "Please enter some text to correct."
            elif len(original_text) > flask_app.config["MAX_INPUT_CHARS"]:
                error_message = (
                    f"Please keep your text under {flask_app.config['MAX_INPUT_CHARS']} characters."
                )
            else:
                try:
                    corrected_text = correct_grammar(original_text)
                except GrammarCorrectionError as exc:
                    error_message = str(exc)

        return render_template(
            "index.html",
            corrected_text=corrected_text,
            error_message=error_message,
            original_text=original_text,
            max_input_chars=flask_app.config["MAX_INPUT_CHARS"],
        )

    @flask_app.get("/health")
    def health():
        """Simple health check endpoint for load balancers and Elastic Beanstalk."""
        return {"status": "ok"}

    return flask_app


@lru_cache(maxsize=1)
def get_bedrock_client():
    """Create the Amazon Bedrock Runtime client using environment configuration."""
    region_name = (
        os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or boto3.Session().region_name
        or DEFAULT_AWS_REGION
    )

    return boto3.client(
        "bedrock-runtime",
        region_name=region_name,
        config=Config(
            connect_timeout=10,
            read_timeout=int(os.getenv("BEDROCK_READ_TIMEOUT", "60")),
            retries={"max_attempts": 3, "mode": "standard"},
        ),
    )


def correct_grammar(text):
    """Send user text to Amazon Bedrock and return the corrected grammar."""
    model_id = os.getenv("BEDROCK_MODEL_ID", DEFAULT_MODEL_ID)
    prompt = f"{PROMPT_PREFIX}\n\n{text}\n\nReturn only the corrected text."

    request_body = {
        "messages": [
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ],
        "inferenceConfig": {
            "maxTokens": int(os.getenv("BEDROCK_MAX_TOKENS", "1000")),
            "temperature": float(os.getenv("BEDROCK_TEMPERATURE", "0.2")),
        },
    }

    try:
        response = get_bedrock_client().invoke_model(
            modelId=model_id,
            body=json.dumps(request_body),
            contentType="application/json",
            accept="application/json",
        )
        response_body = json.loads(response["body"].read())
        corrected_text = extract_text_from_response(response_body)
    except (NoCredentialsError, PartialCredentialsError) as exc:
        logger.warning("AWS credentials are missing or incomplete: %s", exc)
        raise GrammarCorrectionError(
            "AWS credentials were not found. Configure the AWS CLI or environment variables."
        ) from exc
    except ClientError as exc:
        logger.exception("Amazon Bedrock returned an error")
        message = exc.response.get("Error", {}).get("Message", "Amazon Bedrock request failed.")
        raise GrammarCorrectionError(f"Amazon Bedrock error: {message}") from exc
    except (BotoCoreError, KeyError, json.JSONDecodeError, TypeError) as exc:
        logger.exception("Unable to complete the Bedrock request")
        raise GrammarCorrectionError(
            "Could not correct the text right now. Please check your Bedrock configuration."
        ) from exc

    if not corrected_text:
        raise GrammarCorrectionError("Amazon Bedrock returned an empty response.")

    return corrected_text


def extract_text_from_response(response_body):
    """Extract generated text from the Amazon Nova InvokeModel response."""
    content_blocks = response_body.get("output", {}).get("message", {}).get("content", [])

    for block in content_blocks:
        if "text" in block:
            return block["text"].strip()

    return ""


# Elastic Beanstalk and Gunicorn can import "application" directly.
application = create_app()
app = application


if __name__ == "__main__":
    debug_enabled = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=debug_enabled)
