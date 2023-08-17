## Продуктовый помощник - foodgram

![workflow](https://github.com/kora21/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

Foodgram - продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, подписываться на других авторов, а также формировать список покупок для выбранных рецептов.

Проект доступен по [адресу](https://foodrams.hopto.org)

```bash
# Админ зона
Login: admin1
Password: admin 

### Технологии:

Python 3.9, Django 3.2, DRF 3.13, Nginx, Docker, Docker-compose, Postgresql, Github Actions.

### Развернуть проект на удаленном сервере:

Клонировать репозиторий:
```
https://github.com/kora21/foodgram-project-react.git
```

Установить на сервере Docker, Docker Compose:

```
sudo apt install curl                                   # установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      # скачать скрипт для установки
sh get-docker.sh                                        # запуск скрипта
sudo apt-get install docker-compose-plugin              # последняя версия docker compose
```

Скопировать на сервер файлы docker-compose.yml, nginx.conf из папки infra (команды выполнять находясь в папке infra):

```
scp docker-compose.yml nginx.conf username@IP:/home/username/   # username - имя пользователя на сервере
                                                                # IP - публичный IP сервера
```

Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:
```
SECRET_KEY              # секретный ключ Django проекта
DOCKER_PASSWORD         # пароль от Docker Hub
DOCKER_USERNAME         # логин Docker Hub
HOST                    # публичный IP сервера
USER                    # имя пользователя на сервере
PASSPHRASE              # *если ssh-ключ защищен паролем
SSH_KEY                 # приватный ssh-ключ
TELEGRAM_TO             # ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          # токен бота, посылающего сообщение

DB_ENGINE               # django.db.backends.postgresql
DB_NAME                 # django
POSTGRES_USER           # django_user
POSTGRES_PASSWORD       # mysecretpassword
DB_HOST                 # db
DB_PORT                 # 5432 (порт по умолчанию)
```

Создать и запустить контейнеры Docker, выполнить команду на сервере
*(версии команд "docker compose" или "docker-compose" отличаются в зависимости от установленной версии Docker Compose):*
```
sudo docker compose up -d
```

После успешной сборки выполнить миграции:
```
sudo docker compose exec backend python manage.py migrate
```

Создать суперпользователя:
```
sudo docker compose exec backend python manage.py createsuperuser
```

Собрать и копировать статику:
```
sudo docker compose exec backend python manage.py collectstatic --noinput
```

```
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

Наполнить базу данных содержимым из файла ingredients.json:
```
sudo docker compose exec backend python manage.py load_ingredients
```

Для остановки контейнеров Docker:
```
sudo docker compose down -v      # с их удалением
sudo docker compose stop         # без удаления
```

### Запуск проекта на локальной машине:

Клонировать репозиторий:
```
https://github.com/kora21/foodgram-project-react.git
```

В директории infra файл example.env переименовать в .env и заполнить своими данными:
```
DB_ENGINE               # django.db.backends.postgresql
DB_NAME                 # django
POSTGRES_USER           # django_user
POSTGRES_PASSWORD       # mysecretpassword
DB_HOST                 # db
DB_PORT                 # 5432 (порт по умолчанию)
```

Создать и запустить контейнеры Docker, последовательно выполнить команды по созданию миграций, сбору статики, 
созданию суперпользователя, как указано выше.
```
docker-compose -f docker-compose-local.yml up -d
```


После запуска проект будут доступен по адресу: [http://localhost/](http://localhost/)

**POSTMAN**  
Для полноценного использования API необходимо выполнить регистрацию пользователя и получить токен. Инструкция для ***Postman:***

Получить токен для тестового пользователя если выполнены все импорты:  
POST http://localhost/api/auth/token/login/
```json
{
    "email": "",
    "password": ""
}
```
Без импортов, регистрируем нового пользователя  
POST http://localhost/api/users/
```json
{
    "email": "",
    "username": "",
    "first_name": "",
    "last_name": "",
    "password": ""
}
```
Получаем токен  
POST http://localhost/api/auth/token/login/
```json
{
    "password": "",
    "email": ""
}
```
Response status 200 OK ✅
```json
{
    "token": "abcd..........."
}
```
Полученный токен вставляем Postman -> закладка Headers -> Key(Authorization) -> Value (Ваш токен в формате: Token abcd....)  


### Примеры запросов:

**`POST` | Создание рецепта: `http://127.0.0.1:8000/api/recipes/`**

Request:
```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```

Response:
```
{
  "count": 123,
  "next": "http://foodgram.example.org/api/recipes/?page=4",
  "previous": "http://foodgram.example.org/api/recipes/?page=2",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "color": "#E26C2D",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Картофель отварной",
          "measurement_unit": "г",
          "amount": 1
        }
      ],
      "is_favorited": true,
      "is_in_shopping_cart": true,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "text": "string",
      "cooking_time": 1
    }
  ]
}
```

**`GET` | Получение ингредиента: `http://localhost:8000/api/ingredients/{id}/`**

Response:
```
{
  "id": 0,
  "name": "Капуста",
  "measurement_unit": "кг"
}

```

**`POST` | Добавить рецепт в избранное: `http://localhost:8000/api/recipes/{id}/favorite/`**

Response:
```
{
  "id": 0,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "cooking_time": 1
}
```


**`GET` | Получить список пользователей: `http://localhost:8000/api/users/`**

Response:
```
{
  "count": 123,
  "next": "http://foodgram.example.org/api/users/?page=4",
  "previous": "http://foodgram.example.org/api/users/?page=2",
  "results": [
    {
      "email": "user@example.com",
      "id": 0,
      "username": "string",
      "first_name": "Вася",
      "last_name": "Пупкин",
      "is_subscribed": false
    }
  ]
}

```

### Автор:

Екатерина Тарасенко
