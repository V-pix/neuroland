# Neuroland - приложение для сети обучающих центров Нейроленд

## Оглавление
- [Описание проекта](#description)
- [Используемые технологии](#technologies)
- [Установка и запуск проекта](#launch)
- [Наполнение Базы Данных городами](#cities)

<a id=description></a>
## Описание проекта
В приложении реализована возможность посмотра видео уроков, начисления бонусных баллов за просмотр промо роликов, покупки купонов за бонусные баллы, вывода приоретеных купонов на странице профиля пользователя.
### К API есть документация по адресу `http://localhost:8000/swagger`
---
<a id=technologies></a>
## Используемые технологии:
- Python 3.7
- Django 3.2.18
- Django REST Framework 3.14.0

<a id=launch></a>
## Установка и запуск проекта

### Клонируйте репозиторий и перейдите в его директорию:
```bash
git clone git@github.com:Development-AppBroseph/backend_neuroland.git
```

### Перейдите в директорию проекта:
```bash
cd backend_neuroland 
```
Создайте в директории .env файл с переменными окружения:
- SECRET_KEY=
- SECRET_KEY_ALFA=
- API_KEY=
- X-APP-KEY=
- EMAIL=
- APP_ID = 
- REST_API_KEY =
- DEFAULT_FROM_EMAIL = 

### Cоздать виртуальное окружение:
```bash
python3 -m venv venv
```
### Активировать виртуальное окружение:
```bash
source venv/bin/activate        # для Linux
source venv/Scripts/activate    # для Windows
```
### Установить зависимости из файла requirements.txt:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```
### Выполнить миграции:
```bash
python manage.py migrate
```
### Создать суперпользователя:
```bash
python manage.py createsuperuser
```
### Запустить проект:
```bash
python manage.py runserver
```
<a id=cities></a>
## Наполнение Базы Данных городами

Подготовлен файл с городами России.
Для наполнения базы данных выполните команду

```sh
python manage.py import_cities
```