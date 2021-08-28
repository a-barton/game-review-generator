# Game Review Generator

An exercise in deploying a large scale language/transformer model ([GPT-Neo](https://github.com/EleutherAI/gpt-neo) - utilised via the [Huggingface Transformers library](https://huggingface.co/transformers/)) in a serverless cloud architecture, in order to automatically generate video game reviews from a prompt with the game description.  Also includes a stack for a Discord bot deployed on a cloud server that listens for Steam game URL links in Discord messages, extracts the game description from Steam's website and uses it as a prompt to invoke the model pipeline, and then replies to the Discord message with a generated review for the linked game.

![Example Discord bot review response](docs/witcher-review.png "Example Discord bot review response")

## **Pre-requisites**

### **Assumed Existing Components**

Whilst this repo manages a Cloudformation template/stack with the majority of the components needed for the model stack and Discord bot stack, it assumes you already have the following things created:

1. An AWS account (naturally) - one for which you have admin access
2. An S3 bucket in your AWS account to house build artifacts/model artifacts/modelling data (you must specify the name of this bucket in the `parameters.json` config file at the root of the repo)
3. A [Discord bot created in the Discord developer portal](https://discord.com/developers/applications) and invited to whichever Discord server you would like the bot to listen in (check out the first part of [this guide](https://www.freecodecamp.org/news/create-a-discord-bot-with-python/) for details on Discord bot account setup)
4. A secret created in your AWS account's Secrets Manager that is named `DISCORD_BOT_TOKEN` and contains the token for your Discord bot as sourced from your Discord developer portal

### **Development Environment Requirements**

In order to clone and work with this repo (including deploying the solution stack to AWS), your development environment will need the following:

1. This repo is intended to be used on a Unix based system (e.g. Ubuntu) - setup, build and deployment is all managed via a [Makefile](https://opensource.com/article/18/8/what-how-makefile)
2. Python dependancies are versioned via a conda virtual environment - I recommend installing [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
3. The model is container based - you will need [Docker](https://docs.docker.com/engine/install/), and you will need to make sure the [Docker daemon is running](https://docs.docker.com/config/daemon/) any time you build/push the container
4. Deployment to AWS requires the [AWS CLI tool](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html) (naturally), and you will need to make sure you have your [AWS account programmatic access credentials configured](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)

## **Quickstart**

1. Clone/fork this repo
2. Open the `parameters.json` file at the root of the repo and address the following:
    1. Modify the `bucket` parameter value in `parameters.json` to reference your desired AWS S3 bucket
    2. Modify the `availability_zone` parameter value in `parameters.json` to reference your desired AWS availability zone - you must ensure that the instance type specified in the `batch_instance_type` parameter is one that is [available in the availability zone](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-discovery.html) you select
3. Open the Makefile at the root of the repo and address the following:
    1. Modify the `PROJECT_NAME` (defined at the top) to a different name of your choosing
    2. Also modify the `PROJECT_ALIAS` in line with the change you made to the `PROJECT_NAME`
4. Initialise the repo by opening a terminal at the root and running `make init`
    * This will setup a new Conda virtual environment and install required Python libraries.
    * It will also source the fine-tuned game review model and place it in your nominated S3 bucket.

At this point, assuming you have the Discord bot created and the bot token in AWS Secrets Manager, you can **deploy the model and bot stack by running `make all`**.

## **Architecture**

![Solution Architecture](docs/architecture.png "Solution Architecture")
