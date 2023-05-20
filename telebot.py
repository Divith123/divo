import requests
import json
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = 'BOT TOKEN'
API_URL = 'https://api.openai.com/v1/chat/completions'
API_KEY = 'CHAT GPT API'

# Dictionary to store personal details
personal_details = {}
remember_counter = 0

# Handle the /start command
def start(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! My name is Ninja.")

# Handle incoming messages
def message(update: Update, context):
    message_text = update.message.text

    # Check if user wants to remember something
    if message_text.lower().startswith("remember"):
        remember(update, context, message_text)
    # Check if user wants to clear remembers
    elif message_text.lower() == "clear remembers":
        clear_remembers(update, context)
    # Check if user wants to clear a specific remember
    elif message_text.lower().startswith("clear remember"):
        clear_specific_remember(update, context, message_text)
    # Check if user wants to retrieve personal details
    elif message_text.lower() == "my passwords":
        retrieve_personal_details(update, context)
    else:
        # Send the message to ChatGPT
        headers = {
            'Authorization': 'Bearer ' + API_KEY,
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'system', 'content': 'You are a helpful assistant.'}, {'role': 'user', 'content': message_text}]
        }
        response = requests.post(API_URL, headers=headers, data=json.dumps(data))
        response_json = response.json()
        chatGPT_response = response_json['choices'][0]['message']['content']

        # Send the ChatGPT response to the user
        context.bot.send_message(chat_id=update.effective_chat.id, text=chatGPT_response)

# Handle the "remember" keyword
def remember(update: Update, context, message_text):
    global remember_counter
    remember_counter += 1
    personal_info = message_text[len("remember"):].strip()
    # Store personal detail with serial number
    personal_details[remember_counter] = personal_info
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"I've remembered that with serial number {remember_counter}.")

# Handle the "clear remembers" command
def clear_remembers(update: Update, context):
    global personal_details
    personal_details = {}
    context.bot.send_message(chat_id=update.effective_chat.id, text="I've cleared all remembers.")

# Handle the "clear remember <serial number>" command
def clear_specific_remember(update: Update, context, message_text):
    global personal_details
    serial_number = int(message_text.split()[2])
    if serial_number in personal_details:
        personal_details.pop(serial_number)
        # Update serial numbers of remaining remembers
        for i, key in enumerate(sorted(personal_details.keys())):
            personal_details[i+1] = personal_details.pop(key)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"I've cleared remember with serial number {serial_number}.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"There is no remember with serial number {serial_number}.")


# Handle the "What do you know about me?" command
def retrieve_personal_details(update: Update, context):
    user_id = update.effective_chat.id
    if personal_details:
        details_text = "\n".join([f"{serial_number}: {info}" for serial_number, info in personal_details.items()])
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Here are your remembers:\n{details_text}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="I'm sorry, but I don't have any remembers.")

# Create the Telegram bot and set up handlers
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(Filters.text, message)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(message_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
