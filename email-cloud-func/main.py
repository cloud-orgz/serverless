import base64
import os
import requests
import functions_framework
import json
import pymysql
import pymysql.cursors
from datetime import datetime, timedelta
import uuid

def generate_random_id():
    # Generate a random UUID
    random_id = uuid.uuid4()
    return str(random_id)

def insert_verification_token(user_id):
    # Initialize the token variable
    token = None

    # Convert string UUID to a binary format
    user_id_bin = uuid.UUID(user_id).bytes

    # Connect to the database
    conn = pymysql.connect(
        db=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASS'],
        host=os.environ['DB_HOST'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    with conn.cursor() as cur:
        try:
            # Generate a new UUID for the token and convert it to a binary format
            token_id_bin = generate_random_id()
            token = uuid.uuid4().hex
            expiry_date = datetime.now() + timedelta(minutes=2)

            # Insert the new verification token into the database
            cur.execute("""
                INSERT INTO verification_tokens (id, token, user_id, expiry_date)
                VALUES (%s, %s, %s, %s)
            """, (token_id_bin, token, user_id_bin, expiry_date))

            # Commit the transaction
            conn.commit()
            print(f"Inserted verification token {token} for user {user_id}")

        except Exception as e:
            # Rollback the transaction in case of error
            conn.rollback()
            print(f"Error inserting verification token: {e}")
            token = None
        finally:
            cur.close()
            conn.close()

    return token

@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    # Decode the base64-encoded data from Pub/Sub
    message_data = base64.b64decode(cloud_event.data["message"]["data"]).decode('utf-8')
    print(f"Received message: {message_data}")

    # Convert the JSON string into a Python dictionary
    message_dict = json.loads(message_data)

    # Extract the user ID from the message
    user_id = message_dict.get('id')

    # Insert verification token and receive the generated token
    token = insert_verification_token(user_id)
    domain_name = os.environ.get('DOMAIN_NAME')
    # Generate the verification link using the generated token
    verification_link = f"http://mukulsaipendem.me:8080/v1/user/verify?token={token}"  # Use the actual token

    email = message_dict.get('username')
    username = message_dict.get('firstName', 'User')  # Default to 'User' if not provided

    # Mailgun API URL
    mailgun_api_url = f"https://api.mailgun.net/v3/mail.mukulsaipendem.me/messages"
    # Email content
    subject = "Please Verify Your Email Address"
    html_content = f"""
    <html>
        <body>
            <p>Hi {username},</p>
            <p>Please verify your email address by clicking on the link below:</p>
            <a href="{verification_link}">Verify Email</a>
            <p>If you did not request this, please ignore this email.</p>
        </body>
    </html>
    """

    # Send the email using Mailgun
    response = requests.post(
        mailgun_api_url,
        auth=("api", os.environ.get('MAILGUN_API_KEY')),  # Use environment variable for API key
        data={
            "from": "Webapp <noreply@mail.mukulsaipendem.me>",
            "to": email,
            "subject": subject,
            "html": html_content
        }
    )

    # Check the response from Mailgun
    if response.status_code == 200:
        print("Email sent successfully")
    else:
        print(f"Failed to send email, status code: {response.status_code}, response text: {response.text}")
