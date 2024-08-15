from config.db_conn import db_connection
from config.settings import voters_topic
from kafka_repo.consumer_producer import kafka_produce_msg
from repo.voters import generate_voter_data, insert_voters


if __name__ == "__main__":
    conn, cur = db_connection()

    # generate voters and send to kafka
    for i in range(1000):
        voter_data = generate_voter_data()
        print("Voter number: ", i)
        insert_voters(conn, cur, voter_data)
        kafka_produce_msg(voter_data, voters_topic)
        print('Produced voter {}, data: {}'.format(i, voter_data))
