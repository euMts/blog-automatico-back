from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from time import time
from os import getenv
from utils import (
    send_telegram_success_message,
    send_telegram_common_message,
    get_blog_post_openai,
)

load_dotenv()

MONGO_URI = getenv("MONGO_URI")
DATABASE_NAME = getenv("DATABASE_NAME")
TELEGRAM_BOT_KEY = getenv("TELEGRAM_BOT_KEY")
TELEGRAM_CHAT_ID = getenv("TELEGRAM_CHAT_ID")
OPENAI_KEY = getenv("OPENAI_KEY")
BLOG_POSTS_URL = getenv("BLOG_POSTS_URL")

client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client[DATABASE_NAME]


def main():
    start_time = time()

    try:
        theme = db.Themes.find_one({"alreadyUsed": False})

        if not theme:
            print("Nenhum tema disponível encontrado.")
            raise Exception("Nenhum tema disponível encontrado.")

        theme_name = theme.get("name", "Sem nome")
        print(f"Tema encontrado: {theme_name}")

        brasilia_tz = timezone(timedelta(hours=-3))  # UTC-3

        blog_post = get_blog_post_openai(api_key=OPENAI_KEY, theme=theme_name)
        blog_post_text = blog_post["blog_post"]
        # blog_post_total_cost_usd = blog_post["total_cost_usd"]
        blog_post_total_cost_brl = blog_post["total_cost_brl"]

        post_data = {
            "title": theme_name,
            "text": blog_post_text,
            "createdAt": datetime.now(brasilia_tz),
        }
        result = db.Posts.insert_one(post_data)

        inserted_id = result.inserted_id

        db.Themes.update_one({"_id": theme["_id"]}, {"$set": {"alreadyUsed": True}})

        execution_time = time() - start_time
        send_telegram_success_message(
            api_key=TELEGRAM_BOT_KEY,
            chat_id=TELEGRAM_CHAT_ID,
            inserted_id=inserted_id,
            theme_name=theme_name,
            execution_time=execution_time,
            blog_post_total_cost_brl=blog_post_total_cost_brl,
            blog_posts_url=BLOG_POSTS_URL,
        )

    except Exception as e:
        error_message = f"Ocorreu um erro no script: {e}"
        print(error_message)
        send_telegram_common_message(
            api_key=TELEGRAM_BOT_KEY, chat_id=TELEGRAM_CHAT_ID, message=error_message
        )


if __name__ == "__main__":
    main()
