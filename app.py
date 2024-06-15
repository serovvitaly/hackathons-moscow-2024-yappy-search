from flask import Flask
from flask import jsonify
from flask import request
import psycopg2
from elasticsearch import Elasticsearch
import urllib3


app = Flask(__name__)


@app.route('/api/v1/upload', methods=["POST"])
def upload():
    try:
        conn = psycopg2.connect("dbname=yappy user=postgres host=database password=pass")
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


@app.route('/api/v1/search', methods=["POST"])
def search():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    es = Elasticsearch(
        hosts=[
            {
                'host': 'elastic',
                'port': 9200,
                'scheme': 'https'
            }
        ],
        basic_auth=('elastic', 'MDDIR5KipT5cI=TdSYU2'),
        verify_certs=False
    )

    data = request.get_json(force=True)
    query = data['query']

    search_body = {
        'from' : 0,
        'size' : 30,
        'query': {
            'multi_match': {
                'query': query,
                'fields': ['speech', 'description']
            }
        }
    }

    response = es.search(index='videos_index', body=search_body)
    results = response['hits']['hits']

    return jsonify({'results': results})


@app.route('/api/v1/autocomplete', methods=["POST"])
def autocomplete():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    es = Elasticsearch(
        hosts=[
            {
                'host': 'elastic',
                'port': 9200,
                'scheme': 'https'
            }
        ],
        basic_auth=('elastic', 'MDDIR5KipT5cI=TdSYU2'),
        verify_certs=False
    )

    data = request.get_json(force=True)
    query = data['query']

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

    response = es.search(index='videos_index', body=suggest_body)
    results = response['hits']['hits']

    return jsonify({'results': results})

