# ФСТР Перевалы — REST API

## Описание задачи

Федерация спортивного туризма России (ФСТР) собирает данные о горных перевалах
от туристов через мобильное приложение. Приложение по нажатию кнопки «Отправить»
вызывает REST API, реализованный в этом проекте, чтобы сохранить данные
о перевале в базу данных для последующей модерации сотрудниками ФСТР.

## Что реализовано

- Спроектирована и нормализована база данных PostgreSQL (`final_db`):
  таблицы `users`, `coords`, `pereval_images`, `pereval_added`, связка
  `pereval_images_link` — вместо хранения перевала одним большим JSON-полем,
  как это было в исходной схеме ФСТР.
- Класс `PerevalDAO` — инкапсулирует всю работу с БД (создание, чтение,
  обновление, сериализация перевалов).
- REST API на Django (без DRF) с четырьмя методами:
  - `POST /api/submitData/` — добавить новый перевал
  - `GET /api/submitData/<id>/` — получить перевал по id
  - `PATCH /api/submitData/<id>/` — отредактировать перевал (только в статусе `new`)
  - `GET /api/submitData/?user__email=<email>` — список перевалов пользователя
- Решение задеплоено на Yandex Cloud (Compute Cloud VM + PostgreSQL + Gunicorn + Nginx).
- Код покрыт тестами (Django TestCase).
- Документация в формате Swagger/OpenAPI.

## Стек технологий

- Python 3.12, Django 4.2
- PostgreSQL 15+
- Gunicorn + Nginx (деплой)
- Swagger UI (документация API)

## Развёртывание проекта локально

```bash
git clone <ссылка на репозиторий>
cd restapi
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Создать файл `.env` в корне проекта:
FSTR_DB_HOST=localhost
FSTR_DB_PORT=5432
FSTR_DB_LOGIN=<логин>
FSTR_DB_PASS=<пароль>

Применить миграции и запустить сервер:

```bash
python manage.py migrate
python manage.py runserver
```

## API — примеры вызова

Хостинг: `http://89.232.188.78`

### 1. Добавление нового перевала — POST /api/submitData/

```powershell
$body = @{
    beauty_title = "пер. "
    title = "Пхия"
    other_titles = "Триев"
    connect = ""
    add_time = "2021-09-22 13:18:13"
    user = @{
        email = "qwerty@mail.ru"
        fam = "Пупкин"
        name = "Василий"
        otc = "Иванович"
        phone = "+7 555 55 55"
    }
    coords = @{ latitude = "45.3842"; longitude = "7.1525"; height = "1200" }
    level = @{ winter = ""; summer = "1А"; autumn = "1А"; spring = "" }
    images = @(@{ data = "img1base64"; title = "Седловина" })
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri "http://89.232.188.78/api/submitData/" -Method Post -Body $body -ContentType "application/json; charset=utf-8"
```

Ответ:
```json
{ "status": 200, "message": null, "id": 1 }
```

### 2. Получение перевала по id — GET /api/submitData/<id>/

```powershell
Invoke-RestMethod -Uri "http://89.232.188.78/api/submitData/1/" -Method Get
```

Ответ:
```json
{
  "id": 1,
  "status": "new",
  "beauty_title": "пер. ",
  "title": "Пхия",
  "other_titles": "Триев",
  "connect": "",
  "add_time": "2021-09-22T13:18:13Z",
  "user": { "email": "qwerty@mail.ru", "fam": "Пупкин", "name": "Василий", "otc": "Иванович", "phone": "+7 555 55 55" },
  "coords": { "latitude": 45.3842, "longitude": 7.1525, "height": 1200 },
  "level": { "winter": "", "summer": "1А", "autumn": "1А", "spring": "" },
  "images": [{ "id": 1, "title": "Седловина", "data": "img1base64" }]
}
```

### 3. Редактирование перевала — PATCH /api/submitData/<id>/

```powershell
$body = @{ title = "Новое название перевала" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://89.232.188.78/api/submitData/1/" -Method Patch -Body $body -ContentType "application/json; charset=utf-8"
```

Ответ (успех):
```json
{ "state": 1, "message": "Запись успешно обновлена" }
```

Ответ (если статус уже не `new`):
```json
{ "state": 0, "message": "Редактирование запрещено: статус записи \"accepted\", а не \"new\"" }
```

### 4. Список перевалов пользователя — GET /api/submitData/?user__email=<email>

```powershell
Invoke-RestMethod -Uri "http://89.232.188.78/api/submitData/?user__email=qwerty@mail.ru" -Method Get
```

Ответ — массив объектов в том же формате, что и в примере п. 2.

## Документация Swagger

Интерактивная документация доступна по адресу:
`http://89.232.188.78/api/docs/`

## Тесты

```bash
python manage.py test
```