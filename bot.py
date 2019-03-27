import os
import logging
from datetime import datetime

from telegram.ext import Updater, CommandHandler
from telegram import ParseMode
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
    update.message.reply_text('Hi! Use /ping_on <seconds> ' +
                                  '<mention user with "@" symbol> ' +
                                  '<message, if you wish>')


def help_message(bot, update):
    update.message.reply_text('Help message')


def alarm(bot, job):
    """Send the ping message."""
    query = Message.select().where(Message.chat_id == job.context) \
                               .order_by(Message.created.desc()).get()
    text = (f"[{query.to_user}](tg://user?id={query.to_user_id}) " +
           f"Ping!\n{query.content}")
    bot.send_message(job.context, 
                     text=text,
                     parse_mode=ParseMode.MARKDOWN)


def set_ping(bot, update, args, job_queue, chat_data):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        interval = int(args[0])
        if interval <= 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return
        
        entities = update.message.parse_entities()
        try:
            entity = list(entities.keys())[1]
        except:
            update.message.reply_text("Please mention someone. " +
                                      "Pingo-bot don't know what " +
                                      "he need to do ;)")
            return
        
        if not entity.user:
            update.message.reply_text("Please mention a user in the group")
            return

        user_arg = args[1]
        all_text = update.message.text
        start_text = all_text.find(user_arg) + len(user_arg)
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
            to_user_id=entity['user']['id'],
            to_user=entity['user']['first_name']
        )

        # Add job to queue
        job = job_queue.run_repeating(alarm, interval, context=chat_id)
        chat_data['job'] = job
        
        update.message.reply_text('Ping successfully set!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /ping_on <seconds> ' +
                                  '<mention user with "@" symbol> ' +
                                  '<message, if you wish>')


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

