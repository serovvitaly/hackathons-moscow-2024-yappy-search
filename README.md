# Video Index Hackaton 2024 Yappy

## Развертывание
Инструкция по развертыванию

```
apt update
apt install -y ffmpeg
```

Зависимости
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
```

### Запуск миграции БД

### Создание индекса Elasticsearch

## Использование

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
            "likes": 0,
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
