import os
from dotenv import load_dotenv

# load env vars
load_dotenv()

# app users
BASE_URL = 'https://randomuser.me/api/?nat=gb'
PARTIES = ["Management Party", "Savior Party", "Tech Republic Party"]

# db
db_host = os.getenv("POSTGRES_HOST")
db_name = os.getenv("POSTGRES_DB")
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")

# Kafka
KAFKA_BOOTSTRAP_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVER", "localhost:9092")

voters_topic = 'voters_topic'
candidates_topic = 'candidates_topic'
votes_topic = 'votes_topic'
votes_per_candidate_topic = 'aggregated_votes_per_candidate'
turnout_by_location_topic = 'aggregated_turnout_by_location'
