## Описание проекта

Новостной сайт, на котором можно читать и создавать новости или статьи.

## Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/Danil-Derkachev/NewsPortal.git
```

2. Установите необходимые зависимости:

```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` в корневой директории проекта и добавьте следующие переменные окружения:

```
FSTR_DB_NAME = имя базы данных postgres
FSTR_DB_USER = имя пользователя postgres
FSTR_DB_PASSWORD = пароль postgres
FSTR_DB_HOST = ваш хост postgres
FSTR_DB_PORT = порт postgres
```