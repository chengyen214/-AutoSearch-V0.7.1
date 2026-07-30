import hashlib


def generate_hash(title, content):

    text = (
        title +
        content
    )

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()