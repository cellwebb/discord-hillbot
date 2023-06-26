import openai
import os
import random


prompt_extensions = [
    'created by a talented human artist named Dave',
    'created by a deranged robot artist named Hillbot',
    'made of meat',
    'in the style of a biblical angel',
    'in the style of an unsettling image',
    'with fingers for hot dogs',
    'with hot dogs for fingers',
    'with birds secretly communicating with each other in code',
    'with random words from the dictionary',
    'where the moon is really just a giant disco ball in the sky'
]

def create_image(base_prompt: str = "cat") -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    prompt = " ".join([base_prompt] + random.sample(prompt_extensions, k=random.randint(1, len(prompt_extensions))))
    print(prompt)
    response = openai.Image.create(prompt=prompt, n=1, size="1024x1024")
    image_url = response['data'][0]['url']
    return image_url
