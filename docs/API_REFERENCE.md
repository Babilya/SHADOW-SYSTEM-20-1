# SHADOW SYSTEM iO v2.0 - API Reference

## Core Services

### DMSenderService
Сервіс для відправки особистих повідомлень через Telegram.

#### Methods

##### `create_task(task_id, name, message_template, target_users, **kwargs)`
Створює нову задачу на розсилку DM.

**Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `task_id` | `str` | Yes | Унікальний ID задачі |
| `name` | `str` | Yes | Назва задачі |
| `message_template` | `str` | Yes | Шаблон повідомлення |
| `target_users` | `List[int]` | Yes | Список Telegram ID користувачів |
| `bot_sessions` | `List[str]` | No | Хеші сесій для ротації |
| `interval_min` | `float` | No | Мінімальний інтервал (сек), default: 30.0 |
| `interval_max` | `float` | No | Максимальний інтервал (сек), default: 60.0 |
| `personalization` | `bool` | No | Персоналізація, default: True |

**Returns:** `DMTask`

**Example:**
```python
from core.dm_sender import dm_sender_service

task = dm_sender_service.create_task(
    task_id="campaign-001",
    name="Welcome Campaign",
    message_template="Привіт, {name}! Як справи?",
    target_users=[123456, 789012],
    interval_min=45.0,
    interval_max=90.0
)
```

##### `async start_task(task_id)`
Запускає задачу на виконання. **Асинхронний метод.**

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `task_id` | `str` | ID задачі |

**Returns:** `Dict[str, Any]` з полями `status`, `task_id`, `total_users` або `error`

**Example:**
```python
result = await dm_sender_service.start_task("campaign-001")
```

##### `async stop_task(task_id)`
Зупиняє виконання задачі. **Асинхронний метод.**

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `task_id` | `str` | ID задачі |

**Returns:** `Dict[str, Any]` з полями `status` або `error`

**Example:**
```python
result = await dm_sender_service.stop_task("campaign-001")
```

##### `get_task_status(task_id)`
Отримує статус задачі.

**Returns:** `Dict` з полями:
- `name`: Назва
- `status`: Статус (pending/sending/paused/completed/failed)
- `total_targets`: Кількість цілей
- `sent_count`: Відправлено
- `failed_count`: Помилок
- `progress`: Прогрес у %

---

### GroupParserService
Сервіс для парсингу учасників груп та каналів Telegram.

#### Methods

##### `parse_group(group_id, filters, session_hash)`
Парсить учасників групи.

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `group_id` | `int/str` | ID або username групи |
| `filters` | `List[ParserFilter]` | Фільтри |
| `session_hash` | `str` | Хеш сесії Telethon |

**Returns:** `List[ParsedUser]`

##### `save_list(name, users)`
Зберігає список користувачів.

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `name` | `str` | Назва списку |
| `users` | `List[ParsedUser]` | Список користувачів |

**Returns:** `str` - ID списку

##### `export_to_user_ids(list_id)`
Експортує список у масив ID для розсилки.

**Returns:** `List[int]`

#### ParserFilter Enum
- `ALL` - Всі учасники
- `WITH_USERNAME` - Тільки з username
- `ACTIVE_RECENTLY` - Активні останнім часом
- `PREMIUM_ONLY` - Тільки Premium
- `NOT_BOTS` - Без ботів

---

### FloodMonitor
Моніторинг flood-подій Telegram.

#### Methods

##### `record_event(flood_type, session_id, wait_seconds, task_id)`
Записує flood-подію.

**FloodType Enum:**
- `FLOOD_WAIT` - FloodWaitError
- `PEER_FLOOD` - PeerFloodError
- `PRIVACY_RESTRICTED` - UserPrivacyRestrictedError
- `USER_BANNED` - UserBannedError
- `SESSION_EXPIRED` - SessionExpiredError

##### `get_session_status(session_id)`
Отримує статус сесії.

**Returns:** `Dict` з полями:
- `status`: ok/warning/critical
- `recent_floods`: Кількість за годину
- `total_wait_seconds`: Загальний час очікування

##### `get_active_alerts(severity=None)`
Отримує активні алерти.

**Returns:** `List[FloodAlert]`

##### `get_report()`
Генерує HTML звіт.

**Returns:** `str`

---

### StructuredLogger
Структуроване логування з метриками.

#### Methods

##### `info(category, message, **kwargs)`
Логує інформаційне повідомлення.

**LogCategory Enum:**
- `SECURITY` - Безпека
- `CAMPAIGN` - Кампанії
- `OSINT` - OSINT
- `BOT` - Боти
- `DM` - DM розсилки
- `PARSER` - Парсинг
- `FLOOD` - Flood події
- `SYSTEM` - Система

##### `log_flood_event(session_id, wait_seconds, task_id)`
Логує flood-подію.

##### `log_dm_sent(task_id, target_user_id, session_id, duration_ms)`
Логує успішну відправку DM.

##### `get_metrics()`
Отримує метрики логування.

**Returns:** `Dict`

---

## Database Models

### BotSession
Модель бот-сесії.

#### Fields
| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Primary key |
| `session_hash` | `str` | Хеш сесії |
| `phone` | `str` | Номер телефону |
| `status` | `str` | Статус |
| `is_active` | `bool` | Активна |
| `success_rate` | `float` | Успішність % |
| `messages_sent` | `int` | Відправлено |
| `messages_failed` | `int` | Помилок |
| `flood_wait_until` | `datetime` | Очікування до |

#### Methods

##### `is_available()`
Перевіряє доступність сесії.

**Returns:** `bool`

##### `update_statistics(success)`
Оновлює статистику після відправки.

---

## Handlers

### Parsing Handler
Callbacks for group parsing UI.

| Callback | Description |
|----------|-------------|
| `parsing_main` | Головне меню парсингу |
| `parse_group` | Вибір групи |
| `parse_filter_*` | Вибір фільтру |
| `save_parsed_list` | Збереження списку |
| `dm_from_list_*` | Створення DM задачі |

### DM Handler
Callbacks for DM sending.

| Callback | Description |
|----------|-------------|
| `dm_tasks_list` | Список задач |
| `dm_task_status_*` | Статус задачі |
| `dm_stop_*` | Зупинка задачі |

---

## Error Handling

### Flood Errors
Система обробляє наступні Telethon помилки:

```python
from telethon.errors import (
    FloodWaitError,      # Очікування N секунд
    PeerFloodError,      # Ліміт peer-ів
    UserPrivacyRestrictedError  # Приватність
)
```

**Поведінка:**
- `FloodWaitError`: Пауза на `e.seconds`, max 3 спроби
- `PeerFloodError`: 5хв пауза, max 3 спроби
- `UserPrivacyRestrictedError`: Додати до blacklist

---

## Configuration

### Thresholds (FloodMonitor)
```python
thresholds = {
    "floods_per_session_warn": 3,
    "floods_per_session_critical": 5,
    "floods_per_task_warn": 5,
    "floods_per_task_critical": 10,
    "wait_seconds_warn": 300,
    "wait_seconds_critical": 600,
    "window_minutes": 60
}
```

### DM Intervals
```python
interval_min: int = 30  # seconds
interval_max: int = 60  # seconds
cooldown_hours: int = 24  # per user
```
