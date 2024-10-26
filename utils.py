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


async def add_dave_fact(message: object) -> None:
    async with message.channel.typing():
        new_fact = message.content.replace("!davefacts", "").strip()
        with open("resources/davefacts.txt", "a") as f:
            f.write("- " + new_fact + "\n")
    await message.channel.send("Thanks for telling me more about Dave!")
    return


async def add_prompt_enhancer(message: object) -> None:
    async with message.channel.typing():
        new_prompt_enhancer = message.content.replace("!prompt_enhancer", "").strip()
        with open("resources/prompt_enhancers.txt", "a") as f:
            f.write(new_prompt_enhancer + "\n")
    await message.channel.send("Thanks I've added it to the list!")
    return


def message_contains_image(message: object) -> bool:
    """Check if a message contains an image."""
    if message.attachments:
        for x in message.attachments:
            if x.content_type.startswith("image"):
                return True
    return False
