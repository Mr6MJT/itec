import requests
import base64
import json
from pymongo import MongoClient

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["my_database"]
collection = db["product_responses"]

# API request setup
num = 1
params = {
    'workspace': 'master',
    'maxAge': 'long',
    'appsEtag': 'remove',
    'domain': 'store',
    'locale': 'pt-AO',
    '__bindingId': 'd29086b8-f38b-4a8b-9d93-dfe44418ac0d',
}

cookies = {
    # Fill in if needed
}

headers = {
    'Content-Type': 'application/json',
    # Add more headers if required
}

while True:
    # Create and encode variable
    variable = f'{{"productId":"{num}"}}'
    encoded_variable = base64.b64encode(variable.encode("utf-8")).decode("utf-8")

    # Create request body
    data = {
        "operationName": "productRecommendations",
        "variables": json.loads(variable),
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "a924bfec77ee3002912384f240005507983f6f8c03709572581179a06808a7ab",
                "sender": "ncrangola.components@1.x",
                "provider": "vtex.search-graphql@0.x"
            },
            "variables": encoded_variable
        }
    }

    # Send request
    response = requests.post(
        'https://www.ncrangola.com/_v/private/graphql/v1',
        params=params,
        cookies=cookies,
        headers=headers,
        json=data
    )

    # Stop if status code is 500
    if response.status_code == 500:
        print(f"Stopped at productId {num} (status 500)")
        break

    try:
        parsed_response = response.json()
        collection.insert_one(parsed_response)
        print(f"Inserted productId {num}")
    except Exception as e:
        print(f"Error inserting productId {num}: {e}")

    num += 1
