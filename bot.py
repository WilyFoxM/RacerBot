import time
import telebot
import random
import sqlite3
import threading
import matplotlib.pyplot as plt
import io
import numpy as np

ctx_token = ''

with open('ctx.txt', 'r') as f:
    ctx_token = str(f.readline())

TOKEN = ctx_token

bot = telebot.TeleBot(TOKEN)

con = sqlite3.connect('users.db', check_same_thread=False)
cur = con.cursor()

# def prepare_db():
# 	cur.execute('''CREATE TABLE users
#             		(username text, userid integer, rank text, total_games integer, wins integer, coins integer, skin text, secret_title text, unlocked_skins text, unlocked_ranks text, place_tile text, unlocked_tiles text, flag text, unlocked_flags text, xp int, xp_data text)
#                 ''')
# prepare_db()
# con.commit()

# cur.execute('''
# 		ALTER TABLE users ADD COLUMN xp_data text DEFAULT '0'
# 	''')
# con.commit()

# cur.execute('''
# 		ALTER TABLE users ADD COLUMN unlocked_flags text DEFAULT "🏁"
# 	''')

turn_map = ['0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

# ➖〰️

shop_dict = {
    'skins': {
        '150': {
            'surfer_purple': ['🏄‍♀', 150],
            'surfer_yellow': ['🏄‍', 150],
            'surfer_green': ['🏄‍♂', 150],
        },
        '200': {
            'basketball_red': ['⛹‍♀', 200],
            'basketball_white': ['⛹️', 200],
            'basketball_blue': ['⛹‍♂', 200],
        },
        '400': {
            'moto_red': ['🚴‍♀', 400],
            'moto_white': ['🚴', 400],
            'moto_blue': ['🚴‍♂', 400],
        },
        '500': {
            'mermaid_pink': ['🧞‍♀', 500],
            'mermaid_cian': ['🧞‍♂', 500],
            'mermaid_blue': ['🧞', 500],
        }
    },
    'flags': {
        '300': {
            'red': ['🚩', 300]
        },
        '700': {
            'finish': ['🏁', 700]
        },
        '1000': {
            'double': ['🇳🇵', 1000]
        },
        '1200': {
            'black': ['🏴', 1200]
        },
        '1500': {
            'pirate': ['🏴‍☠️', 1500]
        }

    }
}

place_immutable = ['🏁', '_', '_', '_', '_', '_', '_', '_', '_', '_']
val = ''
inRace = False

servers = {}


def inc_total_games(user_id):
    cur.execute('SELECT total_games FROM users WHERE userid = (?)', (user_id,))
    prev_total = cur.fetchone()[0]
    prev_total += 1

    cur.execute('UPDATE users SET total_games=(?) WHERE userid=(?)', (prev_total, user_id))
    con.commit()


def inc_wins(user_id):
    cur.execute('SELECT wins FROM users WHERE userid = (?)', (user_id,))
    prev_wins = cur.fetchone()[0]
    prev_wins += 1

    cur.execute('UPDATE users SET wins=(?) WHERE userid=(?)', (prev_wins, user_id))
    con.commit()


def inc_coins(user_id, amount):
    cur.execute('SELECT coins FROM users WHERE userid = (?)', (user_id,))
    prev_coins = cur.fetchone()[0]
    prev_coins += int(amount)

    cur.execute('UPDATE users SET coins=(?) WHERE userid=(?)', (prev_coins, user_id))
    con.commit()


def inc_xp(user_id, amount):
    cur.execute('SELECT xp FROM users WHERE userid = (?)', (user_id,))
    prev_xp = cur.fetchone()[0]
    prev_xp += int(amount)

    cur.execute('UPDATE users SET xp=(?) WHERE userid=(?)', (prev_xp, user_id))
    con.commit()


def dec_coins(user_id, amount):
    cur.execute('SELECT coins FROM users WHERE userid = (?)', (user_id,))
    prev_coins = cur.fetchone()[0]
    prev_coins -= amount

    cur.execute('UPDATE users SET coins=(?) WHERE userid=(?)', (prev_coins, user_id))
    con.commit()


def dec_xp(user_id, amount):
    cur.execute('SELECT xp FROM users WHERE userid = (?)', (user_id,))
    xp = cur.fetchone()[0]
    xp -= int(amount)
    if xp < 0:
        xp = 0

    cur.execute('UPDATE users SET xp=(?) WHERE userid=(?)', (xp, user_id))
    con.commit()


def add_skin(user_id, user_skin):
    cur.execute('SELECT unlocked_skins FROM users WHERE userid = (?)', (user_id,))
    prev_skins = cur.fetchone()[0]
    prev_skins = prev_skins + ' ' + str(user_skin).strip()

    cur.execute('UPDATE users SET unlocked_skins=(?) WHERE userid=(?)', (prev_skins, user_id))
    con.commit()


def add_rank(user_id, user_rank):
    cur.execute('SELECT unlocked_ranks FROM users WHERE userid = (?)', (user_id,))
    prev_ranks = cur.fetchone()[0]
    prev_ranks = prev_ranks + '#' + str(user_rank).strip()

    cur.execute('UPDATE users SET unlocked_ranks=(?) WHERE userid=(?)', (prev_ranks, user_id))
    con.commit()


def add_flag(user_id, user_flag):
    cur.execute('SELECT unlocked_flags FROM users WHERE userid = (?)', (user_id,))
    prev_flags = cur.fetchone()[0]
    prev_flags = prev_flags + ' ' + str(user_flag).strip()

    cur.execute('UPDATE users SET unlocked_flags=(?) WHERE userid=(?)', (prev_flags, user_id))
    con.commit()


def add_wins(id, amount):
    cur.execute('SELECT wins FROM users WHERE userid = (?)', (id,))
    prev_wins = cur.fetchone()[0]
    prev_wins = int(prev_wins) + int(amount)

    cur.execute('UPDATE users SET wins=(?) WHERE userid=(?)', (prev_wins, id))
    con.commit()


def set_skin(id, skin):
    skin = str(skin).strip()
    cur.execute('UPDATE users SET skin=(?) WHERE userid=(?)', (skin, id))
    con.commit()


def add_xp_record(id):
    cur.execute('SELECT xp FROM users WHERE userid = (?)', (id,))
    xp_value = cur.fetchone()[0]

    cur.execute('SELECT xp_data FROM users WHERE userid = (?)', (id,))
    prev_xps = cur.fetchone()[0]
    prev_xps = str(prev_xps).strip() + ' ' + str(xp_value).strip()

    cur.execute('UPDATE users SET xp_data=(?) WHERE userid=(?)', (prev_xps, id))
    con.commit()


def set_secret_title(id, ico):
    ico = str(ico).strip()
    cur.execute('UPDATE users SET secret_title=(?) WHERE userid=(?)', (ico, id))
    con.commit()


def set_rank(id, rank):
    rank = str(rank).strip()
    cur.execute('UPDATE users SET rank=(?) WHERE userid=(?)', (rank, id))
    con.commit()


def set_flag(id, flag):
    flag = str(flag).strip()
    cur.execute('UPDATE users SET flag=(?) WHERE userid=(?)', (flag, id))
    con.commit()


def create_user(message):
    cur.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (
        message.from_user.username, message.from_user.id, 'НОВИЧОК', 0, 0, 0, '🏃', '👤', '🏃', '👤 НОВИЧОК', '_', '_',
        '🏳️', '🏳️', 0, '0'))
    con.commit()
    cur.execute('SELECT * FROM users WHERE userid = (?)', (message.from_user.id,))
    user = cur.fetchone()
    return user


