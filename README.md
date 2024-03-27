# serverless

# Email Verification Function

This repository contains the code for a cloud-based function designed to send verification emails to users and track the email sending activity in a database. The function is triggered by messages published to a specific Pub/Sub topic, processes the message to extract user information, generates a unique verification token, inserts the token into a database, and sends an email to the user with a link to verify their account.

## Features

- Generates a unique verification token for each user.
- Stores the verification token and its expiration time in a MySQL database.
- Sends an email to the user with a link to verify their account.
- Tracks the email sending activity in a database.

## Requirements

- Google Cloud Functions
- Google Cloud Pub/Sub
- Google Cloud SQL (MySQL)
- Mailgun for email sending
- Python 3.8 or higher

## Environment Variables

To run this function, you will need to set the following environment variables:

- `DB_NAME`: The name of your MySQL database.
- `DB_USER`: The username for your MySQL database.
- `DB_PASS`: The password for your MySQL database user.
- `DB_HOST`: The hostname or IP address of your MySQL database server.
- `MAILGUN_API_KEY`: Your Mailgun API key for sending emails.
- `DOMAIN_NAME`: The domain name to be used in the verification link.
- `EXPIRE_MIN`: The expiration time for the verification token, in minutes.

## Setup and Deployment

1. **Database Setup**: Ensure your MySQL database is set up with the required tables for storing verification tokens and email tracking information.

2. **Pub/Sub Topic**: Create a Google Cloud Pub/Sub topic that will trigger the function. Note the topic ID.

3. **Mailgun Configuration**: Set up your Mailgun account and note your API key and domain.

4. **Deploy Function**: Deploy this function to Google Cloud Functions, ensuring that you set the environment variables as described above.

   Example deployment command:

   ```bash
   gcloud functions deploy my-cloud-function \
     --runtime python39 \
     --trigger-topic verify-email-topic \
     --set-env-vars DB_NAME=<your-db-name>,DB_USER=<your-db-user>,...
