import psycopg2
from config.settings import db_host, db_name, db_user, db_password


def db_connection():
    conn = psycopg2.connect(f"host={db_host} dbname={db_name} user={db_user} password={db_password}")
    cur = conn.cursor()
    return conn, cur


def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')
