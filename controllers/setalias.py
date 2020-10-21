import models.user as user
import models.bot as bot

def action_setalias(telegram_item):
    """ action for /whatsnew command """
    # parse input
    if 'text' in telegram_item['message']:
        input_text = telegram_item['message']['text']

    try:
        input_text = input_text.split(' ', maxsplit=1)[1] # start from after first ' '
        val = input_text.split('|')
        res, msg = user.set_alias(val[0].strip(), val[1].strip() )
    except Exception as e:
        print(e)
        print(traceback.print_exc())
        bot.process_error(telegram_item, e)
        return None

    print('hasil setalias:', res, msg)

    bot.reply_message(telegram_item, msg, is_direct_reply=True)

    return None if not res else res

