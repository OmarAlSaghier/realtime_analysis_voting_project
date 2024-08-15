-- Create tables for the database
CREATE TABLE IF NOT EXISTS candidates (
    candidate_id VARCHAR(255) PRIMARY KEY,
    candidate_name VARCHAR(255),
    party_affiliation VARCHAR(255),
    biography TEXT,
    campaign_platform TEXT,
    photo_url TEXT
);

CREATE TABLE IF NOT EXISTS voters (
    voter_id VARCHAR(255) PRIMARY KEY,
    voter_name VARCHAR(255),
    date_of_birth VARCHAR(255),
    gender VARCHAR(255),
    nationality VARCHAR(255),
    registration_number VARCHAR(255),
    address_street VARCHAR(255),
    address_city VARCHAR(255),
    address_state VARCHAR(255),
    address_country VARCHAR(255),
    address_postcode VARCHAR(255),
    email VARCHAR(255),
    phone_number VARCHAR(255),
    cell_number VARCHAR(255),
    picture TEXT,
    registered_age INTEGER
);

CREATE TABLE IF NOT EXISTS votes (
    voter_id VARCHAR(255) UNIQUE,
    candidate_id VARCHAR(255),
    voting_time TIMESTAMP,
    vote int DEFAULT 1,
    PRIMARY KEY (voter_id, candidate_id)
);

-- Insert fake data for candidates only (voters will be inserted via the API)
INSERT INTO public.candidates (candidate_id,candidate_name,party_affiliation,biography,campaign_platform,photo_url) VALUES
    ('09946798-0c46-4372-abc1-60277a58c575','Ricardo Bell','Management Party','A brief bio of the candidate.','Key campaign promises or platform.','https://randomuser.me/api/portraits/men/13.jpg'),
    ('f4af0ff8-acb8-4eca-97a8-44b6c789529d','Lisa Watson','Savior Party','A brief bio of the candidate.','Key campaign promises or platform.','https://randomuser.me/api/portraits/women/37.jpg'),
    ('9dd4d25a-2587-4817-88cb-33e2f5a14b8c','Allan Martinez','Tech Republic Party','A brief bio of the candidate.','Key campaign promises or platform.','https://randomuser.me/api/portraits/men/89.jpg')
;
