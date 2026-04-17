# LLM Consulting Project



##  Описание проекта



Проект реализует микросервисную архитектуру с Telegram-ботом и LLM:



- **Auth Service** — регистрация, логин, JWT

- **Bot Service** — Telegram-бот

- **Celery Worker** — асинхронная обработка задач

- **RabbitMQ** — брокер сообщений

- **Redis** — кэш / хранилище

- **OpenRouter** — генерация ответов через LLM



---



## Стек технологий



- Python 3.11

- FastAPI

- Docker + Docker Compose

- RabbitMQ

- Redis

- Celery

- OpenRouter API

- Pytest



---



## Запуск проекта



```bash

docker compose up --build
```



## После запуска



- Auth API: http://localhost:8000/docs  

- Bot API: http://localhost:8001/docs  


---



## Авторизация



Открыть Swagger:



http://localhost:8000/docs



Выполнить:



- POST /auth/register  

- POST /auth/login  



Получить `access_token`



---



##  Работа с Telegram-ботом



Отправить токен:



```

/token <JWT>

```



Задать вопрос:



```

Что такое FastAPI? (например)

```



Бот:

- принимает запрос  

- отправляет задачу в Celery  

- получает ответ от LLM  

- возвращает пользователю  



---



##  Тесты



### Auth Service



```

cd auth_service

pytest -v

```



### Bot Service



```

cd bot_service

pytest -v

```



## 📸 Скриншоты



### Docker контейнеры

![Docker](screenshots/containers.png)



---



### Swagger (Auth Service)



#### Регистрация

![Register](screenshots/register.png)



#### Логин

![Login](screenshots/login.png)



#### Проверка токена (/me)

![Me](screenshots/auth.png)



---



### Telegram бот

![Telegram](screenshots/answer.png)



---



### RabbitMQ



#### Overview

![RabbitMQ Overview](screenshots/overview.png)



#### Queues

![RabbitMQ Queues](screenshots/queues.png)



---



### Тесты



#### Auth Service

![Auth Tests](screenshots/auth_test.png)



#### Bot Service

![Bot Tests](screenshots/bot_test.png)

