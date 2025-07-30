from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler, JobQueue
import logging
import random
import json
import os
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Словарь для хранения состояний чатов
conversation_states = {}

# Структура данных для игроков
players = {}

# Структура данных для гильдий
guilds = {}

# В начале файла добавим состояния
CONVERSATION_STATES = {
    'IN_GUILD_MENU': 1,
    'IN_TOURNAMENT_MENU': 2,
    'AWAITING_GUILD_NAME': 10,
    'AWAITING_JOIN_GUILD': 4 
}

# Дополняем систему веса предметов
item_weights = {
    'Малое зелье здоровья': 0.5,
    'Среднее зелье здоровья': 1,
    'Большое зелье здоровья': 2,
    'Меч': 5,
    'Лук': 3,
    'Посох': 4,
    'Кольчуга': 8,
    'Капюшон': 2,
    'Броники': 6,
    '🐾 Енот': 3,
    '🦊 Лиса': 2,
    '🦔 Ёж': 1
}

# Дополняем словари предметов
item_effects = {
    'Меч': {'attack_bonus': (5, 10)},
    'Лук': {'attack_bonus': (3, 7)},
    'Посох': {'magic_bonus': (4, 8)},
    'Кольчуга': {'defense_bonus': (5, 10)},
    '🐾 Енот': {'scavenge_bonus': 0.2}
}

# Мировые события
world_events = []

# Турниры
tournaments = []

# Места для исследования
locations = [
    '🌲 Лес',
    '🏰 Пещера',
    '🏰 Замок',
    '🏡 Деревня',
    '🏙️ Город',
    '🏔️ Гора',
    '🌿 Лесное царство',
    '🕳️ Подземелье',
    '🌊 Река',
    '🏜️ Пустыня'
]

# Словарь с характеристиками монстров
monsters = {
    '👹 Гоблин': {
        'base_health': 30,
        'base_attack': 5,
        'description': '🧙♂️ Слабый монстр, живущий в пещерах.'
    },
    '🛡️ Орк': {
        'base_health': 50,
        'base_attack': 10,
        'description': '🪖 Сильный монстр, обитающий в степях.'
    },
    '🐉 Дракон': {
        'base_health': 100,
        'base_attack': 20,
        'description': '🔥 Мощное существо, обитающее в горах.'
    },
    '🧟 Тролль': {
        'base_health': 70,
        'base_attack': 15,
        'description': '🌳 Крепкий монстр, живущий в лесу.'
    },
    '🐍 Шахтёрский змей': {
        'base_health': 40,
        'base_attack': 8,
        'description': '🪱 Опасный змей, обитающий в шахтах.'
    },
    '👻 Призрак': {
        'base_health': 35,
        'base_attack': 6,
        'description': '🕵️♂️ Taинственное существо, обитающее в замках.'
    }
}

pets = {
    '🐾 Енот': {
        'health': 20,
        'attack': 3,
        'description': '🌿 Ловкий и хитрый спутник, который поможет в бою.'
    },
    '🦊 Лиса': {
        'health': 25,
        'attack': 4,
        'description': '🦊 Быстрая и умная, идеально подходит для разведки.'
    },
    '🦔 Ёж': {
        'health': 30,
        'attack': 2,
        'description': '🌴 Милый и колючий защитник, который будет защищать вас.'
    }
}

# Словарь с характеристиками одежды
clothes = {
    'Кольчуга': {
        'defense_bonus': random.randint(5, 10),
        'health_bonus': random.randint(5, 15),
        'description': 'Легкая броня, увеличивающая здоровье.'
    },
    'Капюшон': {
        'defense_bonus': random.randint(1, 3),  # Добавляем защиту
        'health_bonus': random.randint(3, 8),
        'attack_bonus': random.randint(1, 4),
        'description': 'Увеличивает атаку и немного здоровье.'
    },
    'Броники': {
        'defense_bonus': random.randint(8, 12),  # Добавляем защиту
        'health_bonus': random.randint(10, 20),
        'attack_bonus': random.randint(-3, 3),
        'description': 'Средняя броня, увеличивающая здоровье.'
    }
}

# Словарь с характеристиками оружия
weapons = {
    'Меч': {
        'attack_bonus': random.randint(5, 10),
        'description': 'Острое оружие для ближнего боя.'
    },
    'Лук': {
        'attack_bonus': random.randint(3, 7),
        'description': 'Оружие для дальнего боя.'
    },
    'Посох': {
        'attack_bonus': random.randint(4, 8),
        'description': 'Магическое оружие.'
    }
}

# Словарь с характеристиками зелий
potions = {
    'Малое зелье здоровья': {
        'health': 20,
        'description': 'Восстанавливает 20 здоровья.'
    },
    'Среднее зелье здоровья': {
        'health': 50,
        'description': 'Восстанавливает 50 здоровья.'
    },
    'Большое зелье здоровья': {
        'health': 100,
        'description': 'Восстанавливает 100 здоровья.'
    }
}

MAX_ITEMS = 10  # Максимальное количество предметов в инвентаре
MAX_WEIGHT = 50  # Максимальный общий вес инвентаря

def save_game():
    with open('players.json', 'w') as f:
        json.dump(players, f)
    with open('guilds.json', 'w') as f:
        json.dump(guilds, f)

def load_game():
    global players, guilds
    if os.path.exists('players.json'):
        with open('players.json') as f:
            players = json.load(f)
    if os.path.exists('guilds.json'):
        with open('guilds.json') as f:
            guilds = json.load(f)

# Обновленная структура игрока
def init_player(user_id: int, name: str):
    players[user_id] = {
        'name': name,
        'level': 1,
        'health': 100,
        'max_health': 100,
        'attack': 10,
        'defense': 5,
        'gold': 100,
        'location': 'Деревня',
        'inventory': [],
        'inventory_weight': 0,
        'equipped': {
            'weapon': None,
            'armor': None
        },
        'active_buffs': {},
        'stats': {
            'monsters_killed': 0,
            'damage_dealt': 0,
            'quests_completed': 0
        },
        'last_active': datetime.now(),
        'pet': None,
        'current_monster': None,
        'experience': 0,
        'experience_to_next_level': 100,
        'inventory_weight': 0
    }

