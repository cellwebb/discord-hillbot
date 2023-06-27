import tiktoken


def chunk_long_messages(conversation_history: list[dict[str]]) -> None:
    """Splits long messages (2001+ tokens) in a conversation history to
    satisfy 'gpt-3.5-turbo' requirements."""
    i = 0
    while i < len(conversation_history):
        if len(conversation_history[i]["content"]) > 2000:
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            tokenized_content = encoding.encode(conversation_history[i]["content"])
            num_tokens = len(tokenized_content)
            if num_tokens > 2000:
                conversation_history[i]["content"] = ''.join(tokenized_content[:2000])
                conversation_history.insert(
                    i + 1,
                    {"role": conversation_history[i]["role"],
                    "content": tokenized_content[2000:]}
                )
        i += 1
    return


async def get_discord_conversation_history(
        client, message, channel_history_limit) -> list[dict[str]]:
    """Asyncrossly pulls messages from the same channel as the message
    and converts to format requirements of 'gpt-3.5-turbo'."""
    conversation_history_generator = message.channel.history(limit=channel_history_limit)
    conversation_history = []
    async for prev_message in conversation_history_generator:
        conversation_history.append(
            {"role": "assistant" if prev_message.author == client.user else "user",
            "content": prev_message.content})
    conversation_history.reverse()

    return conversation_history
