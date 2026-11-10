# Книжный каталог — лабораторная №7

Морозова Анастасия Алексеевна, группа 221341, вариант 3, лабораторная №7.
Методические указания, часть 1, страницы 13–14.

## Как посмотреть результат

Из папки проекта в PowerShell с Python 3.12:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-test.txt
.\.venv\Scripts\python.exe main.py
```

Запуск без аргументов создаёт временную базу, показывает выборку и удаление,
записывает CSV и убирает временные файлы по завершении.

## Средние задания №3, №5 и №9

Прямые запросы с параметрами находятся в `library.py`. Консоль и API работают
с одним файлом `library.sqlite3`. Пример с постоянной базой:

```powershell
.\.venv\Scripts\python.exe main.py init
.\.venv\Scripts\python.exe main.py add 'Два капитана' 'Вениамин Каверин' --pages 640
.\.venv\Scripts\python.exe main.py select --author 'Вениамин Каверин'
.\.venv\Scripts\python.exe main.py export books.csv
.\.venv\Scripts\python.exe main.py delete 1
```

Для удаления используйте фактический номер из вывода `select`.
Экспорт создаёт новый CSV в UTF-8 с BOM. Для повтора укажите новое имя.
`READING_DB` задаёт другой файл для консоли, API и миграций.

## Повышенное №3 — миграции

Версия `100` создаёт каталог с названием и автором. Версия `110` добавляет
число страниц. Для ранее сохранённых книг оно остаётся неизвестным.
Откат к `100` сохраняет названия и авторов, поле страниц удаляется.

```powershell
$env:READING_DB = 'migration-demo.sqlite3'
.\.venv\Scripts\python.exe -m alembic upgrade 100
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m alembic downgrade 100
Remove-Item Env:READING_DB
```

## Повышенное №7 — FastAPI и SQLAlchemy

```powershell
.\.venv\Scripts\python.exe main.py init
.\.venv\Scripts\python.exe -m uvicorn api:app
```

В Swagger UI на `http://127.0.0.1:8000/docs` доступны выборка `/books`,
фильтр `author`, чтение книги по ID, добавление и удаление. Число страниц
меняется через `PATCH /books/{id}/pages` с JSON `{"pages": 640}`.
Например, для добавления книги отправьте в `POST /books` тело
`{"title": "Два капитана", "author": "Вениамин Каверин", "pages": 640}`.

Миграции, запросы SQL, экспорт и API проверяются командой `python -m unittest -v`.
