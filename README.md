# ReachOut CRM 🚀

Высокопроизводительный асинхронный бэкенд для CRM-системы автоматизации маркетинговых рассылок, батчевой загрузки клиентских баз и отслеживания аналитики кампаний в реальном времени.

Проект спроектирован по канонам **Clean Architecture (Чистая Архитектура)** с использованием **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL**, **Redis**, **RabbitMQ** и фоновых задач на **Celery**.

---

## 🛠️ Технологический Стек

* **Web Framework:** FastAPI (Полностью асинхронный движок, строгая валидация через Pydantic).
* **ORM:** SQLAlchemy 2.0 (Асинхронные движки, контекстные транзакции, паттерн Repository).
* **Драйвер БД:** asyncpg (Максимально быстрый нативный асинхронный клиент для PostgreSQL).
* **Миграции:** Alembic (Контроль версий структуры таблиц «код-первее»).
* **Брокер очередей:** RabbitMQ (Надежная AMQP-доставка сообщений между сервисами).
* **Фоновые задачи:** Celery (Распределенная обработка тяжелых кампаний рассылок).
* **Планировщик:** Celery Beat (Автоматический ежеминутный запуск утренних проверок именинников).
* **Кэш и Блэклист:** Redis (Высокоскоростная БД в оперативной памяти для хранения аналитики и отозванных JWT-токенов).
* **Тестирование:** PyTest (Асинхронные e2e-тесты с изоляцией транзакций через контекстные менеджеры и использованием unittest.mock).

---

## ⚙️ Инфраструктура и Настройка Баз Данных

### 1. Автоматический запуск тестовой СУБД (init-multiple-databases.sh)
Чтобы тесты не затирали реальные данные и выполнялись в изолированной «песочнице», в проекте настроен bash-скрипт инициализации официального Docker-образа Postgres. Он автоматически поднимает две независимые базы данных: боевую reachout и тестовую reachout_test.

```bash
#!/bin/bash
set -e
set -u

function create_user_and_database() {
    local database=$1
    echo "  Creating database '$database'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        CREATE DATABASE $database;
EOSQL
}

create_user_and_database "reachout_test"
```

### 2. Шаблон конфигурации окружения (.env)
Создайте файл `.env` в корневом каталоге проекта:

```ini
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=reachout

DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/reachout
TEST_ASYNC_POSTGRES_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/reachout_test

REDIS_URL=redis://redis:6379
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672//
```

---

## 🚀 Запуск и Развертывание (Docker Compose)

### 1. Поднятие всего стека контейнеров
Команда автоматически соберет и запустит API, фоновые воркеры Celery, планировщик Beat, базы данных PostgreSQL, Redis и брокер RabbitMQ:
```zsh
docker compose up --build -d
```

### 2. Применение миграций Alembic на боевую базу данных
```zsh
docker compose exec api alembic upgrade head
```

### 3. Интерактивная документация API
* Swagger UI: http://127.0.0/docs
* ReDoc альтернатива: http://127.0.0

---

## 🧪 Набор Сквозных Автотестов (Testing Suite)

Тестовое покрытие написано с использованием полностью асинхронного HTTP-клиента `httpx.AsyncClient` и механизма подмены зависимостей (Dependency Overrides) в FastAPI [5.1]. 

Изоляция транзакций через контекстные менеджеры PyTest гарантирует, что база данных `reachout_test` полностью очищается после каждого теста, предотвращая конфликты данных [5.1].

### Запуск всего пака тестов внутри контейнера:
```zsh
docker compose exec api pytest -v
```

### Сценарии верификации, покрытые тестами (test_auth.py):
* test_manager_register_success — проверка успешной регистрации менеджера и хэширования паролей.
* test_manager_register_dublicate_email_fails — проверка защиты уникальности email (400 Bad Request) [5.1].
* test_manager_login_success — верификация выдачи OAuth2 JWT-токена в формате Form Data [5.1].
* test_manager_logout_success — интеграция с Redis, проверка мгновенного отзыва токена и блокировки повторных сессий (401 Unauthorized) [5.1].
* test_add_contacts_success — проверка тяжелой батчевой ручки загрузки базы клиентов и фильтрации дубликатов.
* test_add_campaign — сквозной (e2e) тест триггера рассылки с использованием `unittest.mock.patch`, доказывающий, что API гарантированно генерирует кампанию и корректно пушит задачу в Celery [5.1].