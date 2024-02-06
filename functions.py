# -*- coding: utf-8 -*-

# IMPORTS
from google.oauth2.credentials import Credentials
from datetime import datetime as date
from datetime import timedelta
from dotenv import load_dotenv
import pickle
import json
import os

load_dotenv()

# Returns the value of the file associated with the given name
def load_crypted(name):
    with open('DB/' + name + '.pkl', 'rb') as f:
        crypted = pickle.load(f)
        return decode_credentials(crypted)

# Returns the value of the file associated with the given name
def load(name):
    with open('DB/' + name + '.pkl', 'rb') as f:
        crypted = pickle.load(f)
        return decode(crypted)

# Returns the current date, with an offset if necessary (c.f. jetlag)
def getCurrentDate():
    offset = 0
    if "REPLIT" in os.environ:
        offset = 1
    return date.now() + timedelta(seconds=3600 * offset)

# Returns the same date with one years less
def getLastYear(date):
    d = list(str(date))
    d[3] = str(int(d[3]) - 1)
    newDate = ''.join(d)
    return newDate

def code(data):
    password = os.environ.get('HASH_PASSWORD')
    encoded_data = {}
    for key, value in data.items():
        encoded_value = ""
        for i in range(len(value)):
            d = value[i]
            p = password[i % len(password)]
            v = chr(ord(d) + ord(p))
            encoded_value += v

        encoded_data[key] = encoded_value

    return encoded_data

def decode(data):
    password = os.environ.get('HASH_PASSWORD')
    decoded_data = {}
    for key, value in data.items():
        decoded_value = ""
        for i in range(len(value)):
            d = value[i]
            p = password[i % len(password)]
            v = chr(ord(d) - ord(p))
            decoded_value += v

        decoded_data[key] = decoded_value

    return decoded_data


def code_credentials(credentials):
    password = os.environ.get('HASH_PASSWORD')
    serialized_credentials = credentials.to_json()
    credentials_dict = json.loads(serialized_credentials)
    credentials_dict["valid"] = credentials.valid
    credentials_dict["expired"] = credentials.expired
    updated_serialized_credentials = json.dumps(credentials_dict)
    encrypted_data = ""
    for i in range(len(updated_serialized_credentials)):
        d = updated_serialized_credentials[i]
        p = password[i % len(password)]
        v = chr(ord(d) + ord(p))
        encrypted_data += v

    return encrypted_data

def decode_credentials(encrypted_credentials):
    password = os.environ.get('HASH_PASSWORD')

    decrypted_data = ""
    for i in range(len(encrypted_credentials)):
        d = encrypted_credentials[i]
        p = password[i % len(password)]
        v = chr(ord(d) - ord(p))
        decrypted_data += v

    creds_dict = json.loads(decrypted_data)
    creds = Credentials.from_authorized_user_info(creds_dict)
    obj = {"credentials" : creds, "valid" : creds_dict["valid"], "expired" : creds_dict["expired"]}
    return obj
