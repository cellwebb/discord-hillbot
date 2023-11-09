import openai
import os
import random
import requests
import uuid


PROMPT_ENHANCERS = [
    "created by a talented human artist named Dave",
    "created by a talented robot artist named Hillbot",
    "photorealistic",
    "made of meat",
    "in the style of a biblical angel",
    "in the style of an unsettling image",
    "with fingers for hot dogs",
    "with hot dogs for fingers",
    "in the style of Jean-Michel Basquiat",
    "in the style of Pablo Picasso",
    "in the style of Salvador Dali",
    "ancient roman painting",
    "charcoal sketch",
    "etching",
    "political cartoon from US newspaper",
    "children's drawing",
    "scientific diagram",
    "screenshot from Final Fantasy 7",
    "in the style of Disney vintage animation",
    "field journal line art",
    "colored pencil, detailed",
    "aesthetic",
    "beautiful",
    "cinematic lighting",
    "cyberpunk",
    "fantasy",
    "futuristic",
    "masterpiece",
    "photorealistic",
    "psychedelic",
    "vaporwave",
    "LEGO",
]


def create_image(prompt: str = "cat") -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Image.create(
        prompt=prompt, n=1, size="1024x1024", model="dall-e-3"
    )
    image_url = response["data"][0]["url"]
    return image_url


def improve_image_prompt(base_prompt: str) -> str:
    prompt = f"{base_prompt}, {random.choice(PROMPT_ENHANCERS)}"
    return prompt


def save_image_from_url(image_url: str) -> str:
    response = requests.get(image_url)
    os.makedirs("images", exist_ok=True)
    filename = f"images/{str(uuid.uuid4().hex)}.png"
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename
