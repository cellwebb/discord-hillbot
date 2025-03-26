import asyncio
import base64
import os
import random
import time
import uuid
from datetime import datetime
from io import BytesIO

import discord
import replicate
from dotenv import load_dotenv
from openai import APIError, AsyncOpenAI, RateLimitError
from PIL import Image

from config import config

load_dotenv()

openai_client = AsyncOpenAI()


async def extract_prompt(
    message_content: str, prefixes: tuple = ("!image", "!img", "!i")
) -> str:
    """Extract the prompt from the message content."""
    content = message_content.strip().lower()
    original_prompt = ""

    for prefix in prefixes:
        if content.startswith(prefix):
            original_prompt = content[len(prefix) :].strip()
            break

    return original_prompt


async def create_image_from_prompt(prompt: str):
    """Create an image from a prompt using OpenAI API."""
    enhanced_prompt = await enhance_prompt(prompt)
    response = await openai_client.images.generate(
        prompt=enhanced_prompt, **config.get_image_config()
    )

    filename = f"images/creations/{str(uuid.uuid4().hex)}.png"
    with open(filename, "wb") as f:
        f.write(base64.standard_b64decode(response.data[0].b64_json))

    return filename, enhanced_prompt, response.data[0].revised_prompt


async def log_image_creation(prompt: str, filename: str, revised_prompt: str):
    """Log image creation details to a file."""
    with open("images/image_logs.txt", "a") as f:
        f.write(
            f'Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}, '
            f"Prompt: {prompt}, Filename: {filename}, "
            f"Revised Prompt:{revised_prompt}\n"
        )


async def generate_image(message: object) -> None:
    """Generate an image based on a prompt."""
    original_prompt = await extract_prompt(message.content)
    if not original_prompt:
        return

    await message.channel.typing()

    for n_attempts in range(1, 6):
        try:
            filename, enhanced_prompt, revised_prompt = await create_image_from_prompt(
                original_prompt
            )
            await message.channel.send(enhanced_prompt, file=discord.File(filename))
            await log_image_creation(enhanced_prompt, filename, revised_prompt)
            return

        except RateLimitError as err:
            wait_period = 10 * n_attempts
            await handle_error(message, err, original_prompt, True, wait_period)

        except APIError as err:
            await handle_error(message, err, original_prompt, True)

        except Exception as err:
            await handle_error(message, err, original_prompt)
            return
    else:
        await message.channel.send("Please try again later!")

    return


async def create_variation(message: object, attachment: object, params: dict) -> None:
    """Create a variation of an image attachment."""

    await message.channel.send("Nice image! Let me redraw it for you!")

    async with message.channel.typing():
        filetype = attachment.filename.split(".")[-1]
        os.makedirs("images/variations/originals", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        original_filepath = f"images/variations/originals/{timestamp}.{filetype}"
        await attachment.save(original_filepath)

        with Image.open(original_filepath) as img:
            with BytesIO() as buff:
                img.save(buff, format="PNG")
                img_str = base64.b64encode(buff.getvalue()).decode("utf-8")
                image = f"data:application/octet-stream;base64,{img_str}"

        prompt = await enhance_prompt(message.content.strip())
        print(prompt)

        for _ in range(3):
            response = await replicate.async_run(
                params["model"],
                input={
                    "image": image,
                    "prompt": prompt,
                    "cfg": params["cfg"],
                    "steps": params["steps"],
                    "prompt_strength": params["prompt_strength"],
                    # "disable_safety_checker": True,
                    # "apply_watermark": False,
                },
            )
            if response:
                break

        if not response:
            await message.channel.send("Sorry, I couldn't generate a variation.")
            await message.channel.send(f"Attempted prompt: {prompt}")
            await message.channel.send(f"Response: {response}")
            await message.channel.send(f"<||{params}||>")
            return

        if isinstance(response, list):
            response = response[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        variation_filepath = f"images/variations/{timestamp}.png"
        with open(variation_filepath, "wb") as f:
            f.write(response.read())

    await message.channel.send(f":D {prompt}", file=discord.File(variation_filepath))
    await message.channel.send(f"<||{params}||>")

    with open("images/image_logs.txt", "a") as f:
        f.write(
            f'Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}, '
            f"Variation of: {original_filepath}, Filename: {variation_filepath}, "
            f"Prompt: {prompt}\n"
        )

    return


async def go_deeper(message: object) -> None:
    """Create a variation of the most recent variation."""

    if message.content[-1].isdigit() and int(message.content[-1]) > 1:
        n = int(message.content[-1])
    else:
        n = 1

    for _ in range(n):
        await message.channel.send("Let's go deeper!")

        files = os.listdir("images/variations")
        files.sort(key=lambda x: os.path.getmtime(f"images/variations/{x}"))
        most_recent_variation = files[-1]

        async with message.channel.typing():
            prompt = await enhance_prompt(message.content.strip())
            print(prompt)

            response = await openai_client.images.create_variation(
                image=open(f"images/variations/{most_recent_variation}", "rb"),
                response_format="b64_json",
            )

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            variation_filepath = f"images/variations/{timestamp}.png"
            with open(variation_filepath, "wb") as f:
                f.write(base64.standard_b64decode(response.data[0].b64_json))

            await message.channel.send(":D", file=discord.File(variation_filepath))

        with open("images/image_logs.txt", "a") as f:
            f.write(
                f'Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}, '
                f"Variation of: {most_recent_variation}, Filename: {variation_filepath}\n"
            )

    return


async def enhance_prompt(original_prompt: str) -> str:
    """Enhance a prompt by adding a random prompt enhancer."""
    with open("resources/prompt_enhancers.txt", "r") as f:
        prompt_enhancers = f.readlines()
    prompt_enhancer = random.choice(prompt_enhancers).strip()
    return f"{original_prompt}, {prompt_enhancer}"


async def handle_error(
    message: object,
    error: Exception,
    prompt: str = "",
    retry: bool = False,
    wait_seconds: int = 0,
) -> None:
    """Handle errors with consistent messaging."""
    error_msg = f"{error}"
    if prompt:
        error_msg += f"\nAttempted prompt: {prompt}"

    if wait_seconds > 0:
        error_msg += f"\nTrying again in {wait_seconds} seconds!"
    elif retry:
        error_msg += "\nTrying again..."

    await message.channel.send(error_msg)

    if wait_seconds > 0:
        await asyncio.sleep(wait_seconds)
