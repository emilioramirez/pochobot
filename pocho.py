from __future__ import unicode_literals
import willie
import re
from datetime import date
from decimal import Decimal, InvalidOperation

TWOPLACES = Decimal(10) ** -2
MESSAGES = {
    'existing_lunch': 'Ya tenes un almuerzo creado, no podes crear otro hasta que canceles el actual. (.help lunch_cancel)',
    'unexisting_menu': 'No existe ningun menu de {nick}. Puedes crear el tuyo. (.help lunch_create)',
    'create_lunch': 'Necesitas crear un almuerzo antes de poder publicar uno. (.help lunch_create)',
    'created_lunch': 'Lunch creado. Podes cancelarlo (.help lunch_cancel)',
    'publish_lunch': 'Comida: {nick} ha creado un almuerzo: {menu}. te sumas? (.lunch_add {nick})',
    'deleted_lunch': 'Tu menu "{menu}" ha sido borrado. Podes crear el nuevo (.help lunch_create)',
    'added_lunch': '{nick} esta contado para el menu "{menu}".',
    'price_lunch': 'El precio por pera del menu de {nick} "{menu}" es {price}.',
    'not_in_channel': 'El bot no esta en el canal {channel}.',
    'not_total_price': 'Necesito que me digas cuanto costo el almuerzo. (.help lunch_done)',
    'list_lunch': 'Almuerzos creados.',
    'list_lunch_item': 'Menu {owner}: {menu}. (Vacantes {vacants}).',
    'no_more_limit': 'No hay mas vacantes para el menu de {nick}.',
    'no_lunches': 'No hay nigun menu creado',
}


@willie.module.commands(r'lunch_create')
@willie.module.example('.lunch_create milanesas con pure')
def lunch_create(bot, trigger):
    """
    Set a lunch for today: .lunch_create <menu descrition>

    """
    menu = trigger.group(2).strip()
    limit_enable = False
    limit = 0

    p = re.compile(r"\d+")
    result = p.findall(menu)
    if result:
        limit_enable = True
        # Minus 1 because the owner is included
        limit = int(result[0]) - 1

    if bot.memory.contains('lunch'):
        # Storage lunch exists, do not need to create
        if trigger.nick in bot.memory['lunch'].keys():
            # Lunch for nick exists
            bot.msg(trigger.nick, MESSAGES['existing_lunch'])
            return
        else:
            # Added new lunch for nick to the storage
            bot.memory['lunch'][trigger.nick] = {
                'menu': menu,
                'date': date.today(),
                'diners': [trigger.nick, ],
                'limit': limit,
                'limit_enable': limit_enable,
            }
    else:
        # Storage lunch do not exits, we need to create it and added
        # the lunch for nick
        bot.memory['lunch'] = {
            trigger.nick: {
                'menu': menu,
                'date': date.today(),
                'diners': [trigger.nick, ],
                'limit': limit,
                'limit_enable': limit_enable,
            }
        }

    bot.msg(trigger.nick, MESSAGES['created_lunch'])
    return


@willie.module.commands(r'lunch_publish')
@willie.module.example('.lunch_publish')
def lunch_publish(bot, trigger):
    """
    Publish your lunch into the channel: .lunch_publish

    """
    if bot.memory.contains('lunch'):
        # Storage lunch exists, do not need to create
        if trigger.nick in bot.memory['lunch'].keys():
            # Lunch for nick exists
            menu = bot.memory['lunch'][trigger.nick]['menu']
            message = MESSAGES['publish_lunch'].format(nick=trigger.nick, menu=menu)
            for channel in bot.channels:
                bot.msg(channel, message)
            return
    # Storage lunch do not exits
    bot.msg(trigger.nick, MESSAGES['create_lunch'])
    return


@willie.module.commands(r'lunch_cancel')
@willie.module.example('.lunch_cancel')
def lunch_cancel(bot, trigger):
    """
    Cancel your lunch: .lunch_cancel
    """
    if bot.memory.contains('lunch'):
        # Storage lunch exists, do not need to create
        if trigger.nick in bot.memory['lunch'].keys():
            # Lunch for nick exists
            menu = bot.memory['lunch'][trigger.nick]['menu']
            del bot.memory['lunch'][trigger.nick]
            bot.msg(trigger.nick, MESSAGES['deleted_lunch'].format(menu=menu))
            return
    # Storage lunch do not exits
    bot.msg(trigger.nick, MESSAGES['unexisting_menu'].format(nick=trigger.nick))
    return


