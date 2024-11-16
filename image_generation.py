import os
import uuid
import base64
import random
import yaml
import asyncio
import time
from datetime import datetime
from io import BytesIO

from PIL import Image
from openai import AsyncOpenAI, APIError, RateLimitError
import discord
import replicate
from dotenv import load_dotenv


load_dotenv()

openai_client = AsyncOpenAI()


async def generate_image(message: object) -> None:
    """Generate an image based on a prompt."""

    with open("resources/prompt_enhancers.txt", "r") as f:
        prompt_enhancers = f.readlines()
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    if message.content.strip().lower().startswith("!image"):
        original_prompt = message.content.strip()[6:].strip()
    elif message.content.strip().lower().startswith("!img"):
        original_prompt = message.content.strip()[4:].strip()
    elif message.content.strip().lower().startswith("!i"):
        original_prompt = message.content.strip()[2:].strip()

    for n_attempts in range(1, 6):
        async with message.channel.typing():
            try:
                prompt = f"{original_prompt}, {random.choice(prompt_enhancers)}"[:-1]
                response = await openai_client.images.generate(
                    prompt=prompt, **config["image_model"]
                )

                filename = f"images/creations/{str(uuid.uuid4().hex)}.png"
                with open(filename, "wb") as f:
                    f.write(base64.standard_b64decode(response.data[0].b64_json))

                await message.channel.send(prompt, file=discord.File(filename))

                with open("images/image_logs.txt", "a") as f:
                    f.write(
                        f'Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}, '
                        f"Prompt: {prompt}, Filename: {filename}, "
                        f"Revised Prompt:{response.data[0].revised_prompt}\n"
                    )
                return

            except RateLimitError as err:
                wait_period = 10 * n_attempts
                await message.channel.send(f"{err}\nTrying again in {wait_period} seconds!")
                await asyncio.sleep(wait_period)

            except APIError as err:
                await message.channel.send(f"{err}\nAttempted prompt: {prompt}\nTrying again...")

            except Exception as err:
                await message.channel.send(f"{err}\nAttempted prompt: {prompt}")
                return
    else:
        await message.channel.send("Please try again later!")

    return


async def create_variation(message: object, attachment: object, params: dict) -> None:
    """Create a variation of an image attachment."""

    await message.channel.send("Nice image! Let me redraw it for you!")

    with open("resources/prompt_enhancers.txt", "r") as f:
        prompt_enhancers = f.readlines()
    prompt = message.content.strip()
    # prompt = f"{prompt}, {random.choice(prompt_enhancers)}"[:-1]
    print(prompt)

    async with message.channel.typing():
        filetype = attachment.filename.split(".")[-1]
        os.makedirs("images/variations/originals", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        original_filepath = f"images/variations/originals/{timestamp}.{filetype}"
        await attachment.save(original_filepath)

        with Image.open(original_filepath) as img:
            buff = BytesIO()
            img.save(buff, format="PNG")
            img_str = base64.b64encode(buff.getvalue()).decode("utf-8")
            image = f"data:application/octet-stream;base64,{img_str}"

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
