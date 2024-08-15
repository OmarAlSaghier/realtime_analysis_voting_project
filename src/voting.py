import random
import time
import simplejson as json

from datetime import datetime
from confluent_kafka import Consumer, KafkaException, KafkaError

from config.db_conn import db_connection
from config.settings import KAFKA_BOOTSTRAP_SERVER, voters_topic, votes_topic
from kafka_repo.consumer_producer import kafka_produce_msg
from repo.candidates import check_candidates
from repo.voters import insert_votes

consumer = Consumer({
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVER,
    'group.id': 'voting-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
})
consumer.subscribe([voters_topic])


if __name__ == "__main__":
    conn, cur = db_connection()
    candidates = check_candidates(cur)

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            elif msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break
            else:
                voter = json.loads(msg.value().decode('utf-8'))
                chosen_candidate = random.choice(candidates)
                vote = voter | chosen_candidate | {
                    "voting_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    "vote": 1
                }
                print("User {} is voting for candidate: {}".format(vote['voter_id'], vote['candidate_id']))

                try:
                    insert_votes(conn, cur, vote)
                    consumer.commit(msg)
                    kafka_produce_msg(vote, votes_topic)
                    
                except Exception as e:
                    print("Error: {}".format(e))
                    # conn.rollback()
                    continue
            time.sleep(0.2)
            
    except KafkaException as e:
        print(e)
