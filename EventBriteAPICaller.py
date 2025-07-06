import json
import re
import requests
TOKEN = 'YEMNVG4IIXVPKVNGU2YS'

counter=0




def scan_socials(s, socials):

    if s is None:
        return
    #Social media patterns listed here:
    #Pattern for Phone

    phone_pattern = re.compile(
        r'''
        (?:^|[ \t\n])     # Starting Word boundary
        (?:               # Non-capturing group for optional parts
          \d{3}           # 123 (first 3 digits, no paren) 
          |               # OR
          \(\d{3}\)      # (123) (with paren)
        )
        [\s-]?           # Optional space or hyphen
        \d{3}            # 456 (middle 3)
        [\s-]?           # Optional space or hyphen
        \d{4}            # 7890 (last 4)
        \b               # Ending Word boundary (prevents longer numbers)
        ''',
        re.VERBOSE
    )
    email_pattern = re.compile(
        r"\S+@\S+",
        re.IGNORECASE,
    )
    fb_pattern = re.compile(
        r'(facebook\.com[^\s]&)',
        re.IGNORECASE,
    )
    insta_link_pattern = re.compile(
        r'(instagram\.com[^\s]*)',
        re.IGNORECASE
    )
    #pattern1 and pattern2 are listed as such bc easier than having to manually delete the space before the @ for search pattern 1
    insta_handle_pattern = re.compile(
        r"(?:^|[ \t\n])@([a-zA-Z0-9._]+)(?=\W|$)",
        re.IGNORECASE
        )


    phone_matches = phone_pattern.findall(s)
    if(len(phone_matches) > 0):
        for i in phone_matches:
            socials["phone"].append(i)

    #Pattern for Emails
    email_match = email_pattern.findall(s)
    if(len(email_match) > 0):
        for i in email_match:
            socials["emails"].append(i)


    # Pattern for Facebook links
    fb_match = fb_pattern.findall(s)
    if len(fb_match) > 0:
        for i in fb_match:
            socials["fb_link"].append(i)

    # Pattern for Instagram link
    insta_link_match = insta_link_pattern.findall(s)
    if len(insta_link_match) > 0:
        for i in insta_link_match:
            socials["insta_link"].append(i)

    # Pattern for Instagram handles with @
    insta_handle_match = insta_handle_pattern.findall(s)
    print(len(insta_handle_match))
    if len(insta_handle_match) > 0:
        for i in insta_handle_match:
            print(i)
            socials["insta_handle"].append('@'+i)
with open("event_page_text_chicago.ndjson", "r") as jsonfile:
    text_data = json.load(jsonfile)
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
            socials = {"fb_link": [], "insta_link": [], "insta_handle": [], "emails":[], "phone":[]}


            scan_socials(eventInfo[line], socials) #this scrapes the page text, not the API text
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

