from openai import OpenAI

openai_client = OpenAI()


def get_chatgpt_response(
    messages: list[dict[str]],
    model: str,
    temperature: int,
    max_completion_tokens: int,
    top_p: float,
) -> str:
    chat_completion = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_completion_tokens=max_completion_tokens,
        top_p=top_p,
    )
    response = chat_completion.choices[0].message.content
    return response


async def get_channel_history(client: object, channel: object, limit: int) -> list[dict[str]]:
    """Pulls messages from discord channel and formats for OpenAI API."""
    channel_history_generator = channel.history(limit=limit)

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