def check_user_by_name(name):
    cur.execute('SELECT * FROM users WHERE username = (?)', (name,))
    user = cur.fetchone()
    ret = ''
    if not user:
        ret = False
    else:
        ret = user

    if not ret:
        return ret
    if user[4] >= 70:
        rank = '🐲 Одарённый'
        player_ranks = get_ranks(user[1])
        if rank not in player_ranks.split('#'):
            add_rank(user[1], '🐲 Одарённый')
    if user[4] >= 60:
        rank = '👺 Демон'
        player_ranks = get_ranks(user[1])
        if rank not in player_ranks.split('#'):
            add_rank(user[1], '👺 Демон')
    if user[4] >= 50:
        rank = '🥷 Скрытный'
        player_ranks = get_ranks(user[1])
        if rank not in player_ranks.split('#'):
            add_rank(user[1], '🥷 Скрытный')
    if user[4] >= 40:
        rank = '🤹 Ловкач'
        player_ranks = get_ranks(user[1])
        if rank not in player_ranks.split('#'):
            add_rank(user[1], '🤹 Ловкач')
    if user[4] >= 30:
        rank = '🧸 Плюшевый'
        player_ranks = get_ranks(user[1])
        if rank not in player_ranks.split('#'):
            add_rank(user[1], '🧸 Плюшевый')
    if user[4] >= 20:
        rank = '🗿 Путник'
        player_ranks = get_ranks(user[1])
        if rank not in player_ranks.split('#'):
            add_rank(user[1], '🗿 Путник')
    if user[4] >= 10:
        rank = '🧟‍♂ Мелочь'
        player_ranks = get_ranks(user[1])
        if rank not in player_ranks.split('#'):
            add_rank(user[1], '🧟‍♂ Мелочь')

    return ret


def check_user(message):
    cur.execute('SELECT * FROM users WHERE userid = (?)', (message.from_user.id,))
    user = cur.fetchone()

    ret = ''
    if not user:
        ret = create_user(message)
        user = ret
    else:
        ret = user

    if not ret:
        return ret
    if int(user[4]) >= 70:
        rank = '🐲 Одарённый'
        player_ranks = get_ranks(user[1])
        if rank not in player_ranks.split('#'):
            add_rank(user[1], '🐲 Одарённый')
    if user[4] >= 60:
        rank = '👺 Демон'
        player_ranks = get_ranks(user[1])
        if rank not in player_ranks.split('#'):
            add_rank(user[1], '👺 Демон')
    if user[4] >= 50:
        rank = '🥷 Скрытный'
        player_ranks = get_ranks(user[1])
        if rank not in player_ranks.split('#'):
            add_rank(user[1], '🥷 Скрытный')
    if user[4] >= 40:
        rank = '🤹 Ловкач'
        player_ranks = get_ranks(user[1])
        if rank not in player_ranks.split('#'):
            add_rank(user[1], '🤹 Ловкач')
    if user[4] >= 30:
        rank = '🧸 Плюшевый'
        player_ranks = get_ranks(user[1])
        if rank not in player_ranks.split('#'):
            add_rank(user[1], '🧸 Плюшевый')
    if user[4] >= 20:
        rank = '🗿 Путник'
        player_ranks = get_ranks(user[1])
        if rank not in player_ranks.split('#'):
            add_rank(user[1], '🗿 Путник')
    if user[4] >= 10:
        rank = '🧟‍♂ Мелочь'
        player_ranks = get_ranks(user[1])
        if rank not in player_ranks.split('#'):
            add_rank(user[1], '🧟‍♂ Мелочь')

    return ret


def get_skins(id):
    cur.execute('SELECT unlocked_skins FROM users WHERE userid = (?)', (id,))
    skins = cur.fetchone()[0]
    return skins


def get_ranks(id):
    cur.execute('SELECT unlocked_ranks FROM users WHERE userid = (?)', (id,))
    skins = cur.fetchone()[0]
    return skins


def get_flags(id):
    cur.execute('SELECT unlocked_flags FROM users WHERE userid = (?)', (id,))
    flags = cur.fetchone()[0]
    return flags


def get_skin(id):
    cur.execute('SELECT skin FROM users WHERE userid = (?)', (id,))
    skin = cur.fetchone()[0]
    return skin


def get_tile(id):
    cur.execute('SELECT place_tile FROM users WHERE userid = (?)', (id,))
    tile = cur.fetchone()[0]
    return tile


def get_ico(id):
    cur.execute('SELECT secret_title FROM users WHERE userid = (?)', (id,))
    ico = cur.fetchone()[0]
    return ico


def get_flag(id):
    cur.execute('SELECT flag FROM users WHERE userid = (?)', (id,))
    flag = cur.fetchone()[0]
    return flag


def get_money(id):
    cur.execute('SELECT coins FROM users WHERE userid = (?)', (id,))
    coins = cur.fetchone()[0]
    return coins


def get_xp(id):
    cur.execute('SELECT xp FROM users WHERE userid = (?)', (id,))
    xp = cur.fetchone()[0]
    return xp


def make_plot(data, message, legend = '', ):
    dataY = list(map(int, data))
    dataX = np.array(range(1, len(dataY) + 1))

    user_figure, user_plot = plt.subplots(layout='constrained')
    if len(legend) > 0:
        user_plot.plot(dataX, dataY, **{'marker': 'o'}, label=str(legend))
    else:
        user_plot.plot(dataX, dataY, **{'marker': 'o'})
    user_plot.legend()
    user_plot.set_facecolor((0.1, 0.1, 0.1))
    user_plot.tick_params(axis='x', colors='white')
    user_plot.tick_params(axis='y', colors='white')
    fig = user_figure
    fig.patch.set_facecolor((0.1, 0.1, 0.1))

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    del_message_markaup = telebot.types.InlineKeyboardMarkup(row_width=1)
    del_message_markaup_item = telebot.types.InlineKeyboardButton('❌', callback_data='del_message ' + str(
        message.from_user.id) + ' ' + str(message.id))
    del_message_markaup.add(del_message_markaup_item)
    bot.send_photo(message.chat.id, buf, reply_markup=del_message_markaup)


