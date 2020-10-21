import re
import models.bot as bot

def action_lapor(item, peserta=None):
    """ action for /lapor command """
    # parse input
    if 'caption' in item['message']:
        input_text = item['message']['caption']
    elif 'text' in item['message']:
        input_text = item['message']['text']

    lines = input_text.split("\n")
    first_params = lines[0]
    first_params = first_params[first_params.find(' ')+1 :] # start from after first ' '
    first_params = first_params.split('|') # split with '|'
    if len(first_params) != 2 :
        bot.process_error(item, 'Wrong format')
        return

    data = {
        'projectName': first_params[0].strip(),
        'nameTask': first_params[1].strip(),
    }
    # parsing options params
    for line in lines[1:]:
        val = [ l.strip() for l in line.split(sep=':', maxsplit=1) ]
        if len(val) > 1 and len(val[1]) > 0: # only process lines which contain field_name & content
            field_name = val[0].lower()
            content = val[1]
            if field_name == 'peserta':
                data[field_name] = [
                    name.strip()
                    for name in re.split(',|\ ', content)
                    if len(name.strip()) > 0
                ]
            else:
                data[field_name] = content

    if 'photo' in item['message']:
        image_data = bot.process_images(item['message']['photo'])
    # if this message is replying to a photo
    elif 'reply_to_message' in item['message'] \
    and 'photo' in item['message']['reply_to_message']:
            image_data = bot.process_images(item['message']['reply_to_message']['photo'])
    else:
        bot.process_error(item, 'No photo data in this input!')
        return None

    return bot.process_report(item, data, image_data, peserta=peserta, save_history=(peserta is None))


