# discord-hillbot

:brain: Hillbot is a chatbot with episodic and semantic memories.

:robot: I made hillbot to impersonate my friend Dave. Dave's a loveable, quirky, and funny guy with a deep interest in comedy, movies, tv, video games, and board games. Hillbot's a loveable, quirky, and funny bot with a deep interest in comedy, movies, tv, video games, and board games. Hillbot does such a good job impersonating Dave that sometimes it isn't sure if it's Dave or if it's Hillbot!

![Image](assets/Screenshot.png)

## !davefacts

Users can give hillbot memories or facts about Dave using the `!davefacts` command, like so: `!davefacts Dave was born very late in life to a family of naked mole rats`

## setup instructions

1. Clone repo: `$ git clone https://github.com/cellwebb/discord-hillbot.git`
1. Set your OpenAI API key and Discord bot token to the environment variables `$OPENAI_API_KEY` and `$DISCORD_HILLBOT_TOKEN`
1. Create virtual environment: `$ python -m venv venv`
1. Activate virtual environment: `$ source venv/bin/activate`
1. Install python libraries: `$ pip install -r requirements.txt`
1. Run app.py: `python app.py`

## To Do

- Try out the stability API

<https://platform.stability.ai/docs/api-reference#tag/Edit/paths/~1v2beta~1stable-image~1edit~1search-and-replace/post>
