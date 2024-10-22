import asyncio
import base64
import discord
import logging
import os
import random
import time
import uuid
import yaml

from PIL import Image

from openai import AsyncOpenAI, APIError, RateLimitError

from chat import get_channel_history


DISCORD_CHARACTER_LIMIT = 2000

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
openai_client = AsyncOpenAI()


@client.event
async def on_ready():
    print(f'{time.strftime("%I:%M:%S %p")} - We have logged in as {client.user}')


@client.event
async def on_message(message):
    with open("discord.log", "a") as f:
        f.write(
            f'[{time.strftime("%I:%M:%S %p")}] | #{message.channel} | {message.author}: {message.content}\n'  # noqa
        )

    if message.author == client.user:
        return
    if message.mention_everyone:
        return

    if message.content.startswith("!davefacts"):
        async with message.channel.typing():
            new_fact = message.content.replace("!davefacts", "").strip()
            with open("davefacts.txt", "a") as f:
                f.write("- " + new_fact + "\n")
            await message.channel.send("Thanks for telling me more about Dave!")
            return

    if message.content.startswith("!prompt_enhancer"):
        async with message.channel.typing():
            new_prompt_enhancer = message.content.replace("!prompt_enhancer", "").strip()
            with open("prompt_enhancers.txt", "a") as f:
                f.write(new_prompt_enhancer + "\n")
            await message.channel.send("Thanks I've added it to the list!")
            return

    if message.content.startswith("!image"):
        with open("prompt_enhancers.txt", "r") as f:
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

                    filename = f"images/{str(uuid.uuid4().hex)}.png"
                    with open(filename, "wb") as f:
                        f.write(base64.standard_b64decode(response.data[0].b64_json))

                    await message.channel.send(prompt, file=discord.File(filename))

                    with open("image_logs.txt", "a") as f:
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
                    await message.channel.send(
                        f"{err}\nAttempted prompt: {prompt}\nTrying again..."
                    )

                except Exception as err:
                    await message.channel.send(f"{err}\nAttempted prompt: {prompt}")
                    return
        else:
            await message.channel.send("Please try again later!")
            return

    if message.channel.name == "hillbot-draws" and message.attachments:
        try:
            for attachment in message.attachments:
                if not attachment.content_type.startswith("image"):
                    continue

                await message.channel.send("Nice image! Let me redraw it for you!")

                async with message.channel.typing():

                    filetype = attachment.filename.split(".")[-1]
                    os.makedirs("images/variations/originals", exist_ok=True)
                    original_filename = (
                        f"images/variations/originals/{str(uuid.uuid4().hex)}.{filetype}"
                    )
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

                    with open("image_logs.txt", "a") as f:
                        f.write(
                            f'Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}, '
                            f"Variation of: {original_filename}, Filename: {variation_filename}\n"
                        )
        except Exception as err:
            await message.channel.send(err)
        return

    if message.channel.name == "hillbot-draws" and (
        message.content.lower().startswith("!again")
        or message.content.lower().startswith("again")
        or message.content.lower().startswith("more")
        or message.content.lower().startswith("deeper")
    ):
        await message.channel.send("Let's go deeper!")

        try:
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

        except Exception as err:
            await message.channel.send(err)
            return

        with open("image_logs.txt", "a") as f:
            f.write(
                f'Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}, '
                f"Variation of: {most_recent_variation}, Filename: {variation_filename}\n"
            )
        return

    if (
        "hillbot" in message.content.lower()
        or client.user.mentioned_in(message)
        or not message.guild  # Direct message
    ):
        with open("system.txt", "r") as f:
            system_msg = f.read()
        with open("davefacts.txt", "r") as f:
            davefacts = f.read()
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)

        async with message.channel.typing():
            conversation_history = await get_channel_history(
                client, message.channel, **config["discord"]
            )

            messages = [{"role": "system", "content": system_msg + "\n" + davefacts}]
            messages.extend(conversation_history)
            messages.append(
                {
                    "role": "system",
                    "content": "REMEMBER YOU'RE ON A DISCORD SERVER! REMEMBER TO KEEP YOUR MESSAGES GOOFY BUT DON'T RAMBLE! REMEMBER TO REPLY LIKE DAVE WOULD! REMEMBER YOUR DAVEFACTS! REMEMBER TO BE DAVE! 🌟",  # noqa
                }
            )

            for n_attempts in range(1, 6):
                try:
                    response = await openai_client.chat.completions.create(
                        messages=messages, **config["llm"]
                    )
                    reply = response.choices[0].message.content

                    for i in range(0, len(reply), DISCORD_CHARACTER_LIMIT):
                        await message.channel.send(reply[i : i + DISCORD_CHARACTER_LIMIT])
                    return

                except RateLimitError as err:
                    wait_period = 10 * n_attempts
                    await message.channel.send(f"{err}\nI'll try again in {wait_period} seconds!")
                    await asyncio.sleep(wait_period)

                except APIError as err:
                    await message.channel.send(f"{err}\n Trying again...")

                except Exception as err:
                    await message.channel.send(err)
                    return
            else:
                await message.channel.send("Please try again later!")
                return


handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
token = os.getenv("DISCORD_HILLBOT_TOKEN")
client.run(token, log_handler=handler)