@bot.callback_query_handler(func=lambda call: True)
def callback_race(call):
    check_user(call)
    global servers
    if call.data.split(' ')[0] == 'join':
        for i in range(len(servers[call.data.split(' ')[1]]['players'])):
            if call.from_user.username == servers[call.data.split(' ')[1]]['players'][i]['name']:
                return
        if len(servers[call.data.split(' ')[1]]['players']) >= 10:
            return
        if call.from_user.username == None:
            return
        if call.from_user.username == '':
            return
        if call.data.split(' ')[1] not in servers:
            return
        servers[call.data.split(' ')[1]]['players'].append(
            {
                'id': call.from_user.id,
                'name': call.from_user.username,
                'idx': len(place_immutable) - 1,
                'skin': get_skin(call.from_user.id),
                'turn': 0,
                'place': [] + place_immutable,
                'place_tile': get_tile(call.from_user.id),
                'flag': get_flag(call.from_user.id),
                'ico': get_ico(call.from_user.id),
                 'win_idx': 100,
                'medal': '',
                'hasBoost': False,
                'boost': 0,
                'stunned': False
            }
        )
        return
    elif call.data.split(' ')[0] == 'buy':
        user = check_user(call)
        cost = shop_dict['skins'][call.data.split(' ')[1]][call.data.split(' ')[2]][1]
        player_money = get_money(call.from_user.id)
        skin = shop_dict['skins'][call.data.split(' ')[1]][call.data.split(' ')[2]][0]
        player_skins = get_skins(call.from_user.id)
        if skin in player_skins.split(' '):
            bot.send_message(call.message.chat.id, '@' + user[0] + ', у вас уже есть скин -> ' + str(skin))
            return
        if cost > player_money:
            bot.send_message(call.message.chat.id, '@' + user[0] + ', у вас недостаточно денег на скин -> ' + str(skin))
            return
        dec_coins(call.from_user.id, cost)
        add_skin(call.from_user.id, skin)
        bot.send_message(call.message.chat.id, '@' + user[0] + ', вы купили скин -> ' + str(skin))
        return
    elif call.data.split(' ')[0] == 'buy_flag':
        user = check_user(call)
        cost = shop_dict['flags'][call.data.split(' ')[1]][call.data.split(' ')[2]][1]
        player_money = get_money(call.from_user.id)
        flag = shop_dict['flags'][call.data.split(' ')[1]][call.data.split(' ')[2]][0]
        player_flags = get_flags(call.from_user.id)
        if flag in player_flags.split(' '):
            bot.send_message(call.message.chat.id, '@' + user[0] + ', у вас уже есть флаг -> ' + str(flag))
            return
        if cost > player_money:
            bot.send_message(call.message.chat.id, '@' + user[0] + ', у вас недостаточно денег на флаг -> ' + str(flag))
            return
        dec_coins(call.from_user.id, cost)
        add_flag(call.from_user.id, flag)
        bot.send_message(call.message.chat.id, '@' + user[0] + ', вы купили флаг -> ' + str(flag))
        return
    elif call.data.split(' ')[0] == 'set':
        caller_id = call.data.split(' ')[2]
        if str(call.from_user.id) != caller_id:
            return
        user = check_user(call)
        skin = call.data.split(' ')[1]
        set_skin(call.from_user.id, skin)
        bot.send_message(call.message.chat.id, '@' + user[0] + ', вы установили скин -> ' + str(skin))
        return
    elif call.data.split(' ')[0] == 'set_rank':
        caller_id = call.data.split(' ')[3]
        if str(call.from_user.id) != caller_id:
            return
        user = check_user(call)
        rank = str(call.data.split(' ')[2]).strip()
        ico = str(call.data.split(' ')[1]).strip()
        set_rank(call.from_user.id, rank)
        set_secret_title(call.from_user.id, ico)
        bot.send_message(call.message.chat.id, '@' + user[0] + ', вы установили ранг -> ' + str(rank))
        return
    elif call.data.split(' ')[0] == 'set_flag':
        caller_id = call.data.split(' ')[2]
        if str(call.from_user.id) != caller_id:
            return
        user = check_user(call)
        flag = call.data.split(' ')[1]
        set_flag(call.from_user.id, flag)
        bot.send_message(call.message.chat.id, '@' + user[0] + ', вы установили флаг -> ' + str(flag))
        return
    elif call.data.split(' ')[0] == 'del_message':
        caller_id = call.data.split(' ')[1]
        init_message_id = call.data.split(' ')[2]
        if str(call.from_user.id) != caller_id:
            return
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.delete_message(call.message.chat.id, init_message_id)
        return
    elif call.data.split(' ')[0] == 'add_box':
        if servers[str(call.message.chat.id)]['hasBox']:
            return
        servers[str(call.message.chat.id)]['hasBox'] = True
        caller_id = call.data.split(' ')[1]
        for i in range(len(servers[str(call.message.chat.id)]['players'])):
            if str(servers[str(call.message.chat.id)]['players'][i]['id']) == str(caller_id):
                servers[str(call.message.chat.id)]['players'][i]['hasBoost'] = True
        return


