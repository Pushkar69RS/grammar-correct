# AI Grammar Corrector

This is a university project web application that uses **Python Flask** and **Amazon Bedrock** to correct grammar in user-provided text. The main idea is simple: a user enters a sentence or paragraph, the Flask backend sends it to a Bedrock language model, and the corrected version is displayed back on the same page.

The project is intentionally kept small so the architecture is easy to understand, explain, and extend. It shows how a basic web application can connect a frontend form, a backend route, cloud-based AI inference, and deployment configuration.

## Project Objectives

- Build a working grammar correction tool using a web interface.
- Learn how Flask handles routes, forms, templates, and configuration.
- Integrate an AI model through Amazon Bedrock Runtime.
- Keep AWS credentials and model settings outside the source code.
- Prepare the application for local development and cloud deployment.

## High-Level Architecture

```text
User Browser
    |
    | 1. User submits text through the HTML form
    v
Flask Web Server
    |
    | 2. Validates input and prepares the prompt
    v
Amazon Bedrock Runtime
    |
    | 3. Model returns corrected text
    v
Flask Web Server
    |
    | 4. Renders the result in the template
    v
User Browser
```

The application follows a simple server-rendered architecture. The frontend does not call Bedrock directly. Instead, all AI requests go through Flask, which keeps the Bedrock integration and AWS configuration on the server side.

## Architecture Components

### 1. Presentation Layer

Files:

- `templates/index.html`
- `static/style.css`

This layer contains the user interface. The page has a textarea for input, a submit button, error display, and a result section. The JavaScript in the template only handles the loading state of the button after submission.

### 2. Application Layer

File:

- `app.py`

This is the main Flask application. It is responsible for:

- Creating the Flask app with `create_app()`
- Handling `GET` and `POST` requests on `/`
- Validating empty input and maximum input length
- Calling the grammar correction function
- Rendering corrected text or error messages
- Providing a `/health` endpoint for deployment checks

### 3. AI Service Layer

File:

- `app.py`

The Bedrock integration is also placed in `app.py` because this project is small. The important functions are:

- `get_bedrock_client()` creates a cached Bedrock Runtime client.
- `correct_grammar(text)` sends the prompt and user text to Amazon Bedrock.
- `extract_text_from_response(response_body)` reads the generated text from the Bedrock Converse API response.

The Bedrock client is cached with `lru_cache(maxsize=1)` so the application does not recreate the AWS client on every request.

### 4. Configuration Layer

Files:

- `.env.example`
- Environment variables

The application uses environment variables for configuration. This makes the same code work locally and in deployment.

Main configuration values:

```text
AWS_REGION=us-east-1
AWS_DEFAULT_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-micro-v1:0
BEDROCK_MAX_TOKENS=1000
BEDROCK_TEMPERATURE=0.2
BEDROCK_READ_TIMEOUT=3600
MAX_INPUT_CHARS=5000
```

### 5. Deployment Layer

Files:

- `Procfile`
- `requirements.txt`

The `Procfile` is included for AWS Elastic Beanstalk or similar platforms. It starts the app with Gunicorn:

```text
web: gunicorn app:application
```

## Request Flow

1. The user opens the home page.
2. Flask renders `templates/index.html`.
3. The user enters text and submits the form.
4. The `/` route receives the `POST` request.
5. Flask checks whether the text is empty or too long.
6. If the input is valid, Flask calls `correct_grammar()`.
7. `correct_grammar()` sends the request to Amazon Bedrock using `boto3`.
8. Bedrock returns a response from the selected model.
9. The app extracts the corrected text.
10. Flask renders the same page again with the corrected result.

## Project Structure

```text
grammar-correct/
|-- app.py
|-- requirements.txt
|-- README.md
|-- .env.example
|-- .gitignore
|-- Procfile
|-- templates/
|   `-- index.html
`-- static/
    `-- style.css
```

## Main Files Explained

| File | Purpose |
| --- | --- |
| `app.py` | Main Flask app, route handling, input validation, Bedrock API call, and health endpoint |
| `templates/index.html` | HTML page rendered by Flask |
| `static/style.css` | Styling for the web interface |
| `.env.example` | Example environment configuration for local setup |
| `requirements.txt` | Python dependencies |
| `Procfile` | Production start command for Gunicorn |

## Tech Stack

- Python 3.11+
- Flask
- boto3
- Amazon Bedrock Runtime Converse API
- HTML
- CSS
- Gunicorn
- python-dotenv for local environment variables

## AWS Bedrock Setup

1. Sign in to the AWS Console.
2. Open Amazon Bedrock.
3. Choose a Region where your selected model is available, for example `us-east-1`.
4. Request access to Amazon Nova Micro or another Bedrock model that supports the Converse API.
5. Make sure the IAM user, role, or instance profile can invoke Bedrock models.

Minimum IAM permission used for this project:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "bedrock:InvokeModel",
      "Resource": "*"
    }
  ]
}
```

Default model:

```text
amazon.nova-micro-v1:0
```

This can be changed by setting `BEDROCK_MODEL_ID`.

Helpful references:

- Bedrock Runtime Converse API: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/converse.html
- Amazon Nova model parameters: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-nova.html
- Elastic Beanstalk Python platform: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html

## Local Installation

Clone or download the repository, then open the project folder in a terminal.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file:

```powershell
Copy-Item .env.example .env
```

On macOS or Linux:

```bash
cp .env.example .env
```

Configure AWS credentials using the AWS CLI:

```bash
aws configure
```

You can test the configured identity with:

```bash
aws sts get-caller-identity
```

## Running the Application

Start the Flask app:

```bash
python app.py
```

Open this URL in the browser:

```text
http://127.0.0.1:5000
```

Enter text in the textarea and submit it. If AWS credentials, model access, and Region are configured correctly, the corrected text will appear in the result area.

## Deployment Notes

The project includes a `Procfile` for running the application with Gunicorn:

```text
web: gunicorn app:application
```

For AWS Elastic Beanstalk, a typical flow is:

```bash
pip install awsebcli
eb init
eb create grammar-corrector-env
eb setenv AWS_REGION=us-east-1 BEDROCK_MODEL_ID=amazon.nova-micro-v1:0 BEDROCK_MAX_TOKENS=1000 BEDROCK_TEMPERATURE=0.2 BEDROCK_READ_TIMEOUT=3600
eb deploy
eb open
```

For deployment, it is better to use an IAM role or instance profile instead of storing access keys in environment variables.

## Error Handling

The app handles a few common problems:

- Empty text input
- Text that exceeds the maximum character limit
- Missing or incomplete AWS credentials
- Bedrock API errors
- Empty responses from the model

Errors are shown on the page instead of crashing the application.

## Current Limitations

- The app does not store correction history.
- There are no user accounts.
- There are no automated tests yet.
- The grammar prompt is fixed and does not provide tone options.
- Very large inputs are limited by `MAX_INPUT_CHARS`.
- The frontend is server-rendered, so every correction reloads the page.

## Future Improvements

- Add copy-to-clipboard for corrected text.
- Add correction history for a session.
- Add tone options such as formal, casual, academic, or concise.
- Add automated tests for validation and response parsing.
- Add request rate limiting for public deployments.
- Move Bedrock-related logic into a separate service module if the project grows.

## Learning Outcome

This project helped demonstrate how a basic AI-powered web application is structured. The most important part architecturally is the separation between the browser, Flask route handling, configuration, and the external Bedrock service. Even though the codebase is small, it follows a pattern that can be expanded into a larger application later.
