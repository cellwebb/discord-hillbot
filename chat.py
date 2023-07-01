import openai
import os
import tiktoken

from config import CHANNEL_HISTORY_LIMIT, TEMPERATURE


def get_chatgpt_response(messages: list[dict[str]]) -> None:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=TEMPERATURE
    )
    response = chat_completion.choices[0].message.content
    return response


def chunk_messages(messages: list[dict[str]]) -> list[dict[str]]:
    """Splits long messages (2001+ tokens) in a conversation history to
    satisfy 'gpt-3.5-turbo' requirements."""
    i = 0
    while i < len(messages):
        if len(messages[i]["content"]) > 2000:
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            tokenized_content = encoding.encode(messages[i]["content"])
            num_tokens = len(tokenized_content)
            if num_tokens > 2000:
                messages[i]["content"] = ''.join(tokenized_content[:2000])
                messages.insert(
                    i + 1,
                    {"role": messages[i]["role"],
                    "content": tokenized_content[2000:]}
                )
        i += 1
    return messages

async def get_channel_history(client: object, channel: object) -> list[dict[str]]:
    """Asynchronously pulls messages from a channel and converts to format
    requirements of 'gpt-3.5-turbo'."""
    channel_history_generator = channel.history(limit=CHANNEL_HISTORY_LIMIT)
    channel_history = []
    async for prev_message in channel_history_generator:
        channel_history.append({
            "role": "assistant" if prev_message.author == client.user else "user",
            "content": prev_message.content
        })
    channel_history.reverse()

    return channel_history

