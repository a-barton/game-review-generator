import logging
import watchtower

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger("game-review-generator-discord-bot-ec2")
LOGGER.setLevel(logging.DEBUG)

handler = watchtower.CloudWatchLogHandler(
    log_group="game-review-generator-discord-bot-ec2"
)

LOGGER.addHandler(handler)