import json
import re
import requests
TOKEN = 'YEMNVG4IIXVPKVNGU2YS'

counter=0

#added all mentions of IG/FB socials in titles, descriptions and summary

def scan_socials(s, socials):

    if s is None:
        return
    # Pattern for Facebook links
    fb_match = re.findall(r'(facebook\.com[^\s]*)', s, re.IGNORECASE)
    if len(fb_match) > 0:
        for i in fb_match:
            socials["fb_link"].append(i)

    # Pattern for Instagram link
    insta_link_match = re.findall(r'(instagram\.com[^\s]*)', s, re.IGNORECASE)
    if len(insta_link_match) > 0:
        for i in insta_link_match:
            socials["insta_link"].append(i)
    # Pattern for Instagram handles with @
    insta_handle_match = re.findall(r'@(\w+)', s)
    if len(insta_handle_match) > 0:
        for i in insta_handle_match:
            socials["insta_handle"].append('@' + i)

with open("eventIDS_chicago.txt", "r") as IDFile:
    importantKeys = {"name", "description", "url", "start", "end", "organization", "published", "status", "summary", "facebook_event_id", "organizer_id"}

    for line in IDFile:
        EVENT_ID = line.strip()



        url = f'https://www.eventbriteapi.com/v3/events/{EVENT_ID}/'
        headers = {
            'Authorization': f'Bearer {TOKEN}', #my eventbrite private key
        }



        response = requests.get(url, headers=headers)
        if response.status_code == 200:


            eventInfo = response.json()


            #filters json to relevant outputs

            eventInfo = {k: v for k, v in eventInfo.items() if k in importantKeys}
            socials = {"fb_link": [], "insta_link": [], "insta_handle": []}

            scan_socials(eventInfo["name"]["text"], socials)
            scan_socials(eventInfo['description']['text'], socials)
            scan_socials(eventInfo['summary'], socials)

            eventInfo["socials"] = socials
            eventInfo['name'] = eventInfo["name"]["text"]
            eventInfo['description'] = eventInfo["description"]["text"]

            with open('EventInfoChicago.ndjson', 'a') as jsonfile:
                jsonfile.write(json.dumps(eventInfo)+"\n")
                jsonfile.close()
            print("Successful write on id "+ EVENT_ID)
        else:
            print(f"Error {response.status_code}: {response.text}")
            print("EVENT ID FAILED WAS " + EVENT_ID)

    IDFile.close()

