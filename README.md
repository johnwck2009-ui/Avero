# AVERO

AVERO is a simple Telegram bot for random ideas, choices and answers.

## Features

- Random Number — generates a number from 1 to 100
- Random Choice — send options and AVERO picks one
- Random Question — gives a random question
- Random Idea — gives a simple idea
- Yes / No — returns a random YES or NO
- Surprise Me — randomly uses one of AVERO's functions
- Again and Menu buttons after results

## Run locally

1. Install Python 3.10+.
2. Install dependencies with `pip install -r requirements.txt`.
3. Set the environment variable `BOT_TOKEN` to your Telegram bot token.
4. Run `python bot.py`.

## Deploy on Render

This repository includes `render.yaml`. Create a Render Web Service from this repository and set the `BOT_TOKEN` environment variable to the token from BotFather.

Never commit the bot token to GitHub.