def game(message):
    global servers

    chatid = str(message.chat.id)
    if chatid in servers:
        return

    servers[chatid] = {}
    servers[chatid]['inRace'] = True
    servers[chatid]['players'] = []

    tsec = 59

    join_race_markaup = telebot.types.InlineKeyboardMarkup(row_width=1)
    join_race_markaup_item = telebot.types.InlineKeyboardButton('Присоединиться',
                                                                callback_data='join ' + str(message.chat.id))
    join_race_markaup.add(join_race_markaup_item)

    msg = bot.send_message(message.chat.id, 'Времени отсалось: {} секунд\n\nИгроков: 0'.format(str(tsec)),
                           reply_markup=join_race_markaup)

    bot.pin_chat_message(msg.chat.id, msg.message_id, disable_notification=True)

    while tsec > 0:
        tsec -= 1
        init_string = 'Времени отсалось: {} секунд\n\nИгроков: {}'.format(str(tsec),
                                                                          str(len(servers[chatid]['players'])))
        if divmod(tsec, 10)[1] == 0:
            bot.edit_message_text(init_string, msg.chat.id, msg.message_id, reply_markup=join_race_markaup)
        time.sleep(1)

    inRace = True
    race_over = False

    turn_tracker = []

    if len(servers[chatid]['players']) < 1:
        return

    for i in range(len(servers[chatid]['players'])):
        inc_total_games(servers[chatid]['players'][i]['id'])

    win_msg = ''

    if len(message.text.split(' ')) > 1:
        turn = int(message.text.split(' ')[1])
        init_turn = int(message.text.split(' ')[1])
        winners_cup = 3
        winners = []
        if len(servers[chatid]['players']) < 3:
            winners_cup = len(servers[chatid]['players'])

        if turn > 5 or turn < 1:
            return

        for i in range(len(servers[chatid]['players'])):
            servers[chatid]['players'][i]['turn'] = turn

        while not race_over:
            final_str = ''
            place_local = ['🏁', '_', '_', '_', '_', '_', '_', '_', '_', '_']

            for i in range(len(servers[chatid]['players'])):
                if servers[chatid]['players'][i]['idx'] <= 0:
                    if servers[chatid]['players'][i]['turn'] == 1:
                        if len(winners) >= winners_cup:
                            race_over = True
                            inRace = False
                            servers[chatid]['inRace'] = False

                            dec_xp_amount = random.randint(5, 8)
                            xp = random.randint(10, 20) * init_turn
                            coins = random.randint(5, 10) * init_turn

                            inc_xp(winners[0]['id'], xp)

                            win_txt = 'Победители:\n'
                            for j in range(len(winners)):
                                inc_coins(winners[j]['id'], coins)
                                inc_wins(winners[j]['id'])
                                win_txt += '    ' + str(j + 1) + '. ' + str(winners[j]['name']) + ' ' + str(winners[j]['medal']) + '\n'

                            win_txt += '\nЗаработали по ' + str(coins) + ' монет'

                            win_msg = bot.send_message(message.chat.id, win_txt)

                            for j in range(len(servers[chatid]['players'])):
                                if servers[chatid]['players'][i] != winners[0]:
                                    dec_xp(servers[chatid]['players'][i]['id'], dec_xp_amount)

                            for k in range(len(servers[chatid]['players'])):
                                add_xp_record(servers[chatid]['players'][k]['id'])
                            break
                        else:
                            if servers[chatid]['players'][i] not in winners:
                                winners.append(servers[chatid]['players'][i])
                                servers[chatid]['players'][i]['winner_idx'] = len(winners)
                                ic = ''
                                if servers[chatid]['players'][i]['winner_idx'] == 1:
                                    ic = '🥇'
                                elif servers[chatid]['players'][i]['winner_idx'] == 2:
                                    ic = '🥈'
                                elif servers[chatid]['players'][i]['winner_idx'] == 3:
                                    ic = '🥉'
                                servers[chatid]['players'][i]['medal'] = ic
                    else:
                        if servers[chatid]['players'][i] not in winners:
                            servers[chatid]['players'][i]['turn'] -= 1
                            servers[chatid]['players'][i]['idx'] = len(place_local) - 1

            if inRace:
                for i in range(len(servers[chatid]['players'])):

                    if servers[chatid]['players'][i] not in winners:
                        servers[chatid]['players'][i]['place'] = [servers[chatid]['players'][i]['place_tile']] * len(
                            place_local)

                        if servers[chatid]['players'][i]['turn'] != 1:
                            servers[chatid]['players'][i]['place'][0] = str(turn_map[servers[chatid]['players'][i]['turn']])
                        else:
                            servers[chatid]['players'][i]['place'][0] = servers[chatid]['players'][i]['flag']

                        servers[chatid]['players'][i]['place'][servers[chatid]['players'][i]['idx']] = servers[chatid]['players'][i]['skin']
                        race = val.join(servers[chatid]['players'][i]['place'])
                        final_str += race + ' <- ' + '@' + servers[chatid]['players'][i]['name'][
                                                           0:7] + '... ' + str(
                            servers[chatid]['players'][i]['ico']) + '\n'
                    else:
                        ic = ''
                        if servers[chatid]['players'][i]['winner_idx'] == 1:
                            ic = '🥇'
                        elif servers[chatid]['players'][i]['winner_idx'] == 2:
                            ic = '🥈'
                        elif servers[chatid]['players'][i]['winner_idx'] == 3:
                            ic = '🥉'
                        servers[chatid]['players'][i]['place'][0] = ic

                        race = val.join(servers[chatid]['players'][i]['place'])
                        final_str += race + ' <- ' + '@' + servers[chatid]['players'][i]['name'][0:7] + '... ' + str(
                            servers[chatid]['players'][i]['ico']) + '\n'

                rand = random.randint(0, len(servers[chatid]['players']) - 1)
                iteration = 0

                while servers[chatid]['players'][rand] in winners:
                    if iteration >= 100000:
                        race_over = True
                        inRace = False
                        servers[chatid]['inRace'] = False

                        dec_xp_amount = random.randint(5, 8)
                        xp = random.randint(10, 20) * init_turn
                        coins = random.randint(5, 10) * init_turn

                        inc_xp(winners[0]['id'], xp)

                        win_txt = 'Победители:\n'
                        for j in range(len(winners)):
                            inc_coins(winners[j]['id'], coins)
                            inc_wins(winners[j]['id'])
                            win_txt += '    ' + str(j + 1) + '. ' + str(winners[j]['name']) + ' ' + str(
                                winners[j]['medal']) + '\n'

                        win_txt += '\nЗаработали по ' + str(coins) + ' монет'

                        win_msg = bot.send_message(message.chat.id, win_txt)

                        for j in range(len(servers[chatid]['players'])):
                            if servers[chatid]['players'][i] != winners[0]:
                                dec_xp(servers[chatid]['players'][i]['id'], dec_xp_amount)

                        for k in range(len(servers[chatid]['players'])):
                            add_xp_record(servers[chatid]['players'][k]['id'])
                        break
                    else:
                        iteration += 1
                        rand = random.randint(0, len(servers[chatid]['players']) - 1)

                if chatid in servers:
                    servers[chatid]['players'][rand]['idx'] -= 1
                    turn_tracker.append(rand)
                    bot.edit_message_text(final_str, msg.chat.id, msg.message_id)
                    time.sleep(3)

    else:
        while not race_over:
            final_str = ''
            place_local = ['🏁', '_', '_', '_', '_', '_', '_', '_', '_', '_']

            for i in range(len(servers[chatid]['players'])):
                if servers[chatid]['players'][i]['idx'] <= 0:
                    race_over = True
                    inRace = False

                    inc_wins(servers[chatid]['players'][i]['id'])
                    coins = random.randint(5, 10)
                    xp = random.randint(10, 20)
                    inc_xp(servers[chatid]['players'][i]['id'], xp)
                    inc_coins(servers[chatid]['players'][i]['id'], coins)
                    win_msg = bot.send_message(message.chat.id, servers[chatid]['players'][i][
                        'name'] + ' выиграл! И заработал {} монет!'.format(coins))

                    dec_xp_amount = random.randint(5, 8)
                    winner = message.chat.id, servers[chatid]['players'][i]['id']
                    for i in range(len(servers[chatid]['players'])):
                        if servers[chatid]['players'][i]['id'] != winner:
                            dec_xp(servers[chatid]['players'][i]['id'], dec_xp_amount)

                    servers.pop(chatid, None)
                    break;

            if inRace:
                for i in range(len(servers[chatid]['players'])):
                    servers[chatid]['players'][i]['place'] = [servers[chatid]['players'][i]['place_tile']] * len(
                        place_local)
                    servers[chatid]['players'][i]['place'][0] = servers[chatid]['players'][i]['flag']
                    servers[chatid]['players'][i]['place'][servers[chatid]['players'][i]['idx']] = \
                        servers[chatid]['players'][i]['skin']
                    race = val.join(servers[chatid]['players'][i]['place'])
                    final_str += race + ' <- ' + '@' + servers[chatid]['players'][i]['name'][0:7] + '... ' + str(
                        str(servers[chatid]['players'][i]['ico'])) + '\n'

                rand = random.randint(0, len(servers[chatid]['players']) - 1)
                servers[chatid]['players'][rand]['idx'] -= 1
                turn_tracker.append(rand)
                bot.edit_message_text(final_str, msg.chat.id, msg.message_id)
                time.sleep(2)

    servers.pop(chatid, None)
    make_plot(turn_tracker, message, 'Ходы игроков')
    time.sleep(15)
    bot.delete_message(msg.chat.id, msg.message_id)
    bot.delete_message(msg.chat.id, message.message_id)
    bot.delete_message(msg.chat.id, win_msg.message_id)

    return


