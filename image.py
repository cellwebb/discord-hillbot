from openai import OpenAI
import os
import random
import requests
import uuid

openai_client = OpenAI()


def create_image(prompt: str, model: str, size: str) -> str:
    response = openai_client.images.generate(prompt=prompt, model=model, size=size)
    image_url = response.data[0].url
    return image_url


def improve_image_prompt(base_prompt: str) -> str:
    with open("./prompt_enhancers.txt", "r") as f:
        prompt_enhancers = f.read().splitlines()
    prompt = f"{base_prompt}, {random.choice(prompt_enhancers)}"
    return prompt


def save_image_from_url(image_url: str) -> str:
    response = requests.get(image_url)
    os.makedirs("images", exist_ok=True)
    filename = f"images/{str(uuid.uuid4().hex)}.png"
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename
