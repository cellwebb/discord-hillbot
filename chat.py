import openai

openai_client = openai.AsyncOpenAI()


async def get_chatgpt_response(
    messages: list[dict[str]],
    model: str,
    temperature: int,
    max_completion_tokens: int,
    top_p: float,
) -> str:
    chat_completion = await openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_completion_tokens=max_completion_tokens,
        top_p=top_p,
    )
    response = chat_completion.choices[0].message.content
    return response


async def get_channel_history(
    client: object, channel: object, message_limit: int, image_limit: int
) -> list[dict[str]]:
    """Pulls messages from discord channel and formats for OpenAI API.

    NOTE:
    - Discord's channel history generator produces messages in reverse chronological order.
    - OpenAI won't accept images from the assistant, so we call it a user message.

    TODO:
    - Add support for replies.
    - Add support for embeds.
    - Add support for messages with multiple attachments.
    """

    channel_history = []
    image_count = 0

    channel_history_generator = channel.history(limit=message_limit)
    async for message in channel_history_generator:
        formatted_message = {
            "role": "assistant" if message.author == client.user else "user",
            "name": message.author.name.replace(".", "-"),
            "content": [{"type": "text", "text": message.content}],
        }

        if (
            image_count < image_limit
            and message.attachments
            and message.attachments[0].content_type.startswith("image")
        ):
            image_count += 1
            if formatted_message["role"] == "user":
                formatted_message["content"].append(
                    {"type": "image_url", "image_url": {"url": message.attachments[0].url}},
                )
            else:
                channel_history.append(
                    {
                        "role": "user",
                        "name": message.author.name.replace(".", "-"),
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": message.attachments[0].url},
                            }
                        ],
                    }
                )

        channel_history.append(formatted_message)

    channel_history.reverse()

    return channel_history
