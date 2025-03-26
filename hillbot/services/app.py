import asyncio
import os
import time

import discord
from openai import APIError, AsyncOpenAI, RateLimitError

from hillbot.core.config import config
from hillbot.services.image_generation import create_variation, generate_image, go_deeper
from hillbot.utils.utils import (
    add_dave_fact,
    add_prompt_enhancer,
    get_channel_history,
    message_contains_image,
)

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

    if message.content.startswith("!davefacts"):
        add_dave_fact(message)
        return
    if message.content.startswith("!prompt_enhancer"):
        add_prompt_enhancer(message)
        return
    if message.content.lower().startswith("!i"):
        await generate_image(message)
        return

    if message.author == client.user:
        return
    if message.mention_everyone:
        return

    if (
        hasattr(message.channel, "name")
        and message.channel.name == "hillbot-draws"
        and message_contains_image(message)
    ):
        try:
            for attachment in message.attachments:
                if attachment.content_type.startswith("image"):
                    await create_variation(message, attachment, config.get_variation_config())
        except Exception as err:
            await message.channel.send(err)
        return

    if (
        hasattr(message.channel, "name")
        and message.channel.name == "hillbot-draws"
        and (
            message.content.lower().startswith("!again")
            or message.content.lower().startswith("again")
            or message.content.lower().startswith("more")
            or message.content.lower().startswith("deeper")
        )
    ):
        try:
            await go_deeper(message)
        except Exception as err:
            await message.channel.send(err)
        return

    if (
        "hillbot" in message.content.lower()
        or client.user.mentioned_in(message)
        or not message.guild  # Direct message
    ):
        with open("resources/system.txt", "r") as f:
            system_msg = f.read()
        with open("resources/davefacts.txt", "r") as f:
            davefacts = f.read()

        async with message.channel.typing():
            conversation_history = await get_channel_history(
                client, message.channel, **config.get_discord_config()
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
                        messages=messages, **config.get_llm_config()
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


# handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
token = os.getenv("DISCORD_HILLBOT_TOKEN")
client.run(token)  # , log_handler=handler)
