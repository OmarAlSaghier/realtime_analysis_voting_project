import random
import requests

from config.settings import BASE_URL

random.seed(42)


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


def insert_votes(conn, cur, vote):
    cur.execute("""
            INSERT INTO votes (voter_id, candidate_id, voting_time)
            VALUES (%s, %s, %s)
        """, 
        (
            vote['voter_id'], vote['candidate_id'], vote['voting_time']
        )
    )
    conn.commit()
