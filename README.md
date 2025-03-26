# Hillbot: Taking Dave's place in the world

:brain: Hillbot is a chatbot with episodic and semantic memories, which is just a fancy way of saying it's really good at remembering all the crazy stuff my friend Dave says and does.

:robot: I created Hillbot to impersonate Dave, a comedy, movie, TV, video game, and board game enthusiast. Hillbot embodies Dave's best qualities, minus the ability to eat an entire pizza by itself. Sometimes Hillbot gets so into character that it's hard to tell if it's really Dave or just the bot – and that's part of the fun!

![Image](assets/Screenshot.png)

## Features: What Hillbot Can Do

- Engage in conversations with Hillbot and experience Dave's signature personality, complete with witty one-liners and humorous jokes
- Generate images using OpenAI's DALL-E, perfect for creating memes
- Create image variations using Stable Diffusion, allowing you to see Dave in different scenarios
- Feed Hillbot's memory system with interesting facts about Dave, like the time he accidentally superglued his shoes to the floor
- Utilize the prompt enhancement system to help Hillbot come up with creative and humorous responses

## Commands: How to Interact with Hillbot

- `!davefacts` - Add memories about Dave, like the time he tried to cook a frozen pizza in the microwave (e.g. `!davefacts Dave once tried to break the world record for most hamburgers eaten in one sitting`)
- `!prompt_enhancer` - Add prompt enhancement templates to help Hillbot come up with the perfect joke
- `!image` or `!img` or `!i` - Generate images to enhance your conversations
- `!again` or `again` or `more` or `deeper` - Create variations of images to explore different scenarios

## Setup: Getting Hillbot Up and Running

1. Clone the repository:

   ```bash
   git clone https://github.com/cellwebb/discord-hillbot.git
   cd discord-hillbot
   ```

2. Set environment variables:

   ```bash
   export OPENAI_API_KEY=your_openai_api_key
   export DISCORD_HILLBOT_TOKEN=your_discord_bot_token
   ```

3. Install dependencies:

   ```bash
   make install
   ```

4. Run the bot

   ```bash
   make run
   ```

## Development: For Developers

- Run tests: `make test`
- Check code style: `make lint`
- Format code: `make format`
- Clean up: `make clean`

## Requirements: The Essentials

- Python 3.11+
- OpenAI API key
- Discord bot token

## License

MIT License
