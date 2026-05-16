# AI Grammar Corrector

A beginner-friendly web application that corrects grammar with Python Flask and Amazon Bedrock. The user enters text in a simple webpage, Flask sends that text to the Amazon Bedrock Runtime API with `boto3`, and the corrected version is shown on the page.

## Features

- Python Flask backend
- HTML and CSS frontend with a responsive UI
- Amazon Bedrock Runtime integration through `boto3`
- Configurable AWS Region and Bedrock model ID
- Environment-variable based configuration
- Basic loading and error states
- Health check endpoint for deployment
- Ready for AWS Elastic Beanstalk with a `Procfile`

## Tech Stack

- Python 3.11+
- Flask
- boto3
- Amazon Bedrock Runtime Converse API
- HTML
- CSS
- Gunicorn for production serving

## Project Structure

```text
grammar-corrector/
|-- app.py
|-- requirements.txt
|-- README.md
|-- .gitignore
|-- .env.example
|-- Procfile
|-- templates/
|   `-- index.html
`-- static/
    `-- style.css
```

## AWS Bedrock Setup

1. Sign in to the AWS Console.
2. Open Amazon Bedrock.
3. Choose a Region where your preferred model is available, such as `us-east-1`.
4. Request model access for Amazon Nova Micro or the model you plan to use.
5. Make sure your IAM user or role can call Bedrock Runtime.

Minimum IAM permission for this app:

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

The default model is:

```text
amazon.nova-micro-v1:0
```

This project uses the Bedrock Runtime `Converse` API. You can use another Bedrock text/chat model that supports Converse by changing `BEDROCK_MODEL_ID`.

Helpful AWS docs:

- Bedrock Runtime `converse`: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime/client/converse.html
- Amazon Nova model parameters: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-nova.html
- Elastic Beanstalk Python platform: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-flask.html

## AWS CLI Configuration

Install the AWS CLI, then run:

```bash
aws configure
```

Enter:

- AWS Access Key ID
- AWS Secret Access Key
- Default region, for example `us-east-1`
- Default output format, for example `json`

You can test the configured identity with:

```bash
aws sts get-caller-identity
```

For production on Elastic Beanstalk, prefer an IAM instance profile or environment role instead of storing long-lived access keys.

For local development, `boto3` can read credentials from the AWS CLI profile, IAM role credentials, or environment variables such as `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN`.

## Local Installation

Download or clone this repository, then open the project folder in your terminal.

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Edit `.env` if you need a different AWS Region or Bedrock model:

```text
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-micro-v1:0
```

## Running Locally

Start the Flask app:

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

Enter text, submit it, and the corrected text will appear below the editor.

## Deploying to AWS Elastic Beanstalk

Install the Elastic Beanstalk CLI:

```bash
pip install awsebcli
```

Initialize Elastic Beanstalk:

```bash
eb init
```

Choose:

- The same AWS Region used for Bedrock
- Python as the platform
- Your preferred SSH option

Create an environment:

```bash
eb create grammar-corrector-env
```

Set environment variables:

```bash
eb setenv AWS_REGION=us-east-1 BEDROCK_MODEL_ID=amazon.nova-micro-v1:0 BEDROCK_MAX_TOKENS=1000 BEDROCK_TEMPERATURE=0.2 BEDROCK_READ_TIMEOUT=3600
```

Deploy:

```bash
eb deploy
```

Open the deployed app:

```bash
eb open
```

The included `Procfile` tells Elastic Beanstalk to run:

```text
gunicorn app:application
```

## Deployment Best Practices

- Use an Elastic Beanstalk instance profile with `bedrock:InvokeModel` permission.
- Keep secrets out of Git and store configuration in Elastic Beanstalk environment properties.
- Use the same Region for Elastic Beanstalk and Bedrock when possible.
- Confirm the Bedrock model is available and enabled in your deployment Region.
- Keep `.env` local only. It is already ignored by `.gitignore`.

## Future Enhancements

- Add copy-to-clipboard for corrected text
- Add tone options such as formal, casual, or concise
- Add user accounts and correction history
- Add automated tests
- Add request rate limiting for public deployments
