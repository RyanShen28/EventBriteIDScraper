import json

import requests
TOKEN = 'YEMNVG4IIXVPKVNGU2YS' # personal token I used on throwaway account - feel free to reuse as needed

with open("eventIDS_chicago.txt", "r") as IDFile:

    for line in IDFile:
        EVENT_ID = line.strip()

        url = f'https://www.eventbriteapi.com/v3/events/{EVENT_ID}/'
        headers = {
            'Authorization': f'Bearer {TOKEN}', #my eventbrite private key
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            eventInfo = response.json()
            with open('EventInfoChicago.ndjson', 'a') as jsonfile:
                jsonfile.write(json.dumps(eventInfo)+"\n")
                jsonfile.close()
            print("Successful write")
        else:
            print(f"Error {response.status_code}: {response.text}")

    IDFile.close()

