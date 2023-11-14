import base64
import uuid
import hashlib
from django.conf import settings


def encode_unique_link(data):
    # Get the secret key from Django settings
    secret_key = settings.SECRET_KEY

    # Convert data to bytes
    data_bytes = str(data).encode()

    # Create an HMAC using the secret key
    verification_key = base64.urlsafe_b64encode(secret_key.encode())
    hmac = hashlib.blake2b(salt=verification_key, digest_size=32)
    hmac.update(data_bytes)
    encoded_hmac = hmac.hexdigest()

    # Concatenate the data and HMAC and encode them together
    concatenated_data = data_bytes + encoded_hmac.encode()
    encoded_link = base64.urlsafe_b64encode(concatenated_data).decode().rstrip('=')

    return encoded_link
