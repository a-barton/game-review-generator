# Game Review Generator

An exercise in deploying a large scale language/transformer model (GPT-Neo) in a serverless cloud architecture, in order to automatically generate video game reviews from a prompt with the game description.  Also includes a stack for a Discord bot deployed on a cloud server that listens for Steam game URL links in Discord messages, extracts the game description from Steam's website and uses it as a prompt to invoke the model pipeline, and then replies to the Discord message with a generated review for the linked game.

## Assumed Existing Components

Whilst this repo includes a Cloudformation template/stack with the majority of the components needed for the model stack and Discord bot stack, it assumes you already have existing the following:
1. An AWS S3 bucket to house build artifacts/model artifacts/modelling data (you can specify the name of this bucket in the `parameters.json` config file at the root of the repo)
2. A Discord bot created in the Discord developer portal and invited to whichever Discord server you would like the bot to listen in
3. A secret created in your AWS account's Secrets Manager that is named `DISCORD_BOT_TOKEN` and contains the token for the bot as sourced from your Discord developer portal
