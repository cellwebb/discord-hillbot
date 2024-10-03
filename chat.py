from openai import OpenAI

from config import CHANNEL_HISTORY_LIMIT, CHAT_MODEL, TEMPERATURE

openai_client = OpenAI()


def get_chatgpt_response(messages: list[dict[str]]) -> str:
    chat_completion = openai_client.chat.completions.create(
        model=CHAT_MODEL, messages=messages, temperature=TEMPERATURE
    )
    response = chat_completion.choices[0].message.content
    return response


async def get_channel_history(client: object, channel: object) -> list[dict[str]]:
    """Pulls messages from discord channel and formats for OpenAI API."""
    channel_history_generator = channel.history(limit=CHANNEL_HISTORY_LIMIT)

    channel_history = []
    async for message in channel_history_generator:
        channel_history.append(
            {
                "role": "assistant" if message.author == client.user else "user",
                "name": message.author.name.replace(".", "-"),
                "content": message.content,
            }
        )

    channel_history.reverse()  # Reverse to put messages in chronological order

    return channel_history
