

# Инструкция по настройке и модификации Telegram-бота "Приключения в фэнтезийном мире"

Эта инструкция описывает, как изменить токен бота, смыслы и значения игры, чтобы адаптировать Telegram-бота под ваши нужды. Все изменения производятся в основном файле с кодом бота (например, `bot.py`).

## 1. Изменение токена бота

Токен бота необходим для его работы в Telegram. Он задается в функции `main()` в конце файла.

### Где менять:
Найдите строку в функции `main()`:
```python
token = 'СЮДА ТОКЕН БОТА'
```

### Как менять:
1. Получите токен вашего бота от **@BotFather** в Telegram.
2. Замените строку `'СЮДА ТОКЕН БОТА'` на ваш токен, например:
   ```python
   token = '1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789'
   ```

### Примечание:
- Убедитесь, что токен хранится в безопасном месте, так как его утечка может позволить злоумышленникам управлять вашим ботом.
- Не публикуйте токен в публичных репозиториях.

## 2. Изменение игровых механик и значений

Игровые механики и значения хранятся в словарях и константах в начале файла. Вы можете изменять их, чтобы настроить баланс, предметы, монстров, локации и другие элементы игры.

### 2.1. Изменение предметов и их характеристик

#### Предметы (`item_weights`, `item_effects`, `weapons`, `clothes`, `potions`, `pets`)
- **Где менять**:
  - `item_weights` — задает вес предметов, влияющий на ограничение инвентаря.
  - `item_effects` — задает эффекты предметов (например, бонусы к атаке или защите).
  - `weapons`, `clothes`, `potions`, `pets` — словари с характеристиками оружия, одежды, зелий и питомцев.

- **Пример изменения**:
  Чтобы добавить новое оружие, например, "Магический топор", добавьте в словарь `weapons`:
  ```python
  weapons.update({
      'Магический топор': {
          'attack_bonus': random.randint(6, 12),
          'description': 'Мощный топор с магическими свойствами.',
          'type': 'weapon',
          'weight': 7
      }
  })
  ```
  Затем добавьте вес в `item_weights`:
  ```python
  item_weights['Магический топор'] = 7
  ```

- **Пример удаления**:
  Чтобы удалить предмет, например, "Кольчуга", удалите его из словарей:
  ```python
  del clothes['Кольчуга']
  del item_weights['Кольчуга']
  ```

- **Примечание**:
  - Убедитесь, что добавляемые предметы имеют уникальные названия.
  - Обновляйте связанные словари (`item_weights`, `item_effects`), чтобы избежать ошибок.

#### Ограничения инвентаря (`MAX_ITEMS`, `MAX_WEIGHT`)
- **Где менять**:
  ```python
  MAX_ITEMS = 10  # Максимальное количество предметов в инвентаре
  MAX_WEIGHT = 50  # Максимальный общий вес инвентаря
  ```
- **Как менять**:
  Измените значения, чтобы увеличить или уменьшить лимиты:
  ```python
  MAX_ITEMS = 15  # Увеличение слотов до 15
  MAX_WEIGHT = 75  # Увеличение веса до 75
  ```

### 2.2. Изменение монстров

- **Где менять**:
  Словарь `monsters` содержит характеристики монстров.

- **Пример добавления монстра**:
  Чтобы добавить нового монстра "Волк":
  ```python
  monsters['🐺 Волк'] = {
      'base_health': 45,
      'base_attack': 7,
      'description': '🐺 Быстрый хищник, обитающий в лесах.'
  }
  ```

- **Пример изменения характеристик**:
  Чтобы усилить "Дракона":
  ```python
  monsters['🐉 Дракон']['base_health'] = 150
  monsters['🐉 Дракон']['base_attack'] = 25
  ```

- **Примечание**:
  - Убедитесь, что характеристики сбалансированы с уровнем игрока (см. функцию `generate_monster`).
  - Функция `generate_monster` добавляет случайные отклонения к базовым характеристикам в зависимости от уровня игрока.

### 2.3. Изменение локаций

- **Где менять**:
  Список `locations` содержит доступные локации.

- **Пример добавления локации**:
  ```python
  locations.append('🌌 Звездная долина')
  ```

- **Пример удаления локации**:
  ```python
  locations.remove('🏜️ Пустыня')
  ```

- **Примечание**:
  - Локации влияют на команду `/explore`, которая выбирает случайную локацию.
  - Если добавляете новые локации, убедитесь, что они имеют уникальные эмодзи и названия.

### 2.4. Изменение механики турниров и мировых событий

#### Турниры (`tournaments`, `create_tournament`)
- **Где менять**:
  Функция `create_tournament` задает параметры турниров.
  ```python
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
  ```

- **Пример изменения**:
  Чтобы изменить длительность турнира на 2 часа:
  ```python
  'end_time': datetime.now() + timedelta(hours=2)
  ```
  Чтобы изменить название:
  ```python
  'name': f"Великий турнир #{len(tournaments) + 1}"
  ```

- **Периодичность турниров**:
  Периодичность задается в функции `main()`:
  ```python
  job_queue.run_repeating(tournament_scheduler, interval=3600, first=10)
  ```
  Измените `interval` (в секундах), чтобы изменить частоту турниров, например:
  ```python
  job_queue.run_repeating(tournament_scheduler, interval=7200, first=10)  # Каждые 2 часа
  ```

#### Мировые события (`world_events`, `create_world_event`)
- **Где менять**:
  Функция `create_world_event` задает типы мировых событий:
  ```python
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
  ```

- **Пример добавления события**:
  ```python
  events.append("🌠 Падение метеорита! Игроки находят редкие предметы.")
  ```

