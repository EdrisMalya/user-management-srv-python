import random
import string
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

from app.core.config import settings


# Python program to check validation of password
# Module of regular expression is used with search()
def check_password_policy(password: str) -> bool:
    l, u, p, d = 0, 0, 0, 0
    capitalAlphabets = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    smallAlphabets = "abcdefghijklmnopqrstuvwxyz"
    specialCharacters = "$@_"
    digits = "0123456789"
    if len(password) >= 8:
        for i in password:
            # counting lowercase alphabets
            if i in smallAlphabets:
                l += 1
            # counting uppercase alphates
            if i in capitalAlphabets:
                u += 1
            # counting digits
            if i in digits:
                d += 1
            # counting the mentioned special characters
            if i in specialCharacters:
                p += 1
    if l >= 1 and u >= 1 and p >= 1 and d >= 1 and l + p + u + d == len(password):
        return True
    else:
        return False


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
        return decoded_token["sub"]
    except jwt.JWTError:
        return None


def generate_random_password():
    ## characters to generate password from
    characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")

    ## length of password from the user
    length = 5

    ## shuffling the characters
    random.shuffle(characters)

    ## picking random characters from the list
    password = []
    for i in range(length):
        password.append(random.choice(characters))

    ## shuffling the resultant password
    random.shuffle(password)

    ## converting the list to string
    ## printing the list
    return "".join(password)


def convertTupleToDictionary(t, d):
    for a, b in t:
        a = eval(str(a).replace("b", ""))
        b = eval(str(b).replace("b", ""))
        d.setdefault(a, []).append(b)
    return d