# Обновленные предметы
weapons.update({
    '🗡️ Кинжал теней': {
        'attack_bonus': (8, 12),
        'description': 'Магический кинжал, наносящий дополнительный темный урон',
        'type': 'weapon',
        'weight': 3
    }
})

clothes.update({
    '🛡️ Щит дракона': {
        'defense_bonus': 15,
        'health_bonus': 20,
        'description': 'Легендарный щит из драконьей чешуи',
        'type': 'armor',
        'weight': 10
    }
})

potions.update({
    '🧪 Эликсир ярости': {
        'effect': {'attack_multiplier': 1.5, 'duration': 300},
        'description': 'Увеличивает атаку на 50% на 5 минут',
        'type': 'buff',
        'weight': 1
    }
})

async def calculate_damage(attacker, defender):
    base_attack = attacker.get('attack', 0)
    if attacker.get('equipped', {}).get('weapon'):
        weapon = weapons[attacker['equipped']['weapon']]
        base_attack += random.randint(*weapon['attack_bonus'])
    
    defense = defender.get('defense', 0)
    damage = max(1, base_attack - defense + random.randint(-2, 2))
    return damage

async def battle_cycle(player, monster):
    while player['health'] > 0 and monster['health'] > 0:
        player_damage = await calculate_damage(player, monster)
        monster['health'] -= player_damage
        
        monster_damage = await calculate_damage(monster, player)
        player['health'] -= monster_damage
        
        yield {
            'player_damage': player_damage,
            'monster_damage': monster_damage,
            'player_health': player['health'],
            'monster_health': monster['health']
        }

# Функция для создания гильдии
async def create_guild(update: Update, context: CallbackContext, guild_name: str):
    user_id = update.message.from_user.id
    player = players.get(user_id)
    
    if not player:
        await update.message.reply_text("❌ Персонаж не найден!")
        return

    if len(guild_name) < 3:
        await update.message.reply_text("❌ Название гильдии должно быть не менее 3 символов!")
        return

    if guild_name in guilds:
        await update.message.reply_text("❌ Гильдия с таким названием уже существует!")
        return

    guilds[guild_name] = {
        'leader': user_id,
        'members': [user_id],
        'created_at': datetime.now(),
        'level': 1,
        'reputation': 0
    }
    
    players[user_id]['guild'] = guild_name
    await update.message.reply_text(f"✅ Гильдия «{guild_name}» успешно создана!")
    await main_menu(update, context)

# Функция для вступления в гильдию
async def join_guild(update: Update, context: CallbackContext, guild_name: str):
    user_id = update.message.from_user.id
    player = players.get(user_id)
    
    if not player:
        await update.message.reply_text("❌ Персонаж не найден!")
        return

    if guild_name not in guilds:
        await update.message.reply_text("❌ Гильдия не существует!")
        return

    if user_id in guilds[guild_name]['members']:
        await update.message.reply_text("❌ Вы уже в этой гильдии!")
        return

    guilds[guild_name]['members'].append(user_id)
    players[user_id]['guild'] = guild_name
    await update.message.reply_text(f"✅ Вы вступили в гильдию «{guild_name}»!")
    await main_menu(update, context)

