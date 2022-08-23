import logging
import os
import time

import requests
from discord_webhook import DiscordEmbed, DiscordWebhook
from dotenv import load_dotenv

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"}
BASE_URL = "https://www.reddit.com/r/ProgrammerHumor/hot.json"

load_dotenv()
webhook = DiscordWebhook(url=os.getenv("WEBHOOK_URL"))
date_strftime_format = "%D %H:%M:%S"
message_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(format=message_format, datefmt=date_strftime_format, level=logging.INFO)
last_post_id = None


def is_different_post() -> bool:
    """Returns if the last post sent via the webhook is different from the last post found on the subreddit.

    Returns:
        bool: False or True.
    """
    logging.info("Checking if the last post is different from the last post found on the subreddit...")
    r = requests.get(url=BASE_URL, headers=HEADERS)
    res = r.json()
    return last_post_id != res["data"]["children"][1]["data"]["id"]


def get_last_post() -> dict:
    """Returns the last post found on the subreddit.

    Returns:
        dict: Dictionary include useful information from the last post.
    """
    logging.info("Getting the last post from the subreddit...")
    r = requests.get(url=BASE_URL, headers=HEADERS)
    res = r.json()
    last_post = res["data"]["children"][1]["data"]
    return {
        "id": last_post.get("id", ""),
        "title": last_post.get("title", ""),
        "url_post": last_post.get("permalink", ""),
        "url_media": last_post.get("url", ""),
        "author": last_post.get("author", "")
    }


def run() -> None:
    """Check if subreddit has a new post and send it to the webhook if it is different from the last post sent.
    """
    global last_post_id
    while True:
        if is_different_post():
            post = get_last_post()
            embed = DiscordEmbed(
                title=post["title"],
                description="Last popular post from r/ProgrammerHumor.",
                color="03b2f8",
                url=f"https://www.reddit.com{post['url_post']}"
            )
            embed.set_timestamp()
            embed.set_image(url=post["url_media"])
            embed.set_footer(text=f"Publish by u/{post['author']}")
            webhook.add_embed(embed)
            logging.info("Sending the new post to the webhook...")
            webhook.execute()
            last_post_id = post["id"]
        time.sleep(60)


if __name__ == "__main__":
    run()
 