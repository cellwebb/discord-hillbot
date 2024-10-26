async def get_channel_history(
    client: object, channel: object, message_limit: int
) -> list[dict[str]]:
    """Pulls messages from discord channel and formats for OpenAI API.

    NOTE:
    - Discord's channel history generator produces messages in reverse chronological order.
    - OpenAI won't accept images from the assistant, so we call it a user message.

    TODO:
    - Add support for replies.
    - Add support for embeds.
    - Add support for other attachment types.
    """

    channel_history = []

    channel_history_generator = channel.history(limit=message_limit)
    async for message in channel_history_generator:
        role = "assistant" if message.author == client.user else "user"
        name = message.author.name.replace(".", "-")
        text_json = {"type": "text", "text": message.content}

        image_content = []
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type.startswith("image"):
                    image_json = {"type": "image_url", "image_url": {"url": attachment.url}}
                    image_content.append(image_json)

        if role == "user":
            content = [text_json, *image_content]
            channel_history.append({"role": role, "name": name, "content": content})
        else:
            if image_content:
                channel_history.append({"role": "user", "name": name, "content": image_content})
            channel_history.append({"role": role, "name": name, "content": text_json})

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
