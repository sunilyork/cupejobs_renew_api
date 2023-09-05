import datetime
import json

import requests
from bson import ObjectId
from cryptography.fernet import Fernet

from apps.config import get_settings
from apps.lib.decorators import timer

Settings = get_settings()


def generate_key():
    """
    # Reference - https://milovantomasevic.com/blog/stackoverflow/2021-04-28-how-do-i-encrypt-and-decrypt-a-string-in-python/
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    with open(Settings.JWT_SECRET_KEY, "wb") as key_file:
        key_file.write(key)

    return key


def load_key():
    """
    Load the previously generated key
    """
    return open(Settings.JWT_SECRET_KEY, "rb").read()


def encrypt_message(message):
    """
    Encrypts a message
    """
    key = load_key()

    if not key:
        key = generate_key()

    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)

    return encrypted_message


def decrypt_message(encrypted_message):
    """
    Decrypts an encrypted message
    """
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)

    return decrypted_message.decode()


def user_dict(user) -> dict:
    SISID = ""
    if user.SISID:
        SISID = decrypt_message(str.encode(user.SISID))

    PAYNO = ""
    if user.PAYNO:
        PAYNO = decrypt_message(str.encode(user.PAYNO))

    return {
        "id": str(user.id),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "email": user.email,
        "cupe_unit": user.cupe_unit,
        "SISID": SISID,
        "PAYNO": PAYNO,
        "disabled": user.disabled,
    }


def defaultconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


class Serialize(object):
    @staticmethod
    def serialize(obj):
        def check(o):
            for k, v in o.__dict__.items():
                try:
                    _ = json.dumps(v)
                    o.__dict__[k] = v
                except TypeError:
                    o.__dict__[k] = str(v)
            return o

        return json.dumps(check(obj).__dict__, indent=2)


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid.")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# Reference:- https://www.geeksforgeeks.org/python-program-check-validity-password/
def is_valid_password(password: str):
    """
    Primary conditions for password validation:

    Minimum 8 and Maximum 12 characters.
    The alphabet must be between [a-z]
    At least one alphabet should be of Upper Case [A-Z]
    At least 1 number or digit between [0-9].
    At least 1 character from [*.!@#$%^&(){}[]:;<>,.?/\~_+-=|].
    """
    if not password or type(password) != str:
        return False

    num_of_lowercase_count = 0
    num_of_uppercase_count = 0
    num_of_specialchar_count = 0
    num_of_digits_count = 0
    capitalalphabets = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    smallalphabets = "abcdefghijklmnopqrstuvwxyz"
    specialchar = "*.!@#$%^&(){}[]:;<>,.?/\~_+-=|"
    digits = "0123456789"
    if len(password) >= 8 and len(password) <= 12:
        for i in password:
            # counting lowercase alphabets
            if i in smallalphabets:
                num_of_lowercase_count += 1

            # counting uppercase alphabets
            if i in capitalalphabets:
                num_of_uppercase_count += 1

            # counting digits
            if i in digits:
                num_of_digits_count += 1

            # counting the mentioned special characters
            if i in specialchar:
                num_of_specialchar_count += 1
    if (
        num_of_lowercase_count >= 1
        and num_of_uppercase_count >= 1
        and num_of_specialchar_count >= 1
        and num_of_digits_count >= 1
        and (
            num_of_lowercase_count
            + num_of_uppercase_count
            + num_of_digits_count
            + num_of_specialchar_count
            == len(password)
        )
    ):
        return True
    else:
        return False


@timer
def send_request(url):
    resp = requests.get(url)
    data = resp.json()
    return data
