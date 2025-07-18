# myBlogProject

Блог-платформа на Django, разработанная в рамках учебной практики.

## Описание
Проект включает регистрацию пользователей, создание постов, комментарии, подписки и переключение тем (светлая/тёмная). Сессии кэшируются на 14 дней.

## Установка
1. Склонируйте репозиторий:
```bash
   git clone https://github.com/COTnik789/PracticaOnCafedraMyBlog.git
```

2. Создайте виртуальное окружение:
```bash
    python -m venv venv
    source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. Установите зависимости (нужен requirements.txt, см. ниже):
```bash
    pip install -r requirements.txt
```
4. Запустите миграции:
```bash
    python manage.py migrate
```

5. Запустите сервер:
```bash
    python manage.py runserver
```

Автор: Иван Головченко, ФМ-12-22