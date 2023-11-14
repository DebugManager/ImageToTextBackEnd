import base64
import hashlib
import hmac
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
import binascii


def encode_unique_link(data):
    # Generate a UUID for the data
    unique_id = str(uuid.uuid4())

    # Get the secret key from Django settings
    secret_key = settings.SECRET_KEY

    # Convert data and UUID to bytes
    data_bytes = str(data).encode()
    unique_id_bytes = unique_id.encode()

    # Truncate the salt if it exceeds 16 bytes
    truncated_salt = secret_key.encode()[:16]

    # Create an HMAC using the truncated salt
    hmac = hashlib.blake2b(salt=truncated_salt, digest_size=32)
    hmac.update(data_bytes + unique_id_bytes)
    encoded_hmac = hmac.hexdigest()

    # Concatenate the data, UUID, and HMAC and encode them together
    concatenated_data = data_bytes + unique_id_bytes + encoded_hmac.encode()
    encoded_link = base64.urlsafe_b64encode(concatenated_data).decode().rstrip('=')

    return encoded_link


def decode_unique_link(encoded_link):
    try:
        # Decode the base64-encoded link
        decoded_data = base64.urlsafe_b64decode(encoded_link + '=' * (4 - len(encoded_link) % 4))

        # Split the decoded data into the original data and HMAC
        data_bytes = decoded_data[:-32]
        encoded_hmac = decoded_data[-32:]

        # Verify the HMAC using the secret key
        secret_key = settings.SECRET_KEY[:5]
        verification_key = base64.urlsafe_b64encode(secret_key.encode())
        hmac_instance = hmac.new(verification_key, msg=data_bytes, digestmod=hashlib.sha256)
        computed_hmac = hmac_instance.digest()

        # Constant-time comparison to prevent timing attacks
        if not constant_time_compare(computed_hmac, encoded_hmac):
            raise ValidationError("Invalid HMAC in the encoded link")

        # Return the original data as a string
        return data_bytes.decode()

    except (TypeError, binascii.Error, ValidationError) as e:
        raise ValidationError("Invalid encoded link") from e


def constant_time_compare(val1, val2):
    """
    Compare two values in constant time to prevent timing attacks.
    """
    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in zip(val1, val2):
        result |= x ^ y
    return result == 0
