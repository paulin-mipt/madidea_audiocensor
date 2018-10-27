import logging
import os
from random import choice, randint

from telegram.ext import Updater, MessageHandler, Filters
from telegram import ParseMode

from censorer import Censorer

try:
    from secret_data import TOKEN
except ModuleNotFoundError:
    if 'TELEGRAM_TOKEN' in os.environ:
        TOKEN = os.environ['TELEGRAM_TOKEN']
    else:
        logging.error('no token found, add secret_data.py or TELEGRAM_TOKEN environment variable')
        exit(1)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

replies = [
        '{} sent an swear voice message. The shifted audio:',
        'Censored audio from {}',
        'You could send this to {}\'s mom',
        '...',
        ]

class CensoringBot:

    def __init__(self):
        self.censorer = Censorer()
        self.updater = Updater(TOKEN)
        dp = self.updater.dispatcher
        dp.add_handler(MessageHandler(Filters.audio | Filters.document, self.audio_echo))
        dp.add_handler(MessageHandler(Filters.voice, self.voice_echo))
        dp.add_error_handler(self.error)
               


    def make_reply(self, bot, audio, is_voice=False):
        if is_voice:
            audio_path = './data/test_{}.ogg'.format(randint(0, 100))
        else:
            if 'mime_type' not in audio.__dict__:
                logger.warning('no mime type in %s', str(audio))
                return None
            extension = audio['mime_type'].split('/')
            if extension[0] != 'audio':
                logger.warning('non-audio mime type: %s', extension[0])
                return None
            audio_path = './data/test_{}.{}'.format(randint(0, 100),
                                                    extension[1].split('-')[-1])
        
        file_id = audio.file_id
        audio_file = bot.get_file(file_id)
        audio_file.download(audio_path)

        ret_path = self.censorer.censore(audio_path)
        if ret_path is not None:
            return open(ret_path, 'rb')
        return None


    def make_censoring(self, bot, message, censored_audio):
        logger.info('censored, sending')
        if censored_audio is None:
            return None
        user_name = 'previous sender'
        if 'from_user' in message.__dict__:
            user_name = '[{}](tg://user?id={})'.format(message.from_user.first_name, message.from_user.id)
        try:
            bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
        except Exception:
            pass  # nothing to do
        bot.send_message(chat_id=message.chat_id, text=choice(replies).format(user_name), parse_mode=ParseMode.MARKDOWN)
        return bot.send_audio(chat_id=message.chat_id, audio=censored_audio)
        

    def audio_echo(self, bot, update):
        if update.message.audio is not None:
            audio = update.message.audio
        elif update.message.document is not None:
            audio = update.message.document
        logger.info(audio)
        answer = self.make_reply(bot, audio)
        return self.make_censoring(bot, update.message, answer)  


    def voice_echo(self, bot, update):
        logger.info('new voice message, censoring...')
        voice = update.message.voice
        answer = self.make_reply(bot, voice, is_voice=True)
        return self.make_censoring(bot, update.message, answer)   


    def error(self, bot, update, error):
        logger.warning('Update "%s" caused error "%s"', update, error)


    def start(self):
        if not os.path.exists('./data'):
            os.makedirs('./data')
        
        if 'ON_HEROKU' in os.environ:
            port = int(os.environ.get('PORT', 8443))
            try:
                name = os.environ['HEROKU_APP_NAME']
            except KeyError:
                name = 'audio-censor'
            domain = 'herokuapp.com'
            self.updater.start_webhook(listen='0.0.0.0',
                                       port=port,
                                       url_path=TOKEN)
            fqdn = 'https://{}.{}/{}'.format(name, domain, TOKEN)
            logging.info(fqdn)
            self.updater.bot.set_webhook(fqdn)
        else:
            self.updater.start_polling()
        self.updater.idle()


if __name__ == '__main__':
    cbot = CensoringBot()
    cbot.start()