def arcade_game(message):
    global servers

    chatid = str(message.chat.id)
    if chatid in servers:
        return

    servers[chatid] = {}
    servers[chatid]['inRace'] = True
    servers[chatid]['hasBox'] = False
    servers[chatid]['players'] = []

    # servers[chatid]['players'].append(
    #     {
    #         'id': 0,
    #         'name': 'Robot',
    #         'idx': len(place_immutable) - 1,
    #         'skin': '🤖',
    #         'turn': 0,
    #         'place': [] + place_immutable,
    #         'place_tile': '_',
    #         'flag': '🇮🇨',
    #         'ico': '🤖',
    #         'win_idx': 100,
    #         'medal': '',
    #         'hasBoost': False,
    #         'boost': 0,
    #         'stunned': False
    #     }
    # )

    tsec = 59

    join_race_markaup = telebot.types.InlineKeyboardMarkup(row_width=1)
    join_race_markaup_item = telebot.types.InlineKeyboardButton('Присоединиться',
                                                                callback_data='join ' + str(message.chat.id))
    join_race_markaup.add(join_race_markaup_item)

    msg = bot.send_message(message.chat.id, 'Времени отсалось: {} секунд\n\nИгроков: 0'.format(str(tsec)),
                           reply_markup=join_race_markaup)

    bot.pin_chat_message(msg.chat.id, msg.message_id, disable_notification=True)

    while tsec > 0:
        tsec -= 1
        init_string = 'Времени отсалось: {} секунд\n\nИгроков: {}'.format(str(tsec),
                                                                          str(len(servers[chatid]['players'])))
        if divmod(tsec, 10)[1] == 0:
            bot.edit_message_text(init_string, msg.chat.id, msg.message_id, reply_markup=join_race_markaup)
        time.sleep(1)

    inRace = True
    race_over = False

    if len(servers[chatid]['players']) < 1:
        return

    # for i in range(len(servers[chatid]['players'])):
        # inc_total_games(servers[chatid]['players'][i]['id'])

    win_msg = ''

    if len(message.text.split(' ')) > 1:
        turn = int(message.text.split(' ')[1])
        init_turn = int(message.text.split(' ')[1])
        winners_cup = 3
        winners = []
        if len(servers[chatid]['players']) < 3:
            winners_cup = len(servers[chatid]['players'])

        if turn > 5 or turn < 1:
            return

        for i in range(len(servers[chatid]['players'])):
            servers[chatid]['players'][i]['turn'] = turn

        while not race_over:
            final_str = ''
            place_local = ['🏁', '_', '_', '_', '_', '_', '_', '_', '_', '_']

            for i in range(len(servers[chatid]['players'])):
                if servers[chatid]['players'][i]['idx'] <= 0:
                    if servers[chatid]['players'][i]['turn'] == 1:
                        if len(winners) >= winners_cup:
                            race_over = True
                            inRace = False
                            servers[chatid]['inRace'] = False

                            # dec_xp_amount = random.randint(5, 8)
                            # xp = random.randint(10, 20) * init_turn
                            coins = random.randint(5, 10) * init_turn

                            # inc_xp(winners[0]['id'], xp)

                            win_txt = 'Победители:\n'
                            for j in range(len(winners)):
                                # inc_coins(winners[j]['id'], coins)
                                # inc_wins(winners[j]['id'])
                                win_txt += '    ' + str(j + 1) + '. ' + str(winners[j]['name']) + ' ' + str(winners[j]['medal']) + '\n'

                            win_txt += '\nЗаработали по ' + str(coins) + ' монет'

                            win_msg = bot.send_message(message.chat.id, win_txt)

                            # for j in range(len(servers[chatid]['players'])):
                            #     if servers[chatid]['players'][i] != winners[0]:
                            #         dec_xp(servers[chatid]['players'][i]['id'], dec_xp_amount)

                            # for k in range(len(servers[chatid]['players'])):
                            #     add_xp_record(servers[chatid]['players'][k]['id'])
                            break
                        else:
                            if servers[chatid]['players'][i] not in winners:
                                winners.append(servers[chatid]['players'][i])
                                servers[chatid]['players'][i]['winner_idx'] = len(winners)
                                ic = ''
                                if servers[chatid]['players'][i]['winner_idx'] == 1:
                                    ic = '🥇'
                                elif servers[chatid]['players'][i]['winner_idx'] == 2:
                                    ic = '🥈'
                                elif servers[chatid]['players'][i]['winner_idx'] == 3:
                                    ic = '🥉'
                                servers[chatid]['players'][i]['medal'] = ic
                    else:
                        if servers[chatid]['players'][i] not in winners:
                            servers[chatid]['players'][i]['turn'] -= 1
                            servers[chatid]['players'][i]['idx'] = len(place_local) - 1

            if inRace:
                for i in range(len(servers[chatid]['players'])):

                    if servers[chatid]['players'][i] not in winners:
                        servers[chatid]['players'][i]['place'] = [servers[chatid]['players'][i]['place_tile']] * len(
                            place_local)

                        if servers[chatid]['players'][i]['turn'] != 1:
                            servers[chatid]['players'][i]['place'][0] = str(turn_map[servers[chatid]['players'][i]['turn']])
                        else:
                            servers[chatid]['players'][i]['place'][0] = servers[chatid]['players'][i]['flag']

                        if servers[chatid]['players'][i]['stunned']:
                            servers[chatid]['players'][i]['place'][servers[chatid]['players'][i]['idx']] = '🧊'
                            servers[chatid]['players'][i]['stunned'] = False
                        else:
                            servers[chatid]['players'][i]['place'][servers[chatid]['players'][i]['idx']] = servers[chatid]['players'][i]['skin']

                        race = val.join(servers[chatid]['players'][i]['place'])
                        final_str += race + ' <- ' + '@' + servers[chatid]['players'][i]['name'][
                                                           0:7] + '... ' + str(
                            servers[chatid]['players'][i]['ico']) + '\n'
                    else:
                        ic = ''
                        if servers[chatid]['players'][i]['winner_idx'] == 1:
                            ic = '🥇'
                        elif servers[chatid]['players'][i]['winner_idx'] == 2:
                            ic = '🥈'
                        elif servers[chatid]['players'][i]['winner_idx'] == 3:
                            ic = '🥉'
                        servers[chatid]['players'][i]['place'][0] = ic

                        race = val.join(servers[chatid]['players'][i]['place'])
                        final_str += race + ' <- ' + '@' + servers[chatid]['players'][i]['name'][0:7] + '... ' + str(
                            servers[chatid]['players'][i]['ico']) + '\n'

                rand = random.randint(0, len(servers[chatid]['players']) - 1)
                iteration = 0

                while servers[chatid]['players'][rand] in winners:
                    if iteration >= 100000:
                        race_over = True
                        inRace = False
                        servers[chatid]['inRace'] = False

                        dec_xp_amount = random.randint(5, 8)
                        xp = random.randint(10, 20) * init_turn
                        coins = random.randint(5, 10) * init_turn

                        inc_xp(winners[0]['id'], xp)

                        win_txt = 'Победители:\n'
                        for j in range(len(winners)):
                            inc_coins(winners[j]['id'], coins)
                            inc_wins(winners[j]['id'])
                            win_txt += '    ' + str(j + 1) + '. ' + str(winners[j]['name']) + ' ' + str(
                                winners[j]['medal']) + '\n'

                        win_txt += '\nЗаработали по ' + str(coins) + ' монет'

                        win_msg = bot.send_message(message.chat.id, win_txt)

                        for j in range(len(servers[chatid]['players'])):
                            if servers[chatid]['players'][i] != winners[0]:
                                dec_xp(servers[chatid]['players'][i]['id'], dec_xp_amount)

                        for k in range(len(servers[chatid]['players'])):
                            add_xp_record(servers[chatid]['players'][k]['id'])
                        break
                    else:
                        iteration += 1
                        rand = random.randint(0, len(servers[chatid]['players']) - 1)

                if chatid in servers:
                    if servers[chatid]['players'][rand]['hasBoost']:
                        servers[chatid]['players'][rand]['hasBoost'] = False
                        randval = random.randint(0, 100)
                        if randval < 50:
                            servers[chatid]['players'][rand]['idx'] -= 3
                        else:
                            servers[chatid]['players'][rand]['idx'] -= 0
                            servers[chatid]['players'][rand]['stunned'] = True
                    else:
                        servers[chatid]['players'][rand]['idx'] -= 1

                    box_markup = telebot.types.InlineKeyboardMarkup(row_width=1)
                    box_markup_item = ''
                    key_value = random.randint(0, 10)

                    if key_value in range(2):
                        servers[chatid]['hasBox'] = False
                        box_markup_item = telebot.types.InlineKeyboardButton('🪤',
                                                                                      callback_data='add_box ' + str(
                                                                                          message.from_user.id) + ' ' + str(
                                                                                          message.id))
                    else:
                        box_markup_item = telebot.types.InlineKeyboardButton('🔒',
                                                                             callback_data='box_has_key ' + str(
                                                                                 message.from_user.id) + ' ' + str(
                                                                                 message.id))

                    box_markup.add(box_markup_item)
                    bot.edit_message_text(final_str, msg.chat.id, msg.message_id, reply_markup=box_markup)
                    time.sleep(3)

    else:
        bot.send_message(message.chat.id, 'Укажите количество кругов')
        race_over = True
        inRace = False
        servers[chatid]['inRace'] = False
        return

    servers.pop(chatid, None)
    time.sleep(15)
    bot.delete_message(msg.chat.id, msg.message_id)
    bot.delete_message(msg.chat.id, message.message_id)
    bot.delete_message(msg.chat.id, win_msg.message_id)

    return


