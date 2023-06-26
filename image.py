import openai
import os
import random
import requests
import uuid


def create_image(prompt: str = "cat") -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    image_url = response['data'][0]['url']
    return image_url


def improve_image_prompt(base_prompt: str) -> str:
    from config import prompt_extensions
    prompt = base_prompt + " " \
        + " ".join(random.sample(prompt_extensions, k=random.randint(1, 4))) \
        + " beautiful art"
    return prompt


def save_image_from_url(image_url: str) -> str:
    response = requests.get(image_url)
    os.makedirs('images', exist_ok=True)
    filename = f'images/{str(uuid.uuid4().hex)}.png'
    with open(filename, 'wb') as f:
        f.write(response.content)
    return filename
