import openai
import os
import random

openai.api_key = os.getenv("OPENAI_API_KEY")

prompt_extensions = [
    'created by a schizophrenic robot artist named Dave',
    'created by a schizophrenic robot artist named Hillbot',
    'made of meat',
    'in the style of a biblical angel',
    'in the style of an unsettling image',
    'with fingers for hot dogs',
    'with hot dogs for fingers',
    
    # hillbot's own suggestions
    "The moon is really just a giant disco ball in the sky",
    "Did you know that the word 'gullible' isn't actually in the dictionary? Go ahead, check for yourself!",
    "Do you ever wonder if birds are secretly communicating with each other in code?",
    "If you stare at a cloud long enough, it starts to look like a giant marshmallow.",
    "Did you know that the odds of getting struck by lightning are higher than the odds of winning the lottery? Better stay inside next time it rains!",
]

def create_image(base_prompt: str = "cat") -> str:
    prompt_extension = " ".join(random.choices(
        prompt_extensions, k=int(len(prompt_extensions)/3)))
    full_prompt = base_prompt + " " + prompt_extension
    print(full_prompt)
    response = openai.Image.create(prompt=full_prompt, n=1, size="1024x1024")
    image_url = response['data'][0]['url']
    return image_url