# Функция для отображения информации о гильдии
async def guild_info(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in players:
        await update.message.reply_text("❌ Сначала создайте персонажа!")
        return

    player = players[user_id]
    if 'guild' not in player:
        await update.message.reply_text("❌ Вы не состоите в гильдии!")
        return

    guild_name = player['guild']
    guild = guilds.get(guild_name)
    
    if not guild:
        await update.message.reply_text("❌ Гильдия не найдена!")
        return

    members = "\n".join([f"• {players[member_id]['name']}" for member_id in guild['members']])
    
    await update.message.reply_text(
        f"🏰 Гильдия: {guild_name}\n"
        f"👑 Лидер: {players[guild['leader']]['name']}\n"
        f"📅 Создана: {guild['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
        f"👥 Участники {guild['members']}):\n{members}"
    )

# Функция для создания мирового события
def create_world_event():
    events = [
        "🌋 Извержение вулкана! Все игроки получают урон.",
        "🌧️ Начался сильный дождь. Все игроки восстанавливают здоровье.",
        "🐉 Дракон появился в мире! Все игроки получают бонус к атаке.",
        "🌪️ Началась буря! Все игроки теряют предметы из инвентаря."
    ]
    event = random.choice(events)
    world_events.append({
        'event': event,
        'time': datetime.now()
    })
    return event

# Функция для отображения мировых событий
async def show_world_events(update: Update, context: CallbackContext):
    if not world_events:
        await update.message.reply_text("Мировых событий нет.")
        return

    events_text = "\n".join([f"{event['event']} ({event['time'].strftime('%Y-%m-%d %H:%M:%S')})" for event in world_events])
    await update.message.reply_text(f"Мировые события:\n{events_text}")

# Добавляем периодическую задачу для мировых событий (в функцию main)
async def world_event_scheduler(context: CallbackContext):
    if random.random() < 0.3:
        event = create_world_event()
        await context.bot.send_message(
            chat_id='@ваш_канал',  # Заменить на реальный ID
            text=f"🌍 Мировое событие: {event}"
        )
        await send_notification(user_id, "Началось мировое событие!")

async def tournament_scheduler(context: CallbackContext):
    if not tournaments or datetime.now() >= tournaments[-1]['end_time']:
        new_tournament = create_tournament()
        await context.bot.send_message(
            chat_id='@ваш_канал',
            text=f"🏆 Начат новый турнир: {new_tournament['name']}! Присоединяйтесь!"
        )
        await send_notification(user_id, "Новый турнир начался!")

async def admin_command(update: Update, context: CallbackContext):
    if update.effective_user.id not in ADMINS:
        return
    
    command = context.args[0]
    if command == 'give_gold':
        user_id = int(context.args[1])
        amount = int(context.args[2])
        players[user_id]['gold'] += amount
        await update.message.reply_text(f"Выдано {amount} золота игроку {user_id}")

# Функция для создания турнира
def create_tournament():
    tournament = {
        'name': f"Турнир #{len(tournaments) + 1}",
        'start_time': datetime.now(),
        'end_time': datetime.now() + timedelta(hours=1),
        'participants': [],
        'winner': None,
        'active': True
    }
    tournaments.append(tournament)
    return tournament

# Динамическая сложность монстров
def generate_monster(player_level):
    base_level = max(1, player_level - 2 + random.randint(0, 4))
    return {
        'health': 50 + base_level * 10,
        'attack': 10 + base_level * 3,
        'exp_reward': 20 + base_level * 5
    }

# Прогрессия уровней
def calculate_exp_required(level):
    return 100 * (1.5 ** (level - 1))

# Функция для участия в турнире
async def join_tournament(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in players:
        await update.message.reply_text("Сначала создайте персонажа!")
        return

    active_tournaments = [t for t in tournaments if t['active']]
    if not active_tournaments:
        await update.message.reply_text("Сейчас нет активных турниров.")
        return

    tournament = active_tournaments[-1]
    if user_id in tournament['participants']:
        await update.message.reply_text("Вы уже участвуете в этом турнире.")
        return

    tournament['participants'].append(user_id)
    await update.message.reply_text(f"Вы присоединились к турниру {tournament['name']}!")

async def tournament_menu(update: Update, context: CallbackContext):
    keyboard = [
        ['Присоединиться к турниру', 'Информация о турнире'],
        ['Назад']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Турниры:",
        reply_markup=reply_markup
    )
    conversation_states[update.effective_chat.id] = CONVERSATION_STATES['IN_TOURNAMENT_MENU']

# Функция для отображения информации о турнире
async def tournament_info(update: Update, context: CallbackContext):
    if not tournaments:
        await update.message.reply_text("Сейчас нет активных турниров.")
        return

    tournament = tournaments[-1]
    participants = ", ".join([players[participant]['name'] for participant in tournament['participants']])
    await update.message.reply_text(
        f"Турнир: {tournament['name']}\n"
        f"Участники: {participants}\n"
        f"Время окончания: {tournament['end_time'].strftime('%Y-%m-%d %H:%M:%S')}"
    )

# Функция для использования зелья
async def use_potion(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in players:
        await update.message.reply_text("Сначала создайте персонажа с помощью /create.")
        return

    player = players[user_id]
    potion_name = ' '.join(context.args)
    
    if potion_name not in potions:
        await update.message.reply_text("Такого зелья не существует.")
        return

    if potion_name not in player['inventory']:
        await update.message.reply_text("У вас нет этого зелья.")
        return

    potion = potions[potion_name]
    
    # Применение эффекта
    if 'health' in potion:
        player['health'] = min(
            player['max_health'],
            player['health'] + potion['health']
        )
        await update.message.reply_text(f"Вы восстановили {potion['health']} здоровья.")
    
    # Удаление зелья из инвентаря
    player['inventory'].remove(potion_name)
    player['inventory'] = inventory
    await update.message.reply_text(f"Вы использовали {potion_name} и восстановили {potion['health']} здоровья.")

async def add_item(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in players:
        await update.message.reply_text("???? Сначала создайте персонажа с помощью /create.")
        return

    # Разбиваем сообщение на команду и параметры
    message_text = update.message.text
    parts = message_text.split()
    if len(parts) < 2:
        await update.message.reply_text("???? Используйте: /add_item <имя_предмета> [количество]")
        return

    item_name = parts[1]
    quantity = 1
    if len(parts) > 2:
        try:
            quantity = int(parts[2])
            if quantity <= 0:
                await update.message.reply_text("???? Количество должно быть положительным числом.")
                return
        except ValueError:
            await update.message.reply_text("???? Неверное количество.")
            return

    player = players[user_id]
    inventory = player.get('inventory', [])

    # Проверка existence предмета
    if item_name not in item_weights:
        await update.message.reply_text(f"???? Предмет {item_name} не существует.")
        return

    # Расчет общего веса
    current_weight = sum(item_weights[item] for item in inventory)
    additional_weight = item_weights[item_name] * quantity
    new_weight = current_weight + additional_weight

    if new_weight > MAX_WEIGHT:
        await update.message.reply_text(f"???? Превышен максимальный вес инвентаря ({MAX_WEIGHT}).")
        return

    if len(inventory) + quantity > MAX_ITEMS:
        await update.message.reply_text(f"Инвентарь полон! Макс. {MAX_ITEMS} предметов.")
        return

    # Добавление предмета
    for _ in range(quantity):
        inventory.append(item_name)
    player['inventory'] = inventory

    await update.message.reply_text(f"???? Предмет {item_name} добавлен в инвентарь.")

async def remove_item(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in players:
        await update.message.reply_text("Сначала создайте персонажа с помощью /create.")
        return

    message_text = update.message.text
    parts = message_text.split()
    if len(parts) < 2:
        await update.message.reply_text("Используйте: /remove_item <имя_предмета> [количество]")
        return

    item_name = parts[1]
    quantity = 1
    if len(parts) > 2:
        try:
            quantity = int(parts[2])
            if quantity <= 0:
                await update.message.reply_text("Количество должно быть положительным числом.")
                return
        except ValueError:
            await update.message.reply_text("Неверное количество.")
            return

    player = players[user_id]
    inventory = player.get('inventory', [])

    # Проверка наличия предмета
    if item_name not in inventory:
        await update.message.reply_text(f"Предмета {item_name} нет в инвентаре.")
        return

    # Удаление предмета
    count = 0
    while count < quantity and item_name in inventory:
        inventory.remove(item_name)
        count += 1

    player['inventory'] = inventory

    total_weight_removed = 0
    while count < quantity and item_name in inventory:
        inventory.remove(item_name)
        total_weight_removed += item_weights[item_name]
        count += 1
    
    player['inventory_weight'] -= total_weight_removed

    await update.message.reply_text(f"Предмет {item_name} удален из инвентаря.")

async def error_handler(update: Update, context: CallbackContext):
    error = context.error
    logger.error(msg="Исключение при обработке запроса:", exc_info=error)
    
    if update.message:
        await update.message.reply_text("⚠ Произошла ошибка при обработке запроса. Попробуйте еще раз.")

async def schedule_world_events(context: CallbackContext):
    event = create_world_event()
    for user_id in players:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🌍 Мировое событие: {event['description']}\n"
                     f"Эффект: {event['effect']}"
            )
            apply_world_event_effect(user_id, event)
        except Exception as e:
            logger.error(f"Ошибка отправки события игроку {user_id}: {e}")

def apply_world_event_effect(user_id: int, event: dict):
    if "атака" in event['effect']:
        players[user_id]['attack'] *= 1.2
    elif "здоровье" in event['effect']:
        players[user_id]['health'] = min(
            players[user_id]['max_health'],
            players[user_id]['health'] * 1.3
        )

    # Функция для экипировки предмета
async def equip_item(update: Update, context: CallbackContext):
    try:
        user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    except AttributeError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ошибка доступа к данным пользователя")
        return

    player = players.get(user_id)
    if not player:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Сначала создайте персонажа!")
        return

    if not context.args:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Укажите предмет для экипировки")
        return

    item_name = ' '.join(context.args)
    
    # Проверка наличия предмета
    if item_name not in player['inventory']:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Предмета нет в инвентаре")
        return

    # Определяем тип предмета с защитой от ошибок
    item_type = None
    item_data = {}
    if item_name in weapons:
        item_type = 'weapon'
        item_data = weapons.get(item_name, {})
    elif item_name in clothes:
        item_type = 'armor'
        item_data = clothes.get(item_name, {})
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Это нельзя экипировать")
        return

    # Безопасное получение характеристик
    defense_bonus = item_data.get('defense_bonus', 0)
    health_bonus = item_data.get('health_bonus', 0)
    attack_bonus = item_data.get('attack_bonus', 0)

    try:
        # Снимаем предыдущую экипировку
        if old_item := player['equipped'][item_type]:
            old_data = clothes[old_item] if item_type == 'armor' else weapons[old_item]
            
            # Безопасное снятие характеристик
            player['defense'] -= old_data.get('defense_bonus', 0)
            player['max_health'] -= old_data.get('health_bonus', 0)
            player['attack'] -= old_data.get('attack_bonus', 0)
            player['inventory'].append(old_item)

        # Экипируем новый предмет
        player['equipped'][item_type] = item_name
        player['inventory'].remove(item_name)
        
        # Применяем новые характеристики
        player['defense'] += defense_bonus
        player['max_health'] += health_bonus
        player['attack'] += attack_bonus
        player['health'] = min(player['health'], player['max_health'])

        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"✅ {item_name} экипирован!")
    except Exception as e:
        logger.error(f"Ошибка экипировки: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Ошибка при экипировке")

# Добавьте callback для экипировки:
async def equip_item_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    # Получаем user_id из callback_query
    user_id = query.from_user.id
    item_name = query.data.split('_')[1]

    if user_id not in players:
        await query.edit_message_text("Сначала создайте персонажа!")
        return

    try:
        # Передаем аргументы правильно
        context.args = [item_name]
        
        # Создаем фейковый update с message
        class FakeMessage:
            def __init__(self, user_id):
                self.from_user = type('', (), {'id': user_id})()
                
        fake_update = Update(
            update_id=update.update_id,
            callback_query=update.callback_query,
            message=FakeMessage(user_id)
        )
        
        await equip_item(fake_update, context)
        await query.edit_message_text(f"✅ {item_name} экипирован!")
    except Exception as e:
        logger.error(f"Ошибка экипировки: {e}")
        await query.edit_message_text("❌ Ошибка экипировки")
        await equip_item(update, context)
        await query.message.delete()

async def handle_victory_rewards(update: Update, player: dict):
    # Шансы на выпадение предметов
    reward_chances = {
        'weapon': 40,  # 40% шанс получить оружие
        'armor': 30,    # 30% шанс получить броню
        'potion': 70    # 70% шанс получить зелье
    }

    # Генерация наград
    rewards = []
    
    # Проверяем выпадение оружия
    if random.randint(1, 100) <= reward_chances['weapon']:
        weapon = random.choice(list(weapons.keys()))
        rewards.append(weapon)
        player['inventory'].append(weapon)
    
    # Проверяем выпадение брони
    if random.randint(1, 100) <= reward_chances['armor']:
        armor = random.choice(list(clothes.keys()))
        rewards.append(armor)
        player['inventory'].append(armor)
    
    # Проверяем выпадение зелья
    if random.randint(1, 100) <= reward_chances['potion']:
        potion = random.choice(list(potions.keys()))
        rewards.append(potion)
        player['inventory'].append(potion)

    # Отправка сообщения о наградах
    if rewards:
        reward_text = "🎁 Вы получили:\n" + "\n".join(f"• {item}" for item in rewards)
    else:
        reward_text = "😢 На этот раз ничего не выпало"
    
    await update.message.reply_text(
        f"⚔️ Вы победили {player['current_monster']['name']}!\n"
        f"{reward_text}\n"
        f"💰 +50 золота"
    )
    player['gold'] += 50

    for item in rewards:
        if (len(player['inventory']) >= MAX_ITEMS or 
            player['inventory_weight'] + item_weights[item] > MAX_WEIGHT):
            continue
        player['inventory'].append(item)
        player['inventory_weight'] += item_weights[item]


# Функция выбора оружия с учетом весов
def get_random_weapon():
    total = sum(w['chance'] for w in weapons.values())
    r = random.uniform(0, total)
    current = 0
    for weapon, params in weapons.items():
        if current + params['chance'] >= r:
            return weapon
        current += params['chance']
    return list(weapons.keys())[0]

# Функция для отображения инвентаря
async def show_inventory(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    try:
        user_id = update.message.from_user.id
        if user_id not in players:
            await update.message.reply_text("❌ Персонаж не найден!")
            return

        player = players.get(user_id, {})

        # Гарантированная инициализация всех необходимых полей
        inventory = player.get('inventory', [])
        equipped = player.get('equipped', {'weapon': None, 'armor': None})
        weight = player.get('inventory_weight', 0)

        # Форматирование содержимого инвентаря
        inventory_items = "\n".join([f"• {item}" for item in inventory]) if inventory else "🚫 Пусто"

        # Формирование сообщения
        message = (
            f"🎒 *Инвентарь*:\n{inventory_items}\n\n"
            f"⚖️ *Вес*: {weight}/{MAX_WEIGHT}\n"
            f"🔢 *Слотов*: {len(inventory)}/{MAX_ITEMS}\n\n"
            f"⚔ *Экипировано*:\n"
            f"- Оружие: {equipped.get('weapon', '🚫 Нет')}\n"
            f"- Броня: {equipped.get('armor', '🚫 Нет')}"
        )

        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
            logger.error(f"Ошибка в show_inventory: {str(e)}")
            await update.message.reply_text("⚠ Произошла ошибка при отображении инвентаря")

    if user_id not in players:
        await update.message.reply_text("Сначала создайте персонажа с помощью /create.")
        return

    player = players[user_id]

    # Формируем список предметов с учетом количества
    item_counts = {}
    for item in inventory:
        item_counts[item] = item_counts.get(item, 0) + 1
    
    inventory_list = []
    for item, count in item_counts.items():
        inventory_list.append(f"▫️ {item} ×{count}")

    equipped = [
        f"⚔ Оружие: {player['equipped'].get('weapon', 'Нет')}",
        f"🛡 Броня: {player['equipped'].get('armor', 'Нет')}"
    ]

    # Добавляем информацию о весе
    weight_info = f"\n⚖️ Общий вес: {player.get('inventory_weight', 0)}/{MAX_WEIGHT}"

    inventory = player.get('inventory', [])
    items = "\n".join([f"• {item}" for item in inventory]) if inventory else "Пусто"

    categories = {'weapon': [], 'armor': [], 'potion': [], 'pet': [], 'other': []}
    for item in player['inventory']:
        if item in weapons: categories['weapon'].append(item)
        elif item in clothes: categories['armor'].append(item)
        elif item in potions: categories['potion'].append(item)
        elif item in pets: categories['pet'].append(item)
        else: categories['other'].append(item)

    if not inventory:
        await update.message.reply_text("Ваш инвентарь пуст.")
        return

# Обработчик сообщений от пользователя
async def handle_message(update: Update, context: CallbackContext):
    global conversation_states
    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    current_state = conversation_states.get(chat_id, None)
    text = update.message.text

    if text == 'Назад':
        if current_state in [CONVERSATION_STATES['IN_GUILD_MENU'], 
                           CONVERSATION_STATES['IN_TOURNAMENT_MENU'],
                           CONVERSATION_STATES['AWAITING_GUILD_NAME']]:
            conversation_states[chat_id] = None
            await main_menu(update, context)
        return

    if current_state in [CONVERSATION_STATES['AWAITING_JOIN_GUILD']]:
            # Возврат в меню гильдий
            conversation_states[chat_id] = CONVERSATION_STATES['IN_GUILD_MENU']
            await guild_menu(update, context)
            return

    
    if text == 'Информация о гильдии':
        await guild_info(update, context)
        return

    if text == 'Вступить в гильдию':
        if user_id not in players:
            await update.message.reply_text("❌ Сначала создайте персонажа!")
            return
            
        if 'guild' in players[user_id]:
            await update.message.reply_text("❌ Вы уже состоите в гильдии!")
            return

        conversation_states[chat_id] = CONVERSATION_STATES['AWAITING_JOIN_GUILD']
        await update.message.reply_text("📛 Введите название гильдии для вступления:")
        return

    if current_state == CONVERSATION_STATES['AWAITING_JOIN_GUILD']:
        guild_name = text.strip()
        await join_guild(update, context, guild_name)
        conversation_states[chat_id] = None
        return

    if text == 'Создать гильдию':
        if user_id not in players:
            await update.message.reply_text("❌ Сначала создайте персонажа командой /create!")
            return
            
        if 'guild' in players[user_id]:
            await update.message.reply_text("❌ Вы уже состоите в гильдии!")
            return
            
        conversation_states[chat_id] = CONVERSATION_STATES['AWAITING_GUILD_NAME']
        await update.message.reply_text("📛 Введите название гильдии (3-20 символов):")
        return

    # 3. Обработка ввода названия гильдии
    if current_state == CONVERSATION_STATES['AWAITING_GUILD_NAME']:
        guild_name = text.strip()
        
        if len(guild_name) < 3 or len(guild_name) > 20:
            await update.message.reply_text("❌ Неправильная длина названия (3-20 символов)")
            return
            
        if guild_name in guilds:
            await update.message.reply_text("❌ Гильдия с таким названием уже существует!")
            return
            
        # Создание гильдии
        guilds[guild_name] = {
            'leader': user_id,
            'members': [user_id],
            'created_at': datetime.now(),
            'level': 1
        }
        players[user_id]['guild'] = guild_name
        conversation_states[chat_id] = None
        
        await update.message.reply_text(
            f"✅ Гильдия «{guild_name}» успешно создана!\n"
            f"👑 Вы стали лидером гильдии!"
        )

    if current_state == "waiting_for_name":
        # Обработка имени персонажа
        if not text:
            await update.message.reply_text("Введите имя вашего персонажа.")
            return
        name = text.strip()  # Remove any leading/trailing whitespace

        # Создаем персонажа
        if user_id not in players:
            # Структура данных для игроков
            players[user_id] = {
                'name': name,
                'level': 1,
                'health': 100,
                'max_health': 100,
                'attack': 10,
                'defense': 5,
                'gold': 0,
                'location': 'Деревня',
                'inventory': [],
                'equipped': {'weapon': None, 'armor': None},
                'pet': None,
                'current_monster': None,
                'experience': 0,
                'experience_to_next_level': 100,
                'inventory_weight': 0
            }
            init_player(user_id, name)  # Используем новую функцию
            await update.message.reply_text(f"Персонаж {name} создан! Добро пожаловать в мир приключений!")
            # Сброс состояния
            conversation_states[chat_id] = None
            await main_menu(update, context)
        else:
            await update.message.reply_text("Вы уже создали персонажа!")
        return

    if user_id not in players:
        await update.message.reply_text("Сначала создайте персонажа с помощью /create.")
        return

    if text == 'Исследовать мир':
        await explore(update, context)
    elif text == 'Сражение':
        await fight(update, context)
    elif text == 'Статус персонажа':
        await status(update, context)
    elif text == 'Создать персонажа':
        await create_character(update, context)
    elif text == 'Перейти в город':
        await go_to_town(update, context)
    elif text == 'Атаковать':
        await start_battle(update, context)
    elif text == 'Исследовать дальше':
        await explore(update, context)
    elif text == 'Приручить зверя':
        await get_pet(update, context)
    elif text == 'Одеть одежду':
        await wear_cloth(update, context)
    if text == 'Инвентарь':
        await show_inventory(update, context)
    elif text == 'Экипировать предмет':
        await equip_item_menu(update, context)  # Новая функция для выбора предмета
    elif text == 'Гильдии':
        await guild_menu(update, context)       # Меню гильдий
    elif text == 'Турниры':
        await tournament_menu(update, context)  # Меню турниров

async def equip_item_menu(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in players:
        await update.message.reply_text("Сначала создайте персонажа!")
        return

    player = players[user_id]
    equippable = [item for item in player['inventory'] if item in weapons or item in clothes]
    
    if not equippable:
        await update.message.reply_text("В инвентаре нет предметов для экипировки.")
        return

    keyboard = [[InlineKeyboardButton(item, callback_data=f"equip_{item}")] for item in equippable]
    await update.message.reply_text("Выберите предмет для экипировки:", 
                                  reply_markup=InlineKeyboardMarkup(keyboard))

async def guild_menu(update: Update, context: CallbackContext):
    keyboard = [
        ['Создать гильдию', 'Вступить в гильдию'],
        ['Информация о гильдии', 'Назад']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Гильдии:", reply_markup=reply_markup)

    # Устанавливаем состояние входа в меню гильдий
    conversation_states[update.effective_chat.id] = CONVERSATION_STATES['IN_GUILD_MENU']

async def tournament_menu(update: Update, context: CallbackContext):
    keyboard = [
        ['Присоединиться к турниру', 'Информация о турнире'],
        ['Назад']  # Кнопка Назад теперь будет работать
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Турниры:",
        reply_markup=reply_markup
    )

# Создание персонажа
async def create_character(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in players:
        await update.message.reply_text("🔴 Вы уже создали персонажа!")
        await main_menu(update, context)
        return

    # Устанавливаем состояние ожидания имени
    conversation_states[update.effective_chat.id] = "waiting_for_name"
    await update.message.reply_text("📝 Введите имя вашего персонажа:")

def level_up_player(user_id: int):
    player = players[user_id]
    player['level'] += 1
    player['max_health'] += 20
    player['health'] = player['max_health']
    player['attack'] += 5
    player['defense'] += 2
    player['experience'] = 0
    player['experience_to_next_level'] = 100 * player['level']
    player['active_buffs'] = {}

# Функция для повышения уровня персонажа
def level_up(user_id):
    players[user_id]['level'] += 1
    players[user_id]['health'] = 100 + (players[user_id]['level'] - 1) * 10
    players[user_id]['attack'] = 10 + (players[user_id]['level'] - 1) * 2
    players[user_id]['experience_to_next_level'] = 100 * players[user_id]['level']

# Команда для исследования мира
async def explore(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in players:
        await update.message.reply_text("🟢 Сначала создайте персонажа с помощью /create.")
        return

    location = random.choice(locations)
    players[user_id]['location'] = location
    await update.message.reply_text(f"📍 Вы находитесь в {location}. 🔍 Исследуйте дальше!")
    await main_menu(update, context)

# Команда для сражения с монстрами
async def fight(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in players or players[user_id]['health'] <= 0:
        await update.message.reply_text("🟢 Сначала создайте персонажа с помощью /create.")
        return

    # Выбираем случайного монстра
    monster_name = random.choice(list(monsters.keys()))
    monster = monsters[monster_name]

    # Уровень влияет на характеристики монстра
    player_level = players[user_id]['level']
    base_health = monster['base_health'] + player_level * 2
    base_attack = monster['base_attack'] + player_level * 1

    # Случайные отклонения характеристик
    monster_health = random.randint(int(base_health * 0.9), int(base_health * 1.1))
    monster_attack = random.randint(int(base_attack * 0.9), int(base_attack * 1.1))

    # Сохраняем текущего монстра
    players[user_id]['current_monster'] = {
        'name': monster_name,
        'health': monster_health,
        'attack': monster_attack
    }

    # Отображаем информацию о монстре и выбор действия
    keyboard = [
        ['Атаковать', 'Исследовать дальше']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        f"👻 Вы встретили {monster_name}!\n"
        f"💡 Описание: {monster['description']}\n"
        f"❤️ Здоровье: {monster_health}\n"
        f"🗡 Атака: {monster_attack}\n\n"
        f"🎮 Ваш уровень: {players[user_id]['level']}\n"
        f"❤️ Ваше здоровье: {players[user_id]['health']}\n"
        f"🗡 Ваша атака: {players[user_id]['attack']}\n\n"
        "🎯 Выберите действие:",
        reply_markup=reply_markup
    )

# Команда для начала боя
async def start_battle(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in players or players[user_id]['health'] <= 0:
        await update.message.reply_text("Сначала создайте персонажа с помощью /create.")
        return

    # Получаем текущего монстра
    current_monster = players[user_id].get('current_monster')
    if not current_monster:
        await update.message.reply_text("Сначала встретьте монстра, используя команду /fight.")
        return

    monster_name = current_monster['name']
    monster_health = current_monster['health']
    monster_attack = current_monster['attack']

    # Сражение
    while monster_health > 0 and players[user_id]['health'] > 0:
        player_damage = random.randint(5, players[user_id]['attack'])
        monster_health -= player_damage
        players[user_id]['health'] -= monster_attack
        await update.message.reply_text(f"⚔️ Вы атаковали {monster_name} на {player_damage} урона!")
        await update.message.reply_text(f"{monster_name} атакует вас! Ваше здоровье: {players[user_id]['health']}")

        # Проверка на завершение боя
        if monster_health <= 0:
            await update.message.reply_text(f"Вы победили {monster_name}!")
            level_up(user_id)
            await update.message.reply_text(f"Ваш уровень повышен! Уровень: {players[user_id]['level']}\n"
                                          f"❤️ Здоровье: {players[user_id]['health']}\n"
                                          f"Атака: {players[user_id]['attack']}")
            # Награждаем игрока случайной одеждой
            if random.choice([True, False]):  # 50% шанс выпадения одежды
                cloth_name = random.choice(list(clothes.keys()))
                players[user_id]['inventory'].append(cloth_name)
                await update.message.reply_text(f"Вы получили {cloth_name}!")
            # Сбрасываем текущего монстра
            players[user_id]['current_monster'] = None
            await main_menu(update, context)
            return

        if players[user_id]['health'] <= 0:
            await update.message.reply_text(f"⚰️ Вы погибли в бою с {monster_name}!")
            # Возрождение в городе
            players[user_id]['health'] = 100  # Восстанавливаем здоровье
            players[user_id]['location'] = '🏙️ Город'
            await update.message.reply_text("Вы возродились в городе!")
            await heal(update, context)
            # Сбрасываем текущего монстра
            players[user_id]['current_monster'] = None
            await main_menu(update, context)
            return


# Команда для восстановления здоровья в городе
async def heal(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in players:
        await update.message.reply_text("🟢 Сначала создайте персонажа с помощью /create.")
        return

    if players[user_id]['location'] != '🏙️ Город':
        await update.message.reply_text("🏙️ Вы не в городе. Перейдите в город, чтобы восстановить здоровье.")
        return

    # Восстанавливаем здоровье до максимума
    players[user_id]['health'] = 100 + (players[user_id]['level'] - 1) * 10
    await update.message.reply_text("🧠 Ваше здоровье восстановлено!")
    await main_menu(update, context)

item_effects = {
    'small_potion': {'health': 10},
    # Добавьте больше предметов и их эффектов по необходимости
}

async def use_item(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in players:
        await update.message.reply_text("???? Сначала создайте персонажа с помощью /create.")
        return

    message_text = update.message.text
    parts = message_text.split()
    if len(parts) < 2:
        await update.message.reply_text("???? Используйте: /use_item <имя_предмета>")
        return

    item_name = parts[1]

    player = players[user_id]
    inventory = player.get('inventory', [])

    if item_name not in inventory:
        await update.message.reply_text(f"???? Предмета {item_name} нет в инвентаре.")
        return

    if item_name not in item_effects:
        await update.message.reply_text(f"???? Предмет {item_name} не может быть использован.")
        return

    effect = item_effects[item_name]

    # Применение эффекта
    if 'health' in effect:
        player['health'] += effect['health']
        if player['health'] > 100:  # Пример максимального здоровья
            player['health'] = 100
        await update.message.reply_text(f"???? Вы восстановили здоровье на {effect['health']}.")
    # Добавьте обработку других эффектов по необходимости

    # Удаление предмета из инвентаря
    inventory.remove(item_name)
    player['inventory'] = inventory

    await update.message.reply_text(f"???? Предмет {item_name} использован.")

# Команда для перехода в город
async def go_to_town(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in players:
        await update.message.reply_text("🟢 Сначала создайте персонажа с помощью /create.")
        return

    players[user_id]['location'] = '🏙️ Город'
    await update.message.reply_text("🏙️ Вы находитесь в Городе. Здесь вы можете восстановить здоровье.")
    await heal(update, context)
    await main_menu(update, context)

item_categories = {
    'small_potion': 'зелья',
    'sword': 'оружие',
    'shield': 'броня',
    # Добавьте больше предметов по необходимости
}

# Команда для получения состояния персонажа
async def status(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in players:
        await update.message.reply_text("Сначала создайте персонажа с помощью /create.")
        return

    player = players[user_id]
    
    # Добавляем проверки для обратной совместимости
    if 'equipped' not in player:
        player['equipped'] = {'weapon': None, 'armor': None}
    if 'max_health' not in player:
        player['max_health'] = 100
        
    equipped_weapon = player['equipped']['weapon'] or "Нет"
    equipped_armor = player['equipped']['armor'] or "Нет"
    inventory = "\n".join(player['inventory']) if player['inventory'] else "Пусто"

    attack = player['attack']
    if player['equipped']['weapon']:
        attack += weapons[player['equipped']['weapon']]['attack_bonus']

    await update.message.reply_text(
        f"Имя: {player['name']}\n"
        f"Уровень: {player['level']}\n"
        f"❤️ Здоровье: {player['health']}/{player['max_health']}\n"
        f"🗡 Атака: {player.get('attack_range', player['attack'])}\n"
        f"🛡 Защита: {player['defense']}\n"
        f"📍 Локация: {player['location']}\n"
        f"⚔ Экипировка:\n"
        f"  Оружие: {equipped_weapon}\n"
        f"  Броня: {equipped_armor}\n"
        f"🎒 Инвентарь:\n{inventory}"
    )
    await main_menu(update, context)

# Команда для приручения зверя
async def get_pet(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in players:
        await update.message.reply_text("🟢 Сначала создайте персонажа с помощью /create.")
        return

    keyboard = []
    for pet_name, pet_info in pets.items():
        keyboard.append([InlineKeyboardButton(f"{pet_name}", callback_data=f"get_pet_{pet_name}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🦾 Какого зверя вы хотите приручить?", reply_markup=reply_markup)

# Callback для приручения зверя
async def pet_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    data_parts = query.data.split('_')
    if len(data_parts) < 2:
        await query.edit_message_text("Ошибка в данных.")
        return
    pet_name = data_parts[1]

    if user_id not in players:
        await query.edit_message_text("🟢 Сначала создайте персонажа с помощью /create.")
        return

    # Шанс приручения 50%
    success = random.choice([True, False])
    if success:
        players[user_id]['pet'] = pet_name
        await query.edit_message_text(f"🎉 Вы успешно приручили {pet_name}!")
    else:
        await query.edit_message_text(f"⚰️ Неудачное приручение {pet_name}!")
    await main_menu(update, context)

# Команда для одевания одежды
async def wear_cloth(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in players:
        await update.message.reply_text("Сначала создайте персонажа с помощью /create.")
        return

    keyboard = []
    for cloth_name, cloth_info in clothes.items():
        keyboard.append([InlineKeyboardButton(cloth_name, callback_data=f"wear_{cloth_name}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите одежду для надевания:", reply_markup=reply_markup)

async def send_notification(user_id, message):
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🔔 Уведомление: {message}"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {e}")

# Callback для обработки надевания одежды
async def wear_cloth_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    cloth_name = query.data.split('_')[1]

    if user_id not in players:
        await query.edit_message_text("Сначала создайте персонажа с помощью /create.")
        return

    player = players[user_id]
    
    # Проверяем наличие предмета в инвентаре
    if cloth_name not in player['inventory']:
        await query.edit_message_text("❌ Этого предмета нет в вашем инвентаре.")
        return

    # Проверяем что предмет является броней
    if cloth_name not in clothes:
        await query.edit_message_text("❌ Это нельзя экипировать как броню.")
        return

    # Экипируем через общую систему
    try:
        context.args = [cloth_name]
        await equip_item(update, context)
        await query.edit_message_text(f"✅ {cloth_name} успешно экипирован!")
    except Exception as e:
        logger.error(f"Ошибка экипировки: {e}")
        await query.edit_message_text("❌ Ошибка экипировки предмета.")

    # Обновляем характеристики
    health_bonus = clothes[cloth_name]['health_bonus']
    attack_bonus = clothes[cloth_name]['attack_bonus']
    players[user_id]['health'] += health_bonus
    players[user_id]['attack'] += attack_bonus

    await main_menu(update, context)
    
# Главное меню
async def main_menu(update: Update, context: CallbackContext):
    conversation_states[update.effective_chat.id] = None
    
    keyboard = [
        ['Исследовать мир', 'Сражение'],
        ['Статус персонажа', 'Перейти в город'],
        ['Инвентарь', 'Экипировать предмет'],
        ['Гильдии', 'Турниры']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    try:
        if update.message.text == "Выберите действие:":
            await update.message.edit_text("Выберите действие:", reply_markup=reply_markup)
        else:
            await update.message.reply_text("Главное меню:", reply_markup=reply_markup)
    except:
        await update.message.reply_text("Главное меню:", reply_markup=reply_markup)

# Команда /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Добро пожаловать в игру 'Приключения в фэнтезийном мире'! Чтобы начать, создайте персонажа с помощью /create.")
    await main_menu(update, context)

def migrate_old_players():
    for user_id in list(players.keys()):
        player = players[user_id]
        
        # Мигрируем старую одежду
        if 'cloth' in player:
            for item in player['cloth']:
                if item not in player['inventory']:
                    player['inventory'].append(item)
            del player['cloth']
        
        # Инициализируем недостающие поля
        if 'equipped' not in player:
            player['equipped'] = {
                'weapon': None,
                'armor': None
            }
        if 'max_health' not in player:
            player['max_health'] = 100
        if 'defense' not in player:
            player['defense'] = 5

# Основная функция для запуска бота
def main():
    # Токен вашего бота (замените на свой)
    token = 'СЮДА ТОКЕН БОТА'
    application = Application.builder().token(token).build()
    
    # Добавить планировщик
    job_queue = application.job_queue
    job_queue.run_repeating(tournament_scheduler, interval=3600, first=10)
    job_queue.run_repeating(world_event_scheduler, interval=600, first=5)
    job_queue.run_repeating(lambda _: save_game(), interval=300)
    
    # Обработчики команд
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('create', create_character))
    application.add_handler(CommandHandler('explore', explore))
    application.add_handler(CommandHandler('fight', fight))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CommandHandler('heal', heal))
    application.add_handler(CommandHandler('wear_cloth', wear_cloth))
    application.add_handler(CommandHandler('create_guild', create_guild))
    application.add_handler(CommandHandler('join_guild', join_guild))
    application.add_handler(CommandHandler('guild_info', guild_info))
    application.add_handler(CommandHandler('show_world_events', show_world_events))
    application.add_handler(CommandHandler('join_tournament', join_tournament))
    application.add_handler(CommandHandler('tournament_info', tournament_info))
    application.add_handler(CommandHandler('use_potion', use_potion))
    application.add_handler(CommandHandler('equip_item', equip_item))
    application.add_handler(CommandHandler('equip', equip_item))
    application.add_handler(CommandHandler('show_inventory', show_inventory))
    application.add_handler(CallbackQueryHandler(wear_cloth_callback, pattern='^(wear_)'))
    application.add_handler(CallbackQueryHandler(pet_callback, pattern='^(get_pet_)'))
    application.add_handler(CallbackQueryHandler(equip_item_callback, pattern='^equip_'))

    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.Text() & ~filters.Command(), handle_message))
    application.add_error_handler(error_handler)
    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
#    load_game()
    migrate_old_players()
    main()