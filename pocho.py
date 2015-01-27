import willie
from datetime import date
from random import randint
from decimal import Decimal, InvalidOperation

TWOPLACES = Decimal(10) ** -2
CHANNEL = "#the_it_crowd"
MESSAGES = {
    'existing_lunch': 'Ya tenes un almuerzo creado, no podes crear otro hasta que canceles el actual. (.help lunch_cancel)',
    'unexisting_menu': 'No existe ningun menu de {nick}. Puedes crear el tuyo. (.help lunch_create)',
    'create_lunch': 'Necesitas crear un lunch antes de publicarlo. (.help lunch_create)',
    'created_lunch': 'Lunch creado. Podes cancelarlo (.help lunch_cancel)',
    'publish_lunch': 'Comida: {nick} ha creado un almuerzo: {menu}. te sumas? (.lunch_add {nick})',
    'deleted_lunch': 'Tu menu "{menu}" ha sido borrado. Podes crear el nuevo (.help lunch_create)',
    'added_lunch': 'Estas contado para el menu "{menu}".',
    'price_lunch': 'El precio por pera del menu de {nick} "{menu}" es {price}.',
    'not_in_channel': 'El bot no esta en el canal {channel}.',
    'not_total_price': 'Necesito que me digas cuanto costo el almuerzo. (.help lunch_done)',
}


@willie.module.commands(r'lunch_create')
@willie.module.example('.lunch_create milanesas con pure')
def lunch_create(bot, trigger):
    """
    Set a lunch for today: .lunch_create <menu descrition>

    """
    menu = trigger.group(2)

    # Check for existing lunch
    if bot.memory.contains(trigger.nick):
        bot.msg(trigger.nick, MESSAGES['existing_lunch'])
        return
    else:
        bot.memory[trigger.nick] = {
            'menu': menu,
            'date': date.today(),
            'diners': [trigger.nick,],
            'open': True
        }
        bot.msg(trigger.nick, MESSAGES['created_lunch'])
        return


@willie.module.commands(r'lunch_publish')
@willie.module.example('.lunch_publish')
def lunch_publish(bot, trigger):
    """
    Publish your lunch into the channel: .lunch_publish

    """
    # Check for existing lunch
    if bot.memory.contains(trigger.nick):
        if CHANNEL in bot.channels:
            menu = bot.memory[trigger.nick]['menu']
            message = MESSAGES['publish_lunch'].format(nick=trigger.nick, menu=menu)
            bot.msg(CHANNEL, message)
            return
        else:
            bot.msg(trigger.nick, MESSAGES['not_in_channel'].format(channel=CHANNEL))
            return
    else:
        bot.msg(trigger.nick, MESSAGES['create_lunch'])
        return


@willie.module.commands(r'lunch_cancel')
@willie.module.example('.lunch_cancel')
def lunch_cancel(bot, trigger):
    """
    Cancel your lunch: .lunch_cancel
    """
    # Check for existing lunch
    if bot.memory.contains(trigger.nick):
        menu = bot.memory[trigger.nick]['menu']
        del bot.memory[trigger.nick]
        bot.msg(trigger.nick, MESSAGES['deleted_lunch'].format(menu=menu))
        return
    else:
        bot.msg(trigger.nick, MESSAGES['unexisting_menu'].format(nick=trigger.nick))
        return


@willie.module.commands('lunch_add')
@willie.module.example('.lunch_add gaucho')
def lunch_add(bot, trigger):
    """
    Add to lunch: .lunch_add <nickname>
    """
    nick_name = trigger.group(2)
    # Check for existing lunch
    if bot.memory.contains(nick_name):
        if not (trigger.nick in bot.memory[nick_name]['diners']):
            menu = bot.memory[nick_name]['diners'].append(trigger.nick)
        bot.msg(trigger.nick, MESSAGES['added_lunch'].format(menu=bot.memory[nick_name]['menu']))
        return
    else:
        bot.msg(trigger.nick, MESSAGES['unexisting_menu'].format(nick=nick_name))
        return


@willie.module.commands('lunch_done')
@willie.module.example('.lunch_done 125')
def lunch_done(bot, trigger):
    """
    Publish price of lunch: .lunch_done <total_price>
    """
    total_price = trigger.group(2)

    if not total_price:
        bot.msg(trigger.nick, MESSAGES['not_total_price'])
        return

    try:
        total_price = Decimal(total_price)
    except InvalidOperation as e:
        bot.msg(trigger.nick, e.message)
        return

    if bot.memory.contains(trigger.nick):

        if CHANNEL in bot.channels:
            menu = bot.memory[trigger.nick]['menu']
            price = total_price / len(bot.memory[trigger.nick]['diners'])
            price = price.quantize(TWOPLACES)
            message = MESSAGES['price_lunch'].format(nick=trigger.nick, menu=menu, price=price)
            bot.msg(CHANNEL, message)
            return
        else:
            bot.msg(trigger.nick, MESSAGES['not_in_channel'].format(channel=CHANNEL))
            return
    else:
        bot.msg(trigger.nick, MESSAGES['create_lunch'])
        return


@willie.module.commands('lunch_detail')
@willie.module.example('.lunch_detail')
def lunch_detail(bot, trigger):
    """
    Return detail about your lunch: .lunch_detail
    """
    if bot.memory.contains(trigger.nick):
        menu = bot.memory[trigger.nick]['menu']
        date = bot.memory[trigger.nick]['date']
        diners = bot.memory[trigger.nick]['diners']
        bot.msg(trigger.nick, 'Menu: {}'.format(menu))
        bot.msg(trigger.nick, 'Date: {}'.format(date))
        bot.msg(trigger.nick, 'Diners: {}'.format(', '.join([nick for nick in diners])))
        return
    else:
        bot.msg(trigger.nick, MESSAGES['create_lunch'])
        return
