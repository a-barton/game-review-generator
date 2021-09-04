import logging
import watchtower
import requests

logging.basicConfig(level=logging.DEBUG)

instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text
logger_name = f"game-review-generator-discord-bot-ec2-id-{instance_id}"

LOGGER = logging.getLogger(logger_name)
LOGGER.setLevel(logging.DEBUG)

handler = watchtower.CloudWatchLogHandler(
    log_group=logger_name
)

LOGGER.addHandler(handler)