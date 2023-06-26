import tiktoken

def chunk_long_messages(conversation_history: List[Dict[str]]) -> None:
    """Splits long messages in a conversation history to satisfy requirements
    for 'gpt-3.5-turbo'.

    Messages with 2001 or more tokens are split into multiple messages
    with the same "role"."""
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
