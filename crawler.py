import requests
import base64
import json
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["my_database"]
collection = db["product_responses"]

num = 1
params = {
    'workspace': 'master',
    'maxAge': 'long',
    'appsEtag': 'remove',
    'domain': 'store',
    'locale': 'pt-AO',
    '__bindingId': 'd29086b8-f38b-4a8b-9d93-dfe44418ac0d',
}

headers = {
    'Content-Type': 'application/json',
}

while True:
    variable = f'{{"productId":"{num}"}}'
    encoded_variable = base64.b64encode(variable.encode("utf-8")).decode("utf-8")

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

    response = requests.post(
        'https://www.ncrangola.com/_v/private/graphql/v1',
        params=params,
        headers=headers,
        json=data
    )

    try:
        parsed_response = response.json()
        
        if (response.status_code == 500 and 
            parsed_response.get("message") == "Request failed with status code 500" and 
            parsed_response.get("extensions", {}).get("code") == "INTERNAL_SERVER_ERROR"):
            
            print(f"Stopped at productId {num} (specific 500 error)")
            break
            
        if response.status_code == 200:
            collection.insert_one(parsed_response)
            print(f"Inserted productId {num}")
        else:
            print(f"Received non-200 status ({response.status_code}) for productId {num}")

    except json.JSONDecodeError:
        print(f"Failed to parse response for productId {num}")
        if response.status_code == 500:
            print(f"Stopped at productId {num} (non-JSON 500 response)")
            break
            
    except Exception as e:
        print(f"Error processing productId {num}: {str(e)}")

    num += 1
