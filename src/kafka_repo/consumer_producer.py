import simplejson as json

from confluent_kafka import SerializingProducer
from config.db_conn import delivery_report
from config.settings import KAFKA_BOOTSTRAP_SERVER

# create kafka producer
conf = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVER
}
producer = SerializingProducer(conf)


def kafka_produce_msg(msg_data, topic):
    producer.produce(
        topic,
        key=msg_data["voter_id"],
        value=json.dumps(msg_data),
        on_delivery=delivery_report
    )
    producer.flush()
