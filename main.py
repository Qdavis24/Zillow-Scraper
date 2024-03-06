from bs4 import BeautifulSoup
import requests
from fake_headers import Headers
import json
import random
import time

US_STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
    "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska",
    "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas",
    "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
]
STATES_KEYS = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming'
}

with open("proxies.txt") as file:
    PROXIES = [line.strip() for line in file.readlines()]


def no_detection(location, page):
    """ randomizes headers and proxy and attempts to retrieve target data from endpoint, if successful returns data
    if unsuccessful returns none"""
    headers = Headers(headers=True).generate()
    curr_prox = random.choice(PROXIES)
    proxies = {
        "http": f"http://{curr_prox}"
    }
    response = requests.get(f"https://www.zillow.com/homes/{location}_rb/{page}_p", headers=headers, proxies=proxies)
    soup = BeautifulSoup(response.text, "html.parser")
    data = soup.find(name="script", id="__NEXT_DATA__")

    return data


def scrape_location(pages, location):
    # split location to see if target is state or city
    split_location = location.split(" ")
    if len(split_location) > 2:
        location = split_location[1]
        city = split_location[0]
    else:
        city = None
    # initialize list to store data in
    extracted_data = []
    # iterate through pages requested
    for i in range(pages):
        time.sleep(1)
        # initialize data and counter for tries
        data = None
        counter = 0
        # if target script element not present continue loop
        while data is None:
            if counter > 13:
                print(i)
                with open(f"jsons/{location}.json", "w") as w_f:
                    json.dump(extracted_data, w_f)
                return print(f"Process exited after {counter} tries...")
            else:
                # attempt to find target script element
                if counter > 0:
                    print(f"{counter} Tries...")
                    time.sleep(2)
                data = no_detection(location, i)
                counter += 1
        # if targeted script was found load into list and navigate to required data
        data = json.loads(data.text)
        list_results = data["props"]["pageProps"]["searchPageState"]["cat1"]["searchResults"]["listResults"]
        print(list_results)
        # iterate through each property in list
        for p in list_results:
            # check that the location(state) or the city are the same as the target location
            if STATES_KEYS[p["addressState"]] == location or p["addressCity"] == city:
                # initializes a dictionary of what I am going to call my data and what the key for the data in scrape is
                target_extracts = {"price": "price", "uf-price": "unformattedPrice", "square-footage": "area",
                                   "land": ["hdpData", "homeInfo", "lotAreaValue"],
                                   "land_unit": ['hdpData', "homeInfo", "lotAreaUnit"],
                                   "beds": "beds", "baths": "baths", "street-address": "addressStreet",
                                   "city": "addressCity", "state": "addressState", "zip": "addressZipcode",
                                   "longitude": ["latLong", "longitude"],
                                   "latitude": ["latLong", "latitude"],
                                   "carouselPhotos": "carouselPhotos", "imgSrc": "imgSrc"}
                temp = {}
                # attempts to each specific piece of data, if missing inputs value of none
                for key, value in target_extracts.items():
                    try:
                        if type(value) == list:
                            target = p[value[0]]
                            for target_key in value[1:]:
                                target = target[target_key]
                            temp[key] = target

                        else:
                            temp[key] = p[value]

                    except KeyError:
                        temp[key] = None
                print(temp)
                extracted_data.append(temp)
            # if data for incorrect location skip
            else:
                print(f"Prop {STATES_KEYS[p['addressState']]} {p['addressCity']} not == {location} {city}")
                pass

    with open(f"jsons/{location}.json", "w") as w_file:
        json.dump(extracted_data, w_file)


scrape_location(30, "New York")
# for state in US_STATES:
#     scrape_location(60, state)
