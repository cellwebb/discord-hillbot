import os
import uuid
import base64
import random
import yaml
from PIL import Image
from openai import AsyncOpenAI, APIError, RateLimitError
import discord
import asyncio
import time

openai_client = AsyncOpenAI()


async def generate_image(message: object) -> None:
    with open("resources/prompt_enhancers.txt", "r") as f:
        prompt_enhancers = f.readlines()
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    original_prompt = message.content.replace("!image", "").strip()

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


async def create_variation(message: object, attachment: object) -> None:
    await message.channel.send("Nice image! Let me redraw it for you!")

    async with message.channel.typing():
        filetype = attachment.filename.split(".")[-1]
        os.makedirs("images/variations/originals", exist_ok=True)
        original_filename = f"images/variations/originals/{str(uuid.uuid4().hex)}.{filetype}"
        await attachment.save(original_filename)

        with Image.open(original_filename) as img:
            img.thumbnail((1024, 1024))
            converted_filename = original_filename.replace(filetype, "png")
            img.save(converted_filename)

        response = await openai_client.images.create_variation(
            image=open(converted_filename, "rb"), response_format="b64_json"
        )

        variation_filename = f"images/variations/{str(uuid.uuid4().hex)}.png"
        with open(variation_filename, "wb") as f:
            f.write(base64.standard_b64decode(response.data[0].b64_json))

    await message.channel.send(":D", file=discord.File(variation_filename))

    with open("images/image_logs.txt", "a") as f:
        f.write(
            f'Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}, '
            f"Variation of: {original_filename}, Filename: {variation_filename}\n"
        )

    return


async def go_deeper(message: object) -> None:
    await message.channel.send("Let's go deeper!")

    files = os.listdir("images/variations")
    files.sort(key=lambda x: os.path.getmtime(f"images/variations/{x}"))
    most_recent_variation = files[-1]

    async with message.channel.typing():
        response = await openai_client.images.create_variation(
            image=open(f"images/variations/{most_recent_variation}", "rb"),
            response_format="b64_json",
        )

        variation_filename = f"images/variations/{str(uuid.uuid4().hex)}.png"
        with open(variation_filename, "wb") as f:
            f.write(base64.standard_b64decode(response.data[0].b64_json))

        await message.channel.send(":D", file=discord.File(variation_filename))

    with open("images/image_logs.txt", "a") as f:
        f.write(
            f'Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}, '
            f"Variation of: {most_recent_variation}, Filename: {variation_filename}\n"
        )

    return
