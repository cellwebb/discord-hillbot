import discord
import logging
import os
import time

from openai.error import APIError, RateLimitError, ServiceUnavailableError

from chat import get_channel_history, get_chatgpt_response, chunk_messages
from image import create_image, improve_image_prompt, save_image_from_url


DISCORD_CHARACTER_LIMIT = 2000

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'{time.strftime("%I:%M:%S %p")} - We have logged in as {client.user}')


@client.event
async def on_message(message):
    with open("discord.log", "a") as f:
        f.write(
            f'[{time.strftime("%I:%M:%S %p")}] | #{message.channel} | {message.author}: {message.content}\n'
        )

    if message.author == client.user:
        return

    if message.content.startswith("!davefacts"):
        with open("davefacts.txt", "a") as f:
            new_fact = message.content.replace("!davefacts", "").strip()
            f.write("- " + new_fact + "\n")
        await message.channel.send("Thanks for telling me more about Dave!")
        return

    if message.content.startswith("!image"):
        async with message.channel.typing():
            for n_attempts in range(1, 6):
                try:
                    print("calling openai api...")
                    prompt = message.content.replace("!image", "").strip()
                    prompt = improve_image_prompt(prompt)
                    image_url = create_image(prompt)
                    filename = save_image_from_url(image_url)
                    await message.channel.send(prompt, file=discord.File(filename))
                    with open("image_logs.txt", "a") as f:
                        f.write(
                            f'Datetime: {time.strftime("%Y-%m-%d %H:%M:%S")}, Prompt: {prompt}, Filename: {filename}\n'
                        )
                    return
                except (APIError, RateLimitError, ServiceUnavailableError) as err:
                    wait_period = 30 * n_attempts
                    await message.channel.send(f"{err} I'll try again in {wait_period} seconds!")
                    time.sleep(wait_period)
                except Exception as err:
                    await message.channel.send(err)
                    return

    if (
        "hillbot" in message.content.lower()
        or client.user.mentioned_in(message)
        or not message.guild
    ):
        async with message.channel.typing():
            with open("system.txt") as f:
                system_msg = f.read()
            with open("davefacts.txt") as f:
                davefacts = f.read()

            print("pulling channel history...")
            conversation_history = await get_channel_history(client, message.channel)

            messages = [{"role": "system", "content": system_msg + "\n" + davefacts}]
            messages.extend(conversation_history)
            messages[-1]["content"] = "Reply in Dave's voice. " + messages[-1]["content"]
            messages = chunk_messages(messages)

            for n_attempts in range(1, 6):
                try:
                    response = get_chatgpt_response(messages)
                    for i in range(0, len(response), DISCORD_CHARACTER_LIMIT):
                        await message.channel.send(response[i : i + DISCORD_CHARACTER_LIMIT])
                    return
                except (APIError, RateLimitError, ServiceUnavailableError) as err:
                    wait_period = 30 * n_attempts
                    await message.channel.send(f"{err} I'll try again in {wait_period} seconds!")
                    time.sleep(wait_period)
                except Exception as err:
                    await message.channel.send(err)
                    return
            await message.channel.send("The server is busy! Please try again later!")
            return


handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
token = os.getenv("DISCORD_HILLBOT_TOKEN")
client.run(token, log_handler=handler)
