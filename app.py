from flask import Flask
from flask import jsonify
from flask import request
import psycopg2
from elasticsearch import Elasticsearch
import urllib3
from flask_cors import CORS, cross_origin
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


app = Flask(__name__)
cors = CORS(app, origins=["http://185.50.202.156:8090"])


@app.route('/api/upload', methods=["POST"])
@cross_origin()
def upload():
    try:
        conn = psycopg2.connect(
            dbname=PGS_DBNAME,
            host=PGS_HOST,
            user=PGS_USER,
            password=PGS_PASSWORD
        )
        cur = conn.cursor()

        data = request.get_json(force=True)

        if isinstance(data, list):
            if len(data) > 100:
                return jsonify({"error": 'The maximum number of entries should be no more than 100'})
            for row in data:
                cur.execute(
                    "INSERT INTO videos (link, description) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (row['link'], row['description'],)
                )
        else:
            cur.execute(
                "INSERT INTO videos (link, description) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (data['link'], data['description'],)
            )
        conn.commit()
        return jsonify({"success": True})
    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "This link already exists"})


@app.route('/api/search', methods=["GET"])
@cross_origin()
def search():
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

    query = request.args.get('query')

    search_body = {
        'from' : 0,
        'size' : 30,
        'query': {
            'multi_match': {
                'query': query,
                'fields': ['speech', 'description^2'],
                'analyzer': 'edge_ngram_analyzer'
            }
        }
    }

    response = es.search(index=INDEX_NAME, body=search_body)
    results = response['hits']['hits']

    return jsonify({'results': list(map(clean_search_result, results))})


def clean_search_result(rec):
    return {
        'link': rec['_source']['link'],
        'likes': rec['_source']['likes'],
        'speech': rec['_source']['speech'],
        'description': rec['_source']['description'],
    }


@app.route('/api/autocomplete', methods=["GET"])
@cross_origin()
def autocomplete():
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

    query = request.args.get('query')

    suggest_body = {
        "size": 5,
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["speech", "description"]
            }
        },
        "highlight": {
            "fields": {
                "speech": {},
                "description": {}
            }
        }
    }

    response = es.search(index=INDEX_NAME, body=suggest_body)
    results = response['hits']['hits']

    return jsonify({'results': list(map(clean_autocomplete_result, results))})

def clean_autocomplete_result(rec):
    if 'speech' in rec['highlight']:
        return {
            'text': rec['highlight']['speech'][0]
        }
    
    return {
        'text': rec['highlight']['description'][0]
    }
