import os
import logging
import time

import discord
import openai
import tiktoken

from chat import get_discord_conversation_history, chunk_long_messages
from image import improve_image_prompt, create_image, save_image_from_url
from config import channel_history_limit


token = os.getenv("DISCORD_HILLBOT_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{time.strftime("%I:%M:%S %p")} - We have logged in as {client.user}')

@client.event
async def on_message(message):
    print(f'{time.strftime("%I:%M:%S %p")} - Message from {message.author} in #{message.channel}: {message.content}')

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
            from config import max_openai_api_attempts
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
                except (openai.error.APIError,
                        openai.error.RateLimitError,
                        openai.error.ServiceUnavailableError) as err:
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
            from config import max_openai_api_attempts, temperature
            for n_attempts in range(1, max_openai_api_attempts):
                try:
                    chat_completion = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        temperature=temperature
                    )
                    response = chat_completion.choices[0].message.content
                    break
                except (openai.error.RateLimitError, openai.error.ServiceUnavailableError) as err:
                    wait_period = 30 * n_attempts
                    await message.channel.send(f"{err} I'll try again in {wait_period} seconds!")
                    time.sleep(wait_period)
                except openai.error.APIError as err:
                    await message.channel.send(f"{err} I'll try re-connecting to the API!")
                    time.sleep(5)
                    openai.api_key = os.getenv("OPENAI_API_KEY")
                    time.sleep(5)
            else:
                response = "The server is busy! Please try again later!"
            await message.channel.send(response)


handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
client.run(token, log_handler=handler)
