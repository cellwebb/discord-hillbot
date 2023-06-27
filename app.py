import discord
import logging
import os
import time

from openai.error import APIError, RateLimitError, ServiceUnavailableError

from chat import (
    get_discord_conversation_history,
    chunk_long_messages,
    reply_with_chatgpt
)
from image import improve_image_prompt, create_image, save_image_from_url
from config import channel_history_limit, max_openai_api_attempts


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{time.strftime("%I:%M:%S %p")} - We have logged in as {client.user}')

@client.event
async def on_message(message):
    print(f'[{time.strftime("%I:%M:%S %p")}] | #{message.channel} | {message.author}: {message.content}')

    if message.author == client.user:
        return

    if message.content.startswith('!davefacts'):
        with open('davefacts.txt', 'a') as f:
            new_fact = message.content.replace('!davefacts', '').strip()
            f.write('- ' + new_fact + '\n')
        await message.channel.send('Thanks for telling me more about Dave!')
        return

    if message.content.startswith('!image'):
        async with message.channel.typing():
            for n_attempts in range(1, max_openai_api_attempts):
                try:
                    print('calling openai api...')
                    prompt = message.content.replace('!image', '').strip()
                    prompt = improve_image_prompt(prompt)
                    image_url = create_image(prompt)
                    filename = save_image_from_url(image_url)
                    await message.channel.send(prompt, file=discord.File(filename))
                    with open('image_logs.txt', 'a') as f:
                        f.write(f'Datetime: {time.strftime("%Y-%m-%d %H:%M:%S")}, Prompt: {prompt}, Filename: {filename}\n')
                    return
                except (APIError, RateLimitError, ServiceUnavailableError) as err:
                    wait_period = 30 * n_attempts
                    await message.channel.send(f"{err} I'll try again in {wait_period} seconds!")
                    time.sleep(wait_period)
                except Exception as err:
                    await message.channel.send(err)
                    return

    if 'hillbot' in message.content.lower() or client.user.mentioned_in(message):
        async with message.channel.typing():
            with open('system.txt') as f:
                system_msg = f.read()
            with open('davefacts.txt') as f:
                davefacts = f.read()

            print('pulling conversation history...')
            conversation_history = await get_discord_conversation_history(
                client, message, channel_history_limit)

            print('chunking long messages...')
            chunk_long_messages(conversation_history)

            messages = [{"role": "system", "content": system_msg + '\n' + davefacts}]
            messages.extend(conversation_history)
            messages[-1]["content"] = "Reply in Dave's voice. " + messages[-1]["content"]

            print(messages)
            print('calling openai api...')
            for n_attempts in range(1, max_openai_api_attempts):
                try:
                    await reply_with_chatgpt(message, messages)
                except (APIError, RateLimitError, ServiceUnavailableError) as err:
                    wait_period = 30 * n_attempts
                    await message.channel.send(f"{err} I'll try again in {wait_period} seconds!")
                    time.sleep(wait_period)
                except Exception as err:
                    await message.channel.send(err)
                    return
            else:
                response = "The server is busy! Please try again later!"
            await message.channel.send(response)


handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
token = os.getenv("DISCORD_HILLBOT_TOKEN")
client.run(token, log_handler=handler)
