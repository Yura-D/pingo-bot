import os
import logging
from datetime import datetime

from telegram.ext import Updater, CommandHandler
from database import Message


try:
    TELEGRAM_API_KEY = os.environ['TELEGRAM_API_KEY']
except:
    raise Exception('Telegram api key do not exist')

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
    )
logger = logging.getLogger(__name__)


def start(bot, update):
    update.message.reply_text('Hi! Use /set <seconds> to set a timer')


def help_message(bot, update):
    update.message.reply_text('Help message')


def alarm(bot, job):
    """Send the alarm message."""
    query = Message.select().where(Message.chat_id == job.context) \
                               .order_by(Message.created.desc()).get()
    bot.send_message(job.context, 
                     text=f'@{query.to_user} Ping!\n{query.content}')


def set_ping(bot, update, args, job_queue, chat_data):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        interval = int(args[0])
        if interval <= 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return
        
        to_user = args[1]
        if to_user[0] != '@':
            update.message.reply_text('Please add user name ' +
                                      'that starts with "@"!')
        all_text = update.message.text
        start_text = all_text.find(to_user) + len(to_user)
        ping_text = all_text[start_text:].lstrip()

        from_user = update.message.from_user
        from_user_complite = (str(from_user.id) + ', ' +
                             str(from_user.first_name) + ' ' +
                             str(from_user.last_name))

        Message.create(
            chat_id=chat_id,
            created=datetime.now(),
            content=ping_text,
            from_user=from_user_complite,
            to_user=to_user
        )

        # Add job to queue
        job = job_queue.run_repeating(alarm, interval, context=chat_id)
        chat_data['job'] = job
        
        update.message.reply_text('Ping successfully set!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


def unping(bot, update, chat_data):
    """Remove the job if the user changed their mind."""
    if 'job' not in chat_data:
        update.message.reply_text('You have no active Pings')
        return

    job = chat_data['job']
    job.schedule_removal()
    del chat_data['job']

    update.message.reply_text('Ping successfully unset!')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Run bot."""
    updater = Updater(TELEGRAM_API_KEY)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_message))
    dp.add_handler(CommandHandler("ping_on", set_ping,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("ping_off", unping, pass_chat_data=True))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

