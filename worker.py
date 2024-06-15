import whisper
import psycopg2
import time
import math
import os
import signal
from elasticsearch import Elasticsearch
import random

PID = os.getpid()

ttm = math.trunc(time.time())

conn = psycopg2.connect("dbname=yappy user=postgres host=database password=pass")
cur = conn.cursor()


import urllib3
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


print('PID: ' + str(PID))
print('Loading model...')
tm = math.trunc(time.time())
model = whisper.load_model('large')
print('Model loaded by ' + str((math.trunc(time.time()) - tm)) + ' secs')


def handler(signum, frame):
    print('Timeout')
    raise Exception("end of time")

signal.signal(signal.SIGALRM, handler)


def recognize(thread):
    recognize_many(thread)


def get_links():
    cur.execute('SELECT * FROM videos WHERE id IN (' + ','.join(get_recs_ids()) + ')')
    return cur.fetchall()


def get_recs_ids():
    cur.execute(
        """
        WITH cte AS (
            SELECT id
            FROM videos
            WHERE pid is null
            LIMIT 100
        )
        UPDATE videos v
        SET pid = %s
        FROM cte
        where v.id = cte.id
        RETURNING v.id
        """,
        (PID,)
    )
    conn.commit()
    return [str(t[0]) for t in cur.fetchall()]


def recognize_many(thread):
    for rec in get_links():
        try:
            print('Start recognize(' + str(thread) + '): ' + rec[1])
            tm1 = math.trunc(time.time())
            speech = recognize_one(rec[1])
            cur.execute(
                "UPDATE videos SET speech = %s, likes=%s WHERE id = %s",
                (speech, random.randint(80, 350), rec[0],)
            )
            conn.commit()
            doc = {
                'id': rec[0],
                'link': rec[1],
                'description': rec[2],
                'speech': rec[3],
                'likes': rec[5],
            }
            es.index(index='videos_index', id=rec[0], body=doc)
            print('Finish recognize (' + str(thread) + ') by ' + str((math.trunc(time.time()) - tm1)) + ' secs')
        except Exception as e:
            print(e)


def recognize_one(link):
    signal.alarm(300)
    result = model.transcribe(link, fp16=False)
    return result["text"]


def main():
    recognize(1)
    print('Total time: '  + str((math.trunc(time.time()) - ttm) / 60) + ' mins')


if __name__ == "__main__":
    main()
