import random

import requests
import simplejson as json

from confluent_kafka import SerializingProducer
from config.db_conn import db_connection, delivery_report
from config.settings import BASE_URL, PARTIES, KAFKA_BOOTSTRAP_SERVER, voters_topic
from db_tables import create_tables


random.seed(42)


def generate_candidate_data(candidate_number, total_parties):
    response = requests.get(BASE_URL + '&gender=' + ('female' if candidate_number % 2 == 1 else 'male'))
    if response.status_code == 200:
        user_data = response.json()['results'][0]
        return {
            "candidate_id": user_data['login']['uuid'],
            "candidate_name": f"{user_data['name']['first']} {user_data['name']['last']}",
            "party_affiliation": PARTIES[candidate_number % total_parties],
            "biography": "A brief bio of the candidate.",
            "campaign_platform": "Key campaign promises or platform.",
            "photo_url": user_data['picture']['large']
        }
    else:
        return "Error fetching data"


def generate_voter_data():
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        user_data = response.json()['results'][0]
        return {
            "voter_id": user_data['login']['uuid'],
            "voter_name": f"{user_data['name']['first']} {user_data['name']['last']}",
            "date_of_birth": user_data['dob']['date'],
            "gender": user_data['gender'],
            "nationality": user_data['nat'],
            "registration_number": user_data['login']['username'],
            "address": {
                "street": f"{user_data['location']['street']['number']} {user_data['location']['street']['name']}",
                "city": user_data['location']['city'],
                "state": user_data['location']['state'],
                "country": user_data['location']['country'],
                "postcode": user_data['location']['postcode']
            },
            "email": user_data['email'],
            "phone_number": user_data['phone'],
            "cell_number": user_data['cell'],
            "picture": user_data['picture']['large'],
            "registered_age": user_data['registered']['age']
        }
    else:
        return "Error fetching data"


def check_and_insert_candidates(conn, cur):
    # get candidates from db
    cur.execute("""
        SELECT * FROM candidates
    """)
    candidates = cur.fetchall()

    if len(candidates) == 0:
        for i in range(3):
            candidate = generate_candidate_data(i, 3)
            print(candidate)
            cur.execute("""
                        INSERT INTO candidates (candidate_id, candidate_name, party_affiliation, biography, campaign_platform, photo_url)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                candidate['candidate_id'], candidate['candidate_name'], candidate['party_affiliation'], candidate['biography'],
                candidate['campaign_platform'], candidate['photo_url'])
                )
            conn.commit()
    

def insert_voters(conn, cur, voter):
    cur.execute("""
                INSERT INTO voters (voter_id, voter_name, date_of_birth, gender, nationality, registration_number, address_street, address_city, address_state, address_country, address_postcode, email, phone_number, cell_number, picture, registered_age)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s)
            """,
        (
            voter["voter_id"],
            voter['voter_name'], voter['date_of_birth'], voter['gender'],
            voter['nationality'], voter['registration_number'], voter['address']['street'],
            voter['address']['city'], voter['address']['state'], voter['address']['country'],
            voter['address']['postcode'], voter['email'], voter['phone_number'],
            voter['cell_number'], voter['picture'], voter['registered_age']
        )
    )
    conn.commit()


if __name__ == "__main__":
    conn, cur = db_connection()
    create_tables(conn, cur)
    check_and_insert_candidates(conn, cur)

    # create kafka producer
    producer = SerializingProducer({
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVER, 
    })

    # generate voters and send to kafka
    for i in range(1000):
        voter_data = generate_voter_data()
        print("Voter number: ", i)
        insert_voters(conn, cur, voter_data)

        producer.produce(
            voters_topic,
            key=voter_data["voter_id"],
            value=json.dumps(voter_data),
            on_delivery=delivery_report
        )

        print('Produced voter {}, data: {}'.format(i, voter_data))
        producer.flush()
