
""" author: feezyhendrix

    this module contains followers generation
 """

import random
import mechanicalsoup
import string
import logging

from .config import Config
from .getIdentity import getRandomIdentity

import requests
import time

# API Endpoint for Temp Mail
TEMP_MAIL_API = "https://api.tempmail.lol"
email_var =""


#generating a username
def username(identity):
    n = str(random.randint(1,99))
    name = str(identity).lower().replace(" ","")
    username = name + n
    logging.info("Username: {}".format(username))
    return(username)


#generate password
def generatePassword():
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for i in range(12))


def genEmail(username) :
    return ''.join(username + "@" + str(Config["email_domain"]))


def new_account():
    account_info = {}
    identity, gender, birthday = getRandomIdentity(country=Config["country"])
    account_info["name"] = identity
    account_info["username"] = username(account_info["name"])
    account_info["password"] = generatePassword()
    account_info["email"],account_info["token"] = generate_temporary_email()
    account_info["gender"] = gender
    account_info["birthday"] = birthday
    return(account_info)

# Step 1: Generate a temporary email
def generate_temporary_email():
    response = requests.post(f"{TEMP_MAIL_API}/v2/inbox/create")
    if response.status_code == 200 or response.status_code == 201:
        email_data = response.json()
        print(email_data)
        email_address = email_data['address']
        print(f"Temporary email address: {email_address}")
        email_var = email_address
        return email_address, email_data['token']
    else:
        print("Error generating temporary email.")
        return None, None

# Step 2: Poll the inbox for the verification email
def check_inbox(token):
    print(f"{token}")
    inbox_url = f"{TEMP_MAIL_API}/v2/inbox/?token={token}"

    while True:

        # Send token in JSON format
        time.sleep(3)
        response = requests.get(inbox_url)
        if response.status_code == 200 or response.status_code == 201:
            emails = response.json()["emails"]
            if emails and len(emails) > 0:
                print("Email received!")
                print(emails)
                return emails[0]['from'], emails[0]['subject'], emails[0]['html']
            else:
                print("No email received yet, retrying in 10 seconds...")
                time.sleep(10)
        else:
            print("Error fetching inbox.")
            return None

# Step 3: Extract the verification code from the email body
def extract_verification_code(email_body):
    # Assuming the verification code is a 6-digit number, adjust the regex as needed
    import re
    match = re.search(r'\b\d{6}\b', email_body)
    if match:
        return match.group(0)
    else:
        return None
