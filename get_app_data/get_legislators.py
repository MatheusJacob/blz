from app import db, headers, CURRENT_CONGRESS_SESSION
from models import Legislator
import requests

def get_legislators_json(congress, chamber):

    req = requests.get(f'https://api.propublica.org/congress/v1/{congress}/{chamber}/members.json', headers=headers)

    json = req.json()

    legislators_json = json['results'][0]['members']

    return legislators_json

def save_legislators(legislators):

    for legislator in legislators:

        leg_id = legislator['id']

        if not Legislator.query.filter(Legislator.id==leg_id).one_or_none():
            new_legislator = Legislator(
                id=leg_id,
                first_name=legislator['first_name'], 
                last_name=legislator['last_name'], 
                image= f'https://theunitedstates.io/images/congress/original/{leg_id}.jpg', 
                state_id=legislator['state'], 
                party_id=legislator['party'], 
                position_code=legislator['short_title'], 
                website = legislator['url'],
                in_office=legislator['in_office'],
                twitter_account = legislator['twitter_account'],
                facebook_account =legislator['facebook_account'],
                youtube_account =legislator['youtube_account'],
                office_address = legislator['office'],
                phone = legislator['phone']
            )

            db.session.add(new_legislator)
            db.session.commit()

        else:

            # doesn't account for if state is changed
            existing_legislator = Legislator.query.filter(Legislator.id==leg_id).one_or_none()
            req = requests.get(legislator['api_uri'],headers=headers)
            json = req.json()
            entry = json['results'][0]
            existing_legislator_id = existing_legislator.id
            existing_legislator.first_name=entry['first_name'] 
            existing_legislator.last_name=entry['last_name'] 
            existing_legislator.party_id=entry['current_party'] 

            db.session.add(existing_legislator)
            db.session.commit()

def get_all_legislators(congress,chamber, legislator_status):

    legislators_json = get_legislators_json(congress,chamber)
    legislators = extract_legislators(legislators_json, legislator_status)
    save_legislators(legislators)


# get senate legislators
senate_legislators_json = get_legislators_json(CURRENT_CONGRESS_SESSION,'senate')
save_legislators(senate_legislators_json)

# get house legislators
house_legislators_json = get_legislators_json(CURRENT_CONGRESS_SESSION,'house')
save_legislators(house_legislators_json)
