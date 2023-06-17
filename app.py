import os
import logging

import discord
import openai


handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

token = os.getenv("DISCORD_HILLBOT_TOKEN")
openai.api_key=os.getenv("OPENAI_API_KEY")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}')

    if message.author == client.user:
        return

    if message.content.lower().startswith('!davefacts'):

        with open('davefacts.txt', 'a') as f:
            new_fact = message.content[10:].strip()
            if not new_fact.endswith('.'):
                new_fact += '.'
            f.write('- ' + new_fact + '\n')

        await message.channel.send('Thanks for telling me more about Dave!')

        return

    if 'hillbot' in message.content.lower() \
        or '<@1119312653765050429>' in message.content \
        or client.user.mentioned_in(message):

        with open('system.txt') as f:
            system_msg = f.read()

        with open('davefacts.txt') as f:
            davefacts = f.read()

        print('calling openai api...')
        chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_msg + '\n' + davefacts},
                       {"role": "user", "content": message.content}],
            temperature=1.2
        )
        response = chat_completion.choices[0].message.content
        print(response)
        await message.channel.send(response)

client.run(token, log_handler=handler)
