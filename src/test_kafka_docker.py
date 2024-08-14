
import random
import time
import simplejson as json

from datetime import datetime
from confluent_kafka import Consumer, KafkaException, KafkaError, SerializingProducer

from config.settings import KAFKA_BOOTSTRAP_SERVER_DOCKER


conf = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVER_DOCKER
}

producer = SerializingProducer(conf)
consumer = Consumer(conf | {
    'group.id': 'voting-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
})
consumer.subscribe(['voters_topic'])


if __name__ == "__main__":
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
                vote = voter | {
                    "voting_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    "vote": 1
                }
                print("User {} is voting for candidate: {}".format(vote['voter_id'], 'x'))
                # commit the msg
                consumer.commit(msg)

                # try:
                #     producer.produce(
                #         votes_topic,
                #         key=vote["voter_id"],
                #         value=json.dumps(vote),
                #         on_delivery=delivery_report
                #     )
                #     producer.poll(0)
                # except Exception as e:
                #     print("Error: {}".format(e))
                #     # conn.rollback()
                #     continue

            time.sleep(0.2)
    except KafkaException as e:
        print(e)