# /race command handler
@bot.message_handler(commands=['race'])
def race(message):
    game_thread = threading.Thread(target=game, args=(message,))
    game_thread.start()


# /arcade command handler
@bot.message_handler(commands=['arcade'])
def arcade(message):
    game_thread = threading.Thread(target=arcade_game, args=(message,))
    game_thread.start()


# /profile command handler
@bot.message_handler(commands=['profile'])
def profile(message):
    if inRace:
        return

    if len(message.text.split(' ')) != 2:
        username = message.from_user.username
        user = check_user(message)

        rank = user[2]
        total_games = user[3]
        wins = user[4]
        if total_games != 0:
            avg = round(wins / total_games, 2)
        else:
            avg = 0
        coins = user[5]
        skin = user[6]
        secret_title = user[7]
        flag = user[12]
        xp = user[14]

        xp_data = str(user[15]).strip().split(' ')
        dataX = np.array(range(1, len(xp_data) + 1))

        user_figure, user_plot = plt.subplots(layout='constrained')
        user_plot.plot(dataX, xp_data, **{'marker': 'o'}, label='Рейтинг')
        user_plot.set_title('График игрока ' + str(user[0]))
        user_plot.legend()
        user_plot.set_facecolor((0.1, 0.1, 0.1))
        user_plot.tick_params(axis='x', colors='white')
        user_plot.tick_params(axis='y', colors='white')
        user_plot.title.set_color('white')
        fig = user_figure
        fig.patch.set_facecolor((0.1, 0.1, 0.1))

        imgdata = io.BytesIO()
        fig.savefig(imgdata, format='png')
        imgdata.seek(0)

        profile_string = '📊СТАТИСТИКА RACE:\n\n{} {} [{}] \n\n  ⚔️Всего игр: {}\n  🏆Побед: {}\n  ⚠️Avg: {}\n  💎Монеты: {}\n  🎎Скин: {}\n  🎌Флаг: {}\n\n  🎖Рейтинг: {}'.format(
            secret_title, username, rank, total_games, wins, avg, coins, skin, flag, xp)

        del_message_markaup = telebot.types.InlineKeyboardMarkup(row_width=1)
        del_message_markaup_item = telebot.types.InlineKeyboardButton('❌', callback_data='del_message ' + str(
            message.from_user.id) + ' ' + str(message.id))
        del_message_markaup.add(del_message_markaup_item)

        bot.send_photo(message.chat.id, imgdata, caption=profile_string, reply_markup=del_message_markaup)

    else:

        username = message.text.split(' ')[1].replace('@', '')
        user = check_user_by_name(username)
        if not user:
            bot.send_message(message.chat.id, 'Игрок не найден')
            return

        rank = user[2]
        total_games = user[3]
        wins = user[4]
        if total_games != 0:
            avg = round(wins / total_games, 2)
        else:
            avg = 0
        coins = user[5]
        skin = user[6]
        secret_title = user[7]
        flag = user[12]
        xp = user[14]

        xp_data = str(user[15]).strip().split(' ')
        dataX = np.array(range(1, len(xp_data) + 1))

        user_figure, user_plot = plt.subplots(layout='constrained')
        user_plot.plot(dataX, xp_data, **{'marker': 'o'}, label='Рейтинг')
        user_plot.set_title('График игрока ' + str(user[0]))
        user_plot.legend()
        user_plot.set_facecolor((0.1, 0.1, 0.1))
        user_plot.tick_params(axis='x', colors='white')
        user_plot.tick_params(axis='y', colors='white')
        user_plot.title.set_color('white')
        fig = user_figure
        fig.patch.set_facecolor((0.1, 0.1, 0.1))

        imgdata = io.BytesIO()
        fig.savefig(imgdata, format='png')
        imgdata.seek(0)

        profile_string = '📊СТАТИСТИКА RACE:\n\n{} {} [{}] \n\n  ⚔️Всего игр: {}\n  🏆Побед: {}\n  ⚠️Avg: {}\n  💎Монеты: {}\n  🎎Скин: {}\n  🎌Флаг: {}\n\n  🎖Рейтинг: {}'.format(
            secret_title, username, rank, total_games, wins, avg, coins, skin, flag, xp)

        del_message_markaup = telebot.types.InlineKeyboardMarkup(row_width=1)
        del_message_markaup_item = telebot.types.InlineKeyboardButton('❌', callback_data='del_message ' + str(
            message.from_user.id) + ' ' + str(message.id))
        del_message_markaup.add(del_message_markaup_item)

        bot.send_photo(message.chat.id, imgdata, caption=profile_string, reply_markup=del_message_markaup)