- **Пример изменения эффекта**:
  Чтобы добавить эффект к событию, модифицируйте функцию `apply_world_event_effect`:
  ```python
  def apply_world_event_effect(user_id: int, event: dict):
      if "атака" in event['event']:
          players[user_id]['attack'] *= 1.5  # Увеличение атаки на 50%
      elif "здоровье" in event['event']:
          players[user_id]['health'] = min(
              players[user_id]['max_health'],
              players[user_id]['health'] * 1.5
          )
      elif "метеорит" in event['event']:
          players[user_id]['inventory'].append('Редкий кристалл')
  ```

- **Периодичность событий**:
  Периодичность задается в `main()`:
  ```python
  job_queue.run_repeating(world_event_scheduler, interval=600, first=5)
  ```
  Измените `interval` для изменения частоты событий (например, `1200` для каждых 20 минут).

### 2.5. Изменение характеристик игрока

- **Где менять**:
  Функция `init_player` задает начальные характеристики игрока:
  ```python
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
  ```

- **Пример изменения**:
  Чтобы увеличить начальное здоровье и золото:
  ```python
  'health': 150,
  'max_health': 150,
  'gold': 200
  ```

### 2.6. Изменение механики боя

- **Где менять**:
  Функции `calculate_damage` и `battle_cycle` определяют механику боя.

- **Пример изменения урона**:
  Чтобы увеличить случайное отклонение урона:
  ```python
  async def calculate_damage(attacker, defender):
      base_attack = attacker.get('attack', 0)
      if attacker.get('equipped', {}).get('weapon'):
          weapon = weapons[attacker['equipped']['weapon']]
          base_attack += random.randint(*weapon['attack_bonus'])
      
      defense = defender.get('defense', 0)
      damage = max(1, base_attack - defense + random.randint(-5, 5))  # Изменено с (-2, 2)
      return damage
  ```

- **Примечание**:
  - Убедитесь, что изменения не делают бои слишком легкими или сложными.
  - Функция `battle_cycle` управляет пошаговым боем, где можно добавить дополнительные эффекты (например, критические удары).

### 2.7. Изменение гильдий

- **Где менять**:
  Словарь `guilds` и функции `create_guild`, `join_guild`, `guild_info` определяют механику гильдий.

- **Пример добавления характеристик гильдии**:
  Чтобы добавить репутацию гильдии:
  ```python
  guilds[guild_name] = {
      'leader': user_id,
      'members': [user_id],
      'created_at': datetime.now(),
      'level': 1,
      'reputation': 100  # Новая характеристика
  }
  ```

- **Пример изменения условий создания**:
  Чтобы ограничить создание гильдии по уровню игрока:
  ```python
  async def create_guild(update: Update, context: CallbackContext, guild_name: str):
      user_id = update.message.from_user.id
      player = players.get(user_id)
      
      if not player:
          await update.message.reply_text("❌ Персонаж не найден!")
          return

      if player['level'] < 5:  # Требуется 5 уровень
          await update.message.reply_text("❌ Нужно достичь 5 уровня для создания гильдии!")
          return
  ```

## 3. Изменение текстовых сообщений

Тексты сообщений, отправляемых игрокам, находятся в функциях, таких как `start`, `status`, `fight`, и других. Вы можете изменить их для изменения тона, стиля или языка.

- **Пример изменения**:
  Чтобы изменить приветственное сообщение:
  ```python
  async def start(update: Update, context: CallbackContext):
      await update.message.reply_text("🌟 Добро пожаловать в эпическое приключение! Создай героя с помощью /create!")
      await main_menu(update, context)
  ```

## 4. Сохранение и загрузка данных

- **Где менять**:
  Функции `save_game` и `load_game` управляют сохранением данных игроков и гильдий в файлы `players.json` и `guilds.json`.

- **Пример изменения пути сохранения**:
  ```python
  def save_game():
      with open('game_data/players.json', 'w') as f:
          json.dump(players, f)
      with open('game_data/guilds.json', 'w') as f:
          json.dump(guilds, f)
  ```

- **Примечание**:
  - Убедитесь, что директория для сохранения существует.
  - Для сохранения в базе данных вместо JSON замените функции `save_game` и `load_game` на соответствующие запросы к базе.

## 5. Тестирование изменений

1. Убедитесь, что у вас установлены необходимые библиотеки:
   ```bash
   pip install python-telegram-bot
   ```
2. Запустите бота локально:
   ```bash
   python bot.py
   ```
3. Проверьте изменения, взаимодействуя с ботом через Telegram.
4. Используйте логи (`logging`) для отладки ошибок:
   ```python
   logger.error(f"Ошибка: {str(e)}")
   ```

## 6. Деплой на сервер

Для деплоя на сервер (например, Heroku, VPS):
1. Убедитесь, что токен бота безопасно хранится (например, в переменных окружения):
   ```python
   import os
   token = os.getenv('BOT_TOKEN')
   ```
2. Установите зависимости на сервере:
   ```bash
   pip install -r requirements.txt
   ```
3. Запустите бота с помощью команды или настройте автозапуск (например, через `systemd`).

## 7. Дополнительные рекомендации

- **Сохранение целостности данных**:
  Перед внесением изменений сохраните резервную копию файлов `players.json` и `guilds.json`.
- **Балансировка**:
  Тестируйте изменения, чтобы избежать дисбаланса (например, слишком сильные монстры или предметы).
- **Логирование**:
  Используйте логи для отслеживания ошибок и активности игроков.
- **Обратная совместимость**:
  При добавлении новых полей в структуры данных (`players`, `guilds`) обновите функцию `migrate_old_players`:
  ```python
  def migrate_old_players():
      for user_id in list(players.keys()):
          player = players[user_id]
          if 'new_field' not in player:
              player['new_field'] = default_value
  ```

