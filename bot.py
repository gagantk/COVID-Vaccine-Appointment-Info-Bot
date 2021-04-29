import logging
import traceback
import html
import json
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Defaults
from helpers import helper, constants

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    text = f'Hello {update.message.chat.first_name}!'
    text += f'\n\nThis bot helps you to check COVID-19 Vaccine Appointment availability for India.\nSource code available in <a href="https://github.com/gagantk/COVID-Vaccine-Appointment-Info-Bot">GitHub</a>.\n\nSend the Pin Code to check availability.'
    update.message.reply_text(text, disable_web_page_preview=True)


def check_by_pincode(update: Update, context: CallbackContext) -> None:
    pincode = update.message.text
    obj = helper.Helper(pincode)
    if not obj.check_results():
        update.message.reply_text('No data available for this Pin Code.')
        return
    keyboard = [
        [
            InlineKeyboardButton('18 - 44', callback_data='AGE18' + pincode),
            InlineKeyboardButton('45+', callback_data='AGE45' + pincode)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.chat_data['object'] = obj
    update.message.reply_text(
        'Choose an age category:', reply_markup=reply_markup)


def age_select_results(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    age_category = query.data[3:5]
    pincode = query.data[-6:]
    obj = context.chat_data.get('object', helper.Helper(pincode))
    if not obj.check_age_category(age_category, pincode):
        query.edit_message_text(
            'No hospitals available for this Age category.')
        return
    details = obj.get_centers(pincode)
    keyboard = [
        [InlineKeyboardButton(center[0], callback_data='CENTER' + center[1])] for center in details
    ]
    query.edit_message_text(f'Choose a hospital for Pin Code {pincode}:',
                            reply_markup=InlineKeyboardMarkup(keyboard))


def hospital_details(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    obj = context.chat_data['object']
    center_id = query.data[6:]
    text = obj.get_center_details(center_id)
    query.edit_message_text(text)


def error(update: Update, context: CallbackContext) -> None:
    logger.error(msg="Exception while handling an update:",
                 exc_info=context.error)
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__)
    tb = ''.join(tb_list)
    message = (
        'An exception was raised while handling an update\n'
        '<pre>update = {}</pre>\n\n'
        '<pre>context.chat_data = {}</pre>\n\n'
        '<pre>context.user_data = {}</pre>\n\n'
        '<pre>{}</pre>'
    ).format(
        html.escape(json.dumps(update.to_dict(),
                               indent=2, ensure_ascii=False)),
        html.escape(str(context.chat_data)),
        html.escape(str(context.user_data)),
        html.escape(tb)
    )
    context.bot.send_message(chat_id=constants.MY_PROFILE, text=message)


def main() -> None:
    defaults = Defaults(parse_mode=ParseMode.HTML)
    NAME = os.environ.get('NAME')
    PORT = os.environ.get('PORT')
    updater = Updater(constants.TOKEN, defaults=defaults)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(
        age_select_results, pattern=r'^AGE'))
    dispatcher.add_handler(CallbackQueryHandler(
        hospital_details, pattern=r'^CENTER'))
    dispatcher.add_handler(MessageHandler(
        Filters.regex(r'^[1-9]{2}[0-9]{4}$'), check_by_pincode))
    dispatcher.add_error_handler(error)

    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=constants.TOKEN,
                          webhook_url=f"https://{NAME}.herokuapp.com/{constants.TOKEN}")

    updater.idle()


if __name__ == '__main__':
    main()
