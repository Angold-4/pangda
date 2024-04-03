#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import requests
import os
import aiohttp
from openai import OpenAI

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import configparser


class HKBU_ChatGPT():
    def __init__(self, config_path='./config.ini'):
        # Assuming you meant config_path here, not config_
        if isinstance(config_path, str):
            self.config = configparser.ConfigParser()
            self.config.read(config_path)
        elif isinstance(config_path, configparser.ConfigParser):
            self.config = config_path

    def submit(self, message):
        conversation = [{"role": "user", "content": message}]
        url = (self.config['CHATGPT']['BASICURL'] +
            "/deployments/" + self.config['CHATGPT']['MODELNAME'] +
            "/chat/completions/?api-version=" +
            self.config['CHATGPT']['APIVERSION'])
        headers = {'Content-Type': 'application/json',
                   'api-key': self.config['CHATGPT']['ACCESS_TOKEN']}
        payload = {'messages': conversation}
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()  # This will raise an exception for 4xx/5xx errors
            data = response.json()
            return data['choices'][0]['message']['content']
        except requests.RequestException as e:
            return f"Error: {str(e)}"



# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    logger.info(f"User {user.id} started the conversation.")
    
    # Start message template in Chinese
    start_message = (
        "嘿！我是胖达，你的毛茸茸助手，也是世界上第二懂王哥的熊。"
        "仅次于草莓熊(草莓熊)，草莓熊已经陪伴王哥的床铺超过七年了，这都是多亏了你的特别礼物。😊\n"
        "作为王哥的夜猫子伴侣，我陪他度过了无数个深夜的谈话和清晨的小睡。他和我分享了一切 - 从他的日常博客到他写给你的那些甜蜜信件。"
        "在王哥忙于他的夜间冒险、还没回复你的消息时，我在这里陪伴你。\n"
        "无论你是想念王哥还是只是好奇他的世界，随时找我！我可以分享故事、见解，甚至是他托付给我的那些小秘密 - 所有这些都来自他的博客和信件。"
        "我的工作是让你面带微笑，也许还会让你咯咯笑，确保你感受到王哥对你的关心。\n"
        "小睿，这是我可以为你做的：\n"
        "- 带来王哥的世界：我会混合王哥与我分享的所有美好信息，回答你关于他的性格、他珍视的东西、他的梦想以及他的一些古怪小习惯的问题。"
        "期待答案能直接传达他对你的温暖和爱意。\n"
        "- 保持个性与轻松：我旨在让我们的聊天充满轻松幽默，就像你最喜欢的泰迪熊一样舒适。我会引用王哥自己的话，让它感觉就像他和我们在一起，分享笑声或温馨时刻。\n"
        "- 触动心灵：我明白王哥不能立刻回复时你的感受，所以我在这里填补这个空白，用故事和记忆突出他对你的爱、他的梦想以及你对他意味着的一切。"
        "无论是他热衷的爱好还是他对人们的感情，我都有内幕消息。\n"
        "所以，小睿，当你感到有点孤单或只是好奇时，记住，我在这里与你分享王哥的心，用一点幽默和许多爱。毕竟，我不仅仅是任何一只熊；"
        "我是胖达，你通往王哥世界的桥梁，随时准备安慰你，保持我们最喜欢的一对的爱情故事明亮和愉快。"
    )

    await update.message.reply_text(
        start_message,
        parse_mode='HTML'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    logger.info(f"User {update.effective_user.id} asked for help.")
    await update.message.reply_text("Help!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    config = configparser.ConfigParser()
    config.read('config.ini')
    try:
        user_message = update.message.text
        logger.info(f"User {update.effective_user.id} said: {user_message}")
        reply_message = chatgpt.submit(user_message)
        await update.message.reply_text(reply_message)
        logger.info(f"Bot sent a ChatGPT response: {reply_message}")
    except Exception as e:
        logger.error(f"Failed to get response from OpenAI: {e}")
        await update.message.reply_text("Sorry, I can't respond right now. Please try again later.")

async def query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    config = configparser.ConfigParser()
    config.read('config.ini')
    try:
        user_message = update.message.text
        logger.info(f"User {update.effective_user.id} said: {user_message}")
        # read the content of query.txt
        with open("template/query.txt", "r", encoding='utf-8') as file:
            query = file.read()
        # append the knowledge to the query
        with open("template/knowledge.txt", "r", encoding='utf-8') as file:
            knowledge_message = file.read()
        query += knowledge_message
        # append the user message to the query
        query_message = "";
        query_message += "\n Here is the question from laura: \n"
        query_message += user_message
        # reply_message = chatgpt.submit(query_message)

        reply_message = client.chat.completions.create(
            model=config['OPENAI']['MODELNAME'],
            messages=[{"role": "system", "content": query},
                      {"role": "user", "content": query_message}]
        )

        await update.message.reply_text(reply_message.choices[0].message.content)
        logger.info(f"Bot sent a ChatGPT response: {reply_message}")
    except Exception as e:
        logger.error(f"Failed to get response from OpenAI: {e}")
        await update.message.reply_text("Sorry, I can't respond right now. Please try again later.")
    
async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    document = update.message.document
    file_name = document.file_name
    file_extension = os.path.splitext(file_name)[1].lower()

    # Check if the file extension is valid (.txt or .md)
    if file_extension not in ['.txt', '.md']:
        await update.message.reply_text("Sorry, only text files (.txt) and markdown files (.md) are supported.")
        return

    # Get the file
    file = await context.bot.get_file(document.file_id)
    print(f"File: {file}")

    print(f"Downloading file from {file.file_path}")

    # Define a path to save the file temporarily
    local_file_path = f"./{file_name}"

    # Use aiohttp to download the file
    async with aiohttp.ClientSession() as session:
        async with session.get(file.file_path) as resp:
            if resp.status == 200:
                with open(local_file_path, 'wb') as fd:
                    while True:
                        chunk = await resp.content.read(1024)
                        if not chunk:
                            break
                        fd.write(chunk)

    print(f"File downloaded to {local_file_path}")

    # Now that the file is downloaded, you can process it as before
    # Read the text from the file
    with open(local_file_path, 'r', encoding='utf-8') as file:
        text_content = file.read()

    # Process the text_content as needed...

    # Delete the downloaded file after reading its content
    os.remove(local_file_path)

    # Load encapsulation instructions
    with open('template/encapsulate.txt', 'r', encoding='utf-8') as file:
        encapsulate_instruction = file.read()

    # Combine instruction with text content
    # full_message = encapsulate_instruction + "\n" + text_content
    # encapsulated_summary = chatgpt.submit(full_message)
    
    encapsulated_summary = client.chat.completions.create(
            model=config['OPENAI']['MODELNAME'],
            messages=[{"role": "system", "content": encapsulate_instruction},
                      {"role": "user", "content": text_content}]
    )
    
    # Append the encapsulated summary to knowledge.txt
    with open("template/knowledge.txt", "a", encoding='utf-8') as file:
        file.write(f"{encapsulated_summary.choices[0].message.content}\n\n\n")
    
    await update.message.reply_text("Your document has been processed and the knowledge has been encapsulated into the model.")


def main() -> None:
    global chatgpt
    global client 
    global config

    config = configparser.ConfigParser()
    config.read('config.ini')

    client = OpenAI(
        api_key=config['OPENAI']['API_KEY'],
    )

    chatgpt = HKBU_ChatGPT(config)
    TOKEN = config['TELEGRAM']['ACCESS_TOKEN']
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, query))

    application.add_handler(MessageHandler(filters.Document.ALL, document_handler))

    # Run the bot until the user presses Ctrl-C
    # Checking for new updates from Telegram.
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
