import os
import random
import threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is required")

app = Flask(__name__)

@app.get("/")
def health():
    return "AVERO is running", 200

@app.get("/health")
def health_check():
    return {"status": "ok", "bot": "avero1bot"}, 200


def menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎲 Random Number", callback_data="number"), InlineKeyboardButton("🎯 Random Choice", callback_data="choice")],
        [InlineKeyboardButton("❓ Random Question", callback_data="question"), InlineKeyboardButton("💡 Random Idea", callback_data="idea")],
        [InlineKeyboardButton("🪙 Yes / No", callback_data="yesno"), InlineKeyboardButton("✨ Surprise Me", callback_data="surprise")],
    ])


def result_keyboard(function_name: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Again", callback_data=f"again:{function_name}")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu")],
    ])

QUESTIONS = [
    "What is one thing you would love to learn?",
    "If you could travel anywhere tomorrow, where would you go?",
    "What is a small thing that always makes you happy?",
    "What would you do if you knew you could not fail?",
    "What is one goal you want to achieve this year?",
    "Which skill would you instantly master if you could?",
    "What is the best advice you have ever received?",
    "If you had one free day with no responsibilities, how would you spend it?",
]

IDEAS = [
    "Try a new recipe today.",
    "Write down 3 goals for the next 7 days.",
    "Take a 20-minute walk without your phone.",
    "Learn one useful shortcut or skill today.",
    "Send a genuine thank-you message to someone.",
    "Rearrange one small part of your workspace.",
    "Start a note called 'Ideas' and add 5 things you might try.",
    "Spend 15 minutes reading something outside your usual interests.",
]


def random_number():
    return random.randint(1, 100)


def random_yes_no():
    return random.choice(["YES", "NO"])


def generate_choice_prompt():
    return "Send me the options you want AVERO to choose from.\n\nExample:\nPizza, Burger, Rice, Pasta"


def choose_from_text(text: str):
    separators = [",", "\n"]
    options = [text]
    for separator in separators:
        if separator in text:
            options = [item.strip() for item in text.split(separator) if item.strip()]
            break
    if len(options) < 2:
        return None
    return random.choice(options), options


def result_for(function_name: str):
    if function_name == "number":
        return f"🎲 Your random number is: <b>{random_number()}</b>"
    if function_name == "question":
        return f"❓ <b>Random Question</b>\n\n{random.choice(QUESTIONS)}"
    if function_name == "idea":
        return f"💡 <b>Random Idea</b>\n\n{random.choice(IDEAS)}"
    if function_name == "yesno":
        return f"🪙 <b>{random_yes_no()}</b>"
    return ""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("awaiting_choice", None)
    text = (
        "<b>Welcome to AVERO</b> ✨\n\n"
        "A simple place for random ideas, choices and answers.\n\n"
        "Choose what you want AVERO to do:"
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=menu_keyboard())


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_choice"):
        await update.message.reply_text("Use the buttons below to explore AVERO.", reply_markup=menu_keyboard())
        return

    selected = choose_from_text(update.message.text or "")
    if not selected:
        await update.message.reply_text(
            "🎯 Please send at least 2 options, separated by commas or new lines.\n\nExample: Pizza, Burger, Rice",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu", callback_data="menu")]])
        )
        return

    choice, options = selected
    context.user_data.pop("awaiting_choice", None)
    await update.message.reply_text(
        f"🎯 <b>AVERO chose:</b> {choice}\n\n<i>From: {', '.join(options)}</i>",
        parse_mode="HTML",
        reply_markup=result_keyboard("choice")
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu":
        context.user_data.pop("awaiting_choice", None)
        await query.edit_message_text(
            "<b>AVERO</b> ✨\n\nChoose what you want AVERO to do:",
            parse_mode="HTML",
            reply_markup=menu_keyboard()
        )
        return

    if data == "choice":
        context.user_data["awaiting_choice"] = True
        await query.edit_message_text(
            "🎯 <b>Random Choice</b>\n\nSend me the options you want AVERO to choose from.\n\nExample:\nPizza, Burger, Rice, Pasta",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu", callback_data="menu")]])
        )
        return

    if data.startswith("again:"):
        function_name = data.split(":", 1)[1]
        if function_name == "choice":
            context.user_data["awaiting_choice"] = True
            await query.edit_message_text(
                "🎯 <b>Random Choice</b>\n\nSend your options again.\n\nExample: Pizza, Burger, Rice",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Menu", callback_data="menu")]])
            )
            return
        if function_name == "surprise":
            function_name = random.choice(["number", "question", "idea", "yesno"])
        await query.edit_message_text(
            result_for(function_name),
            parse_mode="HTML",
            reply_markup=result_keyboard(function_name)
        )
        return

    if data == "surprise":
        function_name = random.choice(["number", "question", "idea", "yesno"])
        await query.edit_message_text(
            result_for(function_name),
            parse_mode="HTML",
            reply_markup=result_keyboard("surprise")
        )
        return

    if data in {"number", "question", "idea", "yesno"}:
        await query.edit_message_text(
            result_for(data),
            parse_mode="HTML",
            reply_markup=result_keyboard(data)
        )


def run_web_server():
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port, use_reloader=False)


def main():
    threading.Thread(target=run_web_server, daemon=True).start()
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