# /shop command handler
@bot.message_handler(commands=['shop'])
def shop(message):
    if inRace:
        return
    shop_string = ''

    shop_skins_markaup = telebot.types.InlineKeyboardMarkup(row_width=8)
    row150 = []
    row200 = []
    row400 = []
    row500 = []

    for key in shop_dict['skins']['150']:
        row150.append(telebot.types.InlineKeyboardButton(str(shop_dict['skins']['150'][key][0]),
                                                         callback_data='buy ' + '150 ' + str(key)))
    row150.append(telebot.types.InlineKeyboardButton('150', callback_data='None'))
    for key in shop_dict['skins']['200']:
        row200.append(telebot.types.InlineKeyboardButton(str(shop_dict['skins']['200'][key][0]),
                                                         callback_data='buy ' + '200 ' + str(key)))
    row200.append(telebot.types.InlineKeyboardButton('200', callback_data='None'))
    for key in shop_dict['skins']['400']:
        row400.append(telebot.types.InlineKeyboardButton(str(shop_dict['skins']['400'][key][0]),
                                                         callback_data='buy ' + '400 ' + str(key)))
    row400.append(telebot.types.InlineKeyboardButton('400', callback_data='None'))
    for key in shop_dict['skins']['500']:
        row500.append(telebot.types.InlineKeyboardButton(str(shop_dict['skins']['500'][key][0]),
                                                         callback_data='buy ' + '500 ' + str(key)))
    row500.append(telebot.types.InlineKeyboardButton('500', callback_data='None'))

    del_message_markaup_item = telebot.types.InlineKeyboardButton('❌', callback_data='del_message ' + str(
        message.from_user.id) + ' ' + str(message.id))

    shop_skins_markaup.add(*row150)
    shop_skins_markaup.add(*row200)
    shop_skins_markaup.add(*row400)
    shop_skins_markaup.add(*row500)
    shop_skins_markaup.add(del_message_markaup_item)

    bot.send_message(message.chat.id, 'Выберите скин: ', reply_markup=shop_skins_markaup)


# /flag_shop command handler
@bot.message_handler(commands=['flag_shop'])
def flag_shop(message):
    if inRace:
        return
    shop_string = ''

    flag_shop_skins_markaup = telebot.types.InlineKeyboardMarkup(row_width=8)
    row300 = []
    row700 = []
    row1000 = []
    row1200 = []
    row1500 = []

    for key in shop_dict['flags']['300']:
        row300.append(telebot.types.InlineKeyboardButton(str(shop_dict['flags']['300'][key][0]),
                                                         callback_data='buy_flag ' + '300 ' + str(key)))
    row300.append(telebot.types.InlineKeyboardButton('300', callback_data='None'))
    for key in shop_dict['flags']['700']:
        row700.append(telebot.types.InlineKeyboardButton(str(shop_dict['flags']['700'][key][0]),
                                                         callback_data='buy_flag ' + '700 ' + str(key)))
    row700.append(telebot.types.InlineKeyboardButton('700', callback_data='None'))
    for key in shop_dict['flags']['1000']:
        row1000.append(telebot.types.InlineKeyboardButton(str(shop_dict['flags']['1000'][key][0]),
                                                          callback_data='buy_flag ' + '1000 ' + str(key)))
    row1000.append(telebot.types.InlineKeyboardButton('1000', callback_data='None'))
    for key in shop_dict['flags']['1200']:
        row1200.append(telebot.types.InlineKeyboardButton(str(shop_dict['flags']['1200'][key][0]),
                                                          callback_data='buy_flag ' + '1200 ' + str(key)))
    row1200.append(telebot.types.InlineKeyboardButton('1200', callback_data='None'))
    for key in shop_dict['flags']['1500']:
        row1500.append(telebot.types.InlineKeyboardButton(str(shop_dict['flags']['1500'][key][0]),
                                                          callback_data='buy_flag ' + '1500 ' + str(key)))
    row1500.append(telebot.types.InlineKeyboardButton('1500', callback_data='None'))

    del_message_markaup_item = telebot.types.InlineKeyboardButton('❌', callback_data='del_message ' + str(
        message.from_user.id) + ' ' + str(message.id))

    flag_shop_skins_markaup.add(*row300)
    flag_shop_skins_markaup.add(*row700)
    flag_shop_skins_markaup.add(*row1000)
    flag_shop_skins_markaup.add(*row1200)
    flag_shop_skins_markaup.add(*row1500)

    flag_shop_skins_markaup.add(del_message_markaup_item)
    bot.send_message(message.chat.id, 'Выберите флаг: ', reply_markup=flag_shop_skins_markaup)


# /skin command handler
@bot.message_handler(commands=['skin'])
def skin(message):
    if inRace:
        return
    user = check_user(message)
    skins = user[8].split(' ')

    set_skins_markaup = telebot.types.InlineKeyboardMarkup(row_width=8)
    set_skins_items = []

    for s in skins:
        set_skins_items.append(telebot.types.InlineKeyboardButton(str(s).strip(),
                                                                  callback_data='set ' + str(s) + ' ' + str(
                                                                      message.from_user.id)))

    del_message_markaup_item = telebot.types.InlineKeyboardButton('❌', callback_data='del_message ' + str(
        message.from_user.id) + ' ' + str(message.id))
    set_skins_markaup.add(*set_skins_items)
    set_skins_markaup.add(del_message_markaup_item)
    bot.send_message(message.chat.id, 'Выберите скин: ', reply_markup=set_skins_markaup)


# /rank command handler
@bot.message_handler(commands=['rank'])
def rank(message):
    if inRace:
        return
    user = check_user(message)
    ranks = user[9].split('#')

    set_ranks_markaup = telebot.types.InlineKeyboardMarkup(row_width=2)
    set_ranks_items = []

    for s in ranks:
        set_ranks_items.append(telebot.types.InlineKeyboardButton(str(s).strip(), callback_data='set_rank ' + str(
            s).strip() + ' ' + str(message.from_user.id).strip()))

    del_message_markaup_item = telebot.types.InlineKeyboardButton('❌', callback_data='del_message ' + str(
        message.from_user.id) + ' ' + str(message.id))
    set_ranks_markaup.add(*set_ranks_items)
    set_ranks_markaup.add(del_message_markaup_item)
    bot.send_message(message.chat.id, 'Выберите ранг: ', reply_markup=set_ranks_markaup)


