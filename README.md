# Video Index Hackaton 2024 Yappy

## Развертывание
Инструкция по развертыванию

Установка библиотеки ffmpeg
```
apt update
apt install -y ffmpeg
```

Зависимости python
```
elasticsearch==8.14.0
elastic-transport==8.13.1
ffmpeg==1.4
Flask==3.0.3
Flask-RESTful==0.3.10
flask-swagger-ui==4.11.1
gunicorn==22.0.0
psycopg2-binary==2.9.9
openai-whisper==20231117
flask_swagger_ui
flask_cors
python_dotenv==1.0.1
```

### Запуск миграции БД
Структура БД находится в файле migrations.sql, можно напрямую выполнить в postgres.

### Создание индекса Elasticsearch
Для создания индекса и индексации (или переиндексации) имеющихся в БД распознанных видео, нужно запустить файл indexer.py.
```
python indexer.py
```

### Конфигурация python
Нужно скопировать файл .env.example в .env и внести в него необходимые изменения
```
cp .env.example .env
```

### Настройка воркера
Воркер должен быть постоянно запущен, для этого нужно прописать настройки supervisor.conf.
```
apt install supervisor
cp supervisor.conf /etc/supervisor/conf.d
supervisorctl update
```

Воркер можно запустить напрямую из консоли 
```
python worker.py
```

Воркер беред из БД 100 записей и обрабатывает их синхронно. Пакетная обработка сделана для экономии оперативной памяти и времени выполнения при загрузке модели распознавания, которая в активном режиме может потреблять до 10GB оперативной памяти.
После разпознавания каждой записи происходит запись в индекс и запись в БД.


## Использование

Сссылка на документацию Swagger http://185.50.202.156:8080/swagger/

### Загрузка одного видео
```
POST /api/upload
Content-Type: application/json
{
    "link": "link_1",
    "description": "desc"
}
```

При успешном выполнении получим
```json
{
    "success": true
}
```

### Загрузка нескольких видео
Максимальное количество записей для загрузки = 100, иначе получим ошибку "The maximum number of entries should be no more than 100"
```
POST /api/upload
Content-Type: application/json
[{
    "link": "link_1",
    "description": "desc"
}, {
    "link": "link_2",
    "description": "desc"
}]
```

При успешном выполнении получим
```json
{
    "success": true
}
```

### Запрос на поиск
```
GET /api/search?query=query_text
Content-Type: application/json
```

При успешном выполнении получим
```json
{
    "results": [
        {
            "description": "",
            "link": "",
            "speech": ""
        }
    ]
}
```

### Запрос на автокомплит
```
GET /api/autocomplete?query=query_text
Content-Type: application/json
```

При успешном выполнении получим
```json
{
    "results": [
        {
            "text": ""
        }
    ]
}
```
