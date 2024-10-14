import asyncio
import discord
import logging
import os
import random
import time
import yaml

from openai import AsyncOpenAI, APIError, RateLimitError

from chat import get_channel_history  # , get_chatgpt_response
from image import save_image_from_url


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
            await message.channel.send("Thanks for telling me more about Dave!")
            return

    if message.content.startswith("!image"):
        with open("prompt_enhancers.txt", "r") as f:
            prompt_enhancers = f.readlines()
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)

        for n_attempts in range(1, 6):
            async with message.channel.typing():
                try:
                    prompt = message.content.replace("!image", "").strip()
                    prompt = f"{prompt}, {random.choice(prompt_enhancers)}"

                    response = await openai_client.images.generate(
                        prompt=prompt, **config["image_model"]
                    )
                    image_url = response.data[0].url
                    filename = save_image_from_url(image_url)

                    await message.channel.send(prompt, file=discord.File(filename))

                    with open("image_logs.txt", "a") as f:
                        f.write(
                            f'Datetime: {time.strftime("%Y-%m-%d %H:%M:%S")}, Prompt: {prompt}, Filename: {filename}\n'  # noqa
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
                    response_text = response.choices[0].message.content

                    for i in range(0, len(response_text), DISCORD_CHARACTER_LIMIT):
                        await message.channel.send(response_text[i : i + DISCORD_CHARACTER_LIMIT])
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
