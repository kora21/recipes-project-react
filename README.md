## Продуктовый помощник - foodgram

Foodgram - продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, подписываться на других авторов, а также формировать список покупок для выбранных рецептов.

Проект доступен http://158.160.72.124/   https://foods.hopto.org

### Документация API проекта:
http://recipebook.hopto.org/api/docs/redoc.html

```
Админ:
Login: admin
Password: admin
```

### Технологии:

Python 3.9, Django 3.2, DRF 3.13, Nginx, Docker, Docker-compose, Postgresql, Github Actions

[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=cd5c5c)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=0095b6)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=cd5c5c)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=0095b6)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=cd5c5c)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=0095b6)](https://gunicorn.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=cd5c5c)](https://www.docker.com/)
[![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=0095b6)](https://www.docker.com/)
[![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=cd5c5c)](https://www.docker.com/products/docker-hub)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat&logo=GitHub%20actions&logoColor=56C0C0&color=0095b6)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat&logo=Yandex.Cloud&logoColor=56C0C0&color=cd5c5c)](https://cloud.yandex.ru/)

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

Для полноценного использования API необходимо выполнить регистрацию пользователя и получить токен. 

Регистрируем нового пользователя: 
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
**`POST` | http://localhost/api/auth/token/login/
```json
{
    "password": "",
    "email": ""
}
```
Response status 200 OK
```json
{
    "token": "abcd..........."
}
```
Полученный токен вставляем Postman -> закладка Headers -> Key(Authorization) -> Value (Ваш токен в формате: Token abcd....)  


### Примеры запросов:

**`GET` | Получение ингредиента: `http://localhost:8000/api/ingredients/`**

Response:
```
{
  "id": 0,
  "name": "Капуста",
  "measurement_unit": "кг"
}
```

**`GET` | Получение тэгов: `http://localhost:8000/api/tags/`**

Response:
```
{
  "id": 0,
  "color": "H#17..",
  "slug "breakfast"
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

**`GET` | Получить список рецептов: `http://localhost:8000/api/recipes/`**

Response:
```
{
        "tags": [
            {
                "id": 3,
                "name": "ужин",
                "color": "#7da8ef",
                "slug": "dinner"
            }
        ],
        "ingredients": [
            {
                "id": 14,
                "name": "макаронные изделия",
                "measurement_unit": "г",
                "amount": 500
            },
            {
                "id": 15,
                "name": "кабачки",
                "measurement_unit": "г",
                "amount": 250
            },
            {
                "id": 16,
                "name": "перец",
                "measurement_unit": "г",
                "amount": 200
            },
            {
                "id": 17,
                "name": "пармезан",
                "measurement_unit": "г",
                "amount": 100
            },
            {
                "id": 18,
                "name": "моцарелла",
                "measurement_unit": "г",
                "amount": 100
            },
            {
                "id": 19,
                "name": "сельдерей",
                "measurement_unit": "г",
                "amount": 100
            }
        ],
        "author": {
            "email": "admin1@mail.ru",
            "id": 1,
            "username": "admin",
            "first_name": "",
            "last_name": "",
            "is_subscribed": false
        },
        "id": 4,
        "name": "Вегетарианская лазанья",
        "image": "http://158.160.72.124/media/recipe/a31a19e0-77b6-49fc-8c17-6d1eb3526ab2.jpg",
        "text": "Яркая, до краев наполненная солнцем, сочными овощами, тягучей моцареллой и пряными травами. Отличная итальянская классика конца лета – начала осени.",
        "cooking_time": 50,
        "is_favorited": false,
        "is_in_shopping_cart": false
    },
```

### Автор:
[Ekaterina Tarasenko](https://github.com/kora21/)