@willie.module.commands('lunch_add')
@willie.module.example('.lunch_add gaucho')
def lunch_add(bot, trigger):
    """
    Add to lunch: .lunch_add <nickname>
    """
    lunch_owner_nickname = trigger.group(2).strip()
    nick_to_add = trigger.nick

    if bot.memory.contains('lunch'):
        if trigger.nick in bot.memory['lunch'].keys():
            # The lunch creator try to add someone to the his lunch
            nick_to_add = lunch_owner_nickname
            lunch_owner_nickname = trigger.nick
        # Storage lunch exists, do not need to create
        if lunch_owner_nickname in bot.memory['lunch'].keys():
            # Lunch for nick exists

            # Check lunch limit
            limit_enable = bot.memory['lunch'][lunch_owner_nickname]['limit_enable']
            limit = bot.memory['lunch'][lunch_owner_nickname]['limit']
            if limit_enable and (limit < 1):
                bot.msg(lunch_owner_nickname, MESSAGES['no_more_limit'].format(nick=lunch_owner_nickname))
                bot.msg(nick_to_add, MESSAGES['no_more_limit'].format(nick=lunch_owner_nickname))
                return

            # Add nick to diners only one time
            if not (nick_to_add in bot.memory['lunch'][lunch_owner_nickname]['diners']):
                bot.memory['lunch'][lunch_owner_nickname]['diners'].append(nick_to_add)
                # Count down limit
                bot.memory['lunch'][lunch_owner_nickname]['limit'] = limit - 1

            # Notice to dinner and lunch's owner
            bot.msg(lunch_owner_nickname, MESSAGES['added_lunch'].format(
                nick=nick_to_add,
                menu=bot.memory['lunch'][lunch_owner_nickname]['menu']))
            bot.msg(nick_to_add, MESSAGES['added_lunch'].format(
                nick=nick_to_add,
                menu=bot.memory['lunch'][lunch_owner_nickname]['menu']))

            # Announce the lunch is closed to channels, one time
            if limit_enable and ((limit - 1) < 1):
                for channel in bot.channels:
                    bot.msg(channel, MESSAGES['no_more_limit'].format(nick=lunch_owner_nickname))
            return
    # Storage lunch do not exits
    bot.msg(trigger.nick, MESSAGES['unexisting_menu'].format(nick=lunch_owner_nickname))
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

    if bot.memory.contains('lunch'):
        # Storage lunch exists, do not need to create
        if trigger.nick in bot.memory['lunch'].keys():
            # Lunch for nick exists
            menu = bot.memory['lunch'][trigger.nick]['menu']
            price = total_price / len(bot.memory['lunch'][trigger.nick]['diners'])
            price = price.quantize(TWOPLACES)
            message = MESSAGES['price_lunch'].format(nick=trigger.nick, menu=menu, price=price)
            for nick in bot.memory['lunch'][trigger.nick]['diners']:
                bot.msg(nick, message)
            return
    # Storage lunch do not exits
    bot.msg(trigger.nick, MESSAGES['create_lunch'])
    return


@willie.module.commands('lunch_detail')
@willie.module.example('.lunch_detail')
def lunch_detail(bot, trigger):
    """
    Return detail about your lunch: .lunch_detail
    """
    if bot.memory.contains('lunch'):
        # Storage lunch exists, do not need to create
        if trigger.nick in bot.memory['lunch'].keys():
            # Lunch for nick exists
            bot.msg(trigger.nick, 'Menu: {}'.format(bot.memory['lunch'][trigger.nick]['menu']))
            bot.msg(trigger.nick, 'Date: {}'.format(bot.memory['lunch'][trigger.nick]['date']))
            if bot.memory['lunch'][trigger.nick]['limit_enable']:
                limit = bot.memory['lunch'][trigger.nick]['limit']
                bot.msg(trigger.nick, 'Vacants: {}'.format(limit))

            diners = bot.memory['lunch'][trigger.nick]['diners']
            bot.msg(trigger.nick, 'Diners: {}'.format(', '.join([nick for nick in diners])))
            return
    # Storage lunch do not exits
    bot.msg(trigger.nick, MESSAGES['create_lunch'])
    return


@willie.module.commands('lunch_list')
@willie.module.example('.lunch_list')
def lunch_list(bot, trigger):
    """
    Return a list of all lunches
    """
    if bot.memory.contains('lunch'):
        # Storage lunch exists, do not need to create
        bot.msg(trigger.nick, MESSAGES['list_lunch'])
        for nick, menu in bot.memory['lunch'].items():
            limit = "-"
            if bot.memory['lunch'][nick]['limit_enable']:
                limit = bot.memory['lunch'][nick]['limit']
            bot.msg(trigger.nick, MESSAGES['list_lunch_item'].format(
                menu=menu['menu'], owner=nick, vacants=limit))
        return
    # Storage lunch do not exits
    bot.msg(trigger.nick, MESSAGES['no_lunches'])
    return
