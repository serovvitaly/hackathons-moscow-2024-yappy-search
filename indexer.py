from elasticsearch import Elasticsearch
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
ELASTIC_HOST = os.getenv("ELASTIC_HOST")
ELASTIC_USER = os.getenv("ELASTIC_USER")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")
INDEX_NAME = os.getenv("INDEX_NAME")
PGS_DBNAME = os.getenv("PGS_DBNAME")
PGS_HOST = os.getenv("PGS_HOST")
PGS_USER = os.getenv("PGS_USER")
PGS_PASSWORD = os.getenv("PGS_PASSWORD")



import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


es = Elasticsearch(
    hosts=[
        {
            'host': ELASTIC_HOST,
            'port': 9200,
            'scheme': 'https'
        }
    ],
    basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD),
    verify_certs=False
)


index_body = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 1,
        "analysis": {
            "tokenizer": {
                "edge_ngram_tokenizer": {
                    "type": "edge_ngram",
                    "min_gram": 3,
                    "max_gram": 20,
                    "token_chars": [
                        "letter",
                        "digit"
                    ]
                }
            },
            "analyzer": {
                "edge_ngram_analyzer": {
                    "type": "custom",
                    "tokenizer": "edge_ngram_tokenizer",
                    "filter": [
                        "lowercase",
                        "asciifolding",
                        "snowball",
                        "russian_stop",
                        "russian_stemmer",
                    ]
                }
            },
            "filter": {
                "snowball": {
                    "type": "snowball",
                    "language": "Russian"
                },
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_"
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian"
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "speech": {
                "type": "text",
                "analyzer": "edge_ngram_analyzer"
            },
            "description": {
                "type": "text",
                "analyzer": "edge_ngram_analyzer"
            }
        }
    }
}


if es.indices.exists(index=INDEX_NAME):
    es.indices.delete(index=INDEX_NAME)
if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME, body=index_body)


def index_data():
    conn = psycopg2.connect(
        dbname=PGS_DBNAME,
        host=PGS_HOST,
        user=PGS_USER,
        password=PGS_PASSWORD
    )
    cur = conn.cursor()

    cur.execute('SELECT id, link, description, speech, likes FROM videos WHERE speech is not null')
    records = cur.fetchall()

    for rec in records:
        doc = {
            'id': rec[0],
            'link': rec[1],
            'description': rec[2],
            'speech': rec[3],
            'likes': rec[4],
        }
        es.index(index=INDEX_NAME, id=rec[0], body=doc)


index_data()
