from telegram.ext import Updater, MessageHandler, Filters
import logging
from random import choice, randint

from secret_data import TOKEN

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


replies = [
        'Your shifted audio',
        'Censored audio',
        'You could send this to your mom',
        '...',
        ]


def censore(input_path):
    '''Returns: path for the output file'''
    # TODO paste your censoring code here!
    return input_path


def make_reply(bot, audio, is_voice=False):
    if is_voice:
        audio_path = './test_{}.ogg'.format(randint(0, 100))
    else:
        try:
            file_name = audio.file_name.split('.')[0]
        except KeyError as e:
            file_name = 'test'
            logging.error('no file_name in %s', str(audio))

        if 'mime_type' not in audio.__dict__:
            logger.warning('no mime type in %s', str(audio))
            return None
        extension = audio['mime_type'].split('/')
        if extension[0] != 'audio':
            logger.warning('non-audio mime type: %s', extension[0])
            return None
        audio_path = './{}.{}'.format(file_name,
                                      extension[1].split('-')[-1])
    
    file_id = audio.file_id
    audio_file = bot.get_file(file_id)
    audio_file.download(audio_path)

    ret_path = censore(audio_path)
    return open(ret_path, 'rb')


def audio_echo(bot, update):
    if update.message.audio is not None:
        audio = update.message.audio
    elif update.message.document is not None:
        audio = update.message.document
    logger.info(audio)
    answer = make_reply(bot, audio)
    if answer is not None:
        bot.send_message(chat_id=update.message.chat_id, text=choice(replies))
        return bot.send_audio(chat_id=update.message.chat_id, audio=answer)    


def voice_echo(bot, update):
    voice = update.message.voice
    answer = make_reply(bot, voice, is_voice=True)
    if answer is not None:
        bot.send_message(chat_id=update.message.chat_id, text=choice(replies))
        return bot.send_voice(chat_id=update.message.chat_id, voice=answer)    


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def echo(bot, update):
    print(update)


def main():
    updater = Updater(TOKEN)

    dp = updater.dispatcher
    # dp.add_handler(MessageHandler(Filters.all, echo))
    dp.add_handler(MessageHandler(Filters.audio | Filters.document, audio_echo))
    dp.add_handler(MessageHandler(Filters.voice, voice_echo))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