# /tile command handler
@bot.message_handler(commands=['tile'])
def tile(message):
    if inRace:
        return
    user = check_user(message)
    tiles = user[11].split(' ')

    set_tiles_markaup = telebot.types.InlineKeyboardMarkup(row_width=2)
    set_tiles_items = []

    for s in tiles:
        set_tiles_items.append(telebot.types.InlineKeyboardButton(str(s).strip(), callback_data='set_tile ' + str(
            s).strip() + ' ' + str(message.from_user.id).strip()))

    del_message_markaup_item = telebot.types.InlineKeyboardButton('❌', callback_data='del_message ' + str(
        message.from_user.id) + ' ' + str(message.id))
    set_tiles_markaup.add(*set_tiles_items)
    set_tiles_markaup.add(del_message_markaup_item)
    bot.send_message(message.chat.id, 'Выберите дорогу: ', reply_markup=set_tiles_markaup)


# /flag command handler
@bot.message_handler(commands=['flag'])
def flag(message):
    if inRace:
        return
    user = check_user(message)
    flags = user[13].split(' ')

    set_flags_markaup = telebot.types.InlineKeyboardMarkup(row_width=2)
    set_flags_items = []

    for s in flags:
        set_flags_items.append(telebot.types.InlineKeyboardButton(str(s).strip(), callback_data='set_flag ' + str(
            s).strip() + ' ' + str(message.from_user.id).strip()))

    del_message_markaup_item = telebot.types.InlineKeyboardButton('❌', callback_data='del_message ' + str(
        message.from_user.id) + ' ' + str(message.id))
    set_flags_markaup.add(*set_flags_items)
    set_flags_markaup.add(del_message_markaup_item)
    bot.send_message(message.chat.id, 'Выберите флаг: ', reply_markup=set_flags_markaup)


# /top command handler
@bot.message_handler(commands=['top'])
def top(message):
    cur.execute('SELECT * FROM users ORDER BY wins DESC LIMIT 10')
    players = cur.fetchall()

    top_str = '🏆Рейтинг непобедимых:\n\n'

    for i, p in enumerate(players):
        idx = i + 1
        if idx == 1:
            idx = '🥇'
        elif idx == 2:
            idx = '🥈'
        elif idx == 3:
            idx = '🥉'
        else:
            idx = '  ' + str(idx)

        if idx == '🥉':
            top_str += '    {}. @{} | {} -> 🏆{}\n\n'.format(idx, p[0], p[7], p[4])
        else:
            top_str += '    {}. @{} | {} -> 🏆{}\n'.format(idx, p[0], p[7], p[4])

    del_message_markaup = telebot.types.InlineKeyboardMarkup(row_width=1)
    del_message_markaup_item = telebot.types.InlineKeyboardButton('❌', callback_data='del_message ' + str(
        message.from_user.id) + ' ' + str(message.id))
    del_message_markaup.add(del_message_markaup_item)
    bot.send_message(message.chat.id, top_str, reply_markup=del_message_markaup)


# Admin commands for debug

# /add_wins command handler
@bot.message_handler(commands=['add_wins'])
def add_winss(message):
    if message.from_user.id != 884728824:
        return

    user = message.text.split(' ')[1]
    amount = message.text.split(' ')[2]
    userid = check_user_by_name(user.replace('@', ''))[1]
    add_wins(userid, amount)

    bot.send_message(message.chat.id, '@' + message.from_user.username + ', вы добавили победы для -> ' + user)


# /add_money command handler
@bot.message_handler(commands=['add_money'])
def add_money(message):
    if message.from_user.id != 884728824:
        return

    user = message.text.split(' ')[1]
    amount = message.text.split(' ')[2]
    userid = check_user_by_name(user.replace('@', ''))[1]
    inc_coins(userid, amount)

    bot.send_message(message.chat.id, '@' + message.from_user.username + ', вы добавили монеты для -> ' + user)


# /unlock command handler
@bot.message_handler(commands=['unlock'])
def unlock(message):
    if message.from_user.id != 884728824:
        return

    user = message.text.split(' ')[1]
    skin = message.text.split(' ')[2]
    userid = check_user_by_name(user.replace('@', ''))[1]
    add_skin(userid, skin.strip())

    bot.send_message(message.chat.id,
                     '@' + message.from_user.username + ', вы открыли скин -> ' + str(skin) + ' для ' + user)


# /unlock_rank command handler
@bot.message_handler(commands=['unlock_rank'])
def unlock_rank(message):
    if message.from_user.id != 884728824:
        return

    username = message.text.split(' ')[3]
    ico = message.text.split(' ')[1]
    rank = message.text.split(' ')[2]
    user = check_user_by_name(username.replace('@', ''))
    if not user:
        return
    userid = user[1]
    add_rank(userid, ico.strip() + ' ' + rank.strip())

    bot.send_message(message.chat.id,
                     '@' + message.from_user.username + ', вы открыли ранг -> ' + str(rank) + ' для ' + username)


# /plot command handler
@bot.message_handler(commands=['plot'])
def plot(message):
    legend = ''
    if len(message.text.split(' ')) < 2:
        bot.send_message(message.chat.id, 'Укажите значения по оси Y  формате n#n#n')
        return
    elif len(message.text.split(' ')) > 2:
        legend = ' '.join(message.text.split(' ')[2:len(message.text.split(' '))])

    user = check_user(message)

    dataY = []
    if message.text.split(' ')[1] == 'rand':
        if len(message.text.split(' ')) > 2:
            legend = ''
            rangee = abs(int(message.text.split(' ')[2]))
            if rangee >= 1000:
                rangee = 1000
            if rangee < 0:
                rangee = 0
            for i in range(rangee):
                dataY.append(random.randint(0, 300))
        else:
            for i in range(300):
                dataY.append(random.randint(0, 300))
    else:
        data = message.text.split(' ')[1].split('#')
        dataY = list(map(int, data))


    dataX = np.array(range(1, len(dataY) + 1))

    user_figure, user_plot = plt.subplots(layout='constrained')
    if len(legend) > 0:
        user_plot.plot(dataX, dataY, **{'marker': 'o'}, label=str(legend))
    else:
        user_plot.plot(dataX, dataY, **{'marker': 'o'})
    user_plot.legend()
    user_plot.set_facecolor((0.1, 0.1, 0.1))
    user_plot.tick_params(axis='x', colors='white')
    user_plot.tick_params(axis='y', colors='white')
    fig = user_figure
    fig.patch.set_facecolor((0.1, 0.1, 0.1))

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    del_message_markaup = telebot.types.InlineKeyboardMarkup(row_width=1)
    del_message_markaup_item = telebot.types.InlineKeyboardButton('❌', callback_data='del_message ' + str(
        message.from_user.id) + ' ' + str(message.id))
    del_message_markaup.add(del_message_markaup_item)
    bot.send_photo(message.chat.id, buf, reply_markup=del_message_markaup)


bot.infinity_polling()
