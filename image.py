import os
import requests
import uuid


def save_image_from_url(image_url: str) -> str:
    response = requests.get(image_url)
    os.makedirs("images", exist_ok=True)
    filename = f"images/{str(uuid.uuid4().hex)}.png"
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename
