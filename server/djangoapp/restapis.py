import requests
import json
from .models import CarDealer, DealerReview, CarModel
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features,SentimentOptions

def get_request(url, **kwargs):
    print("GET from {} ".format(url))
    json_data = {}
    try:
        # Call get method of requests library with URL and parameters
        if 'apikey' in kwargs:
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', kwargs['api_key']))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
        status_code = response.status_code
        print("With status {} ".format(status_code))
        json_data = json.loads(response.text)        
    except:
        # If any error occurs
        print("Network exception occurred")
    return json_data

#
# Create a `post_request` to make HTTP POST requests
def post_request(url, json_payload, **kwargs):
    try:
        response = requests.post(url, params=kwargs, json=json_payload)
        return response
    except Exception as e:
        print("Error" ,e)
    print("Status Code ", {response.status_code})
    data = json.loads(response.text)
    return data

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    state = kwargs.get("state")
    if state:
        json_result = get_request(url, state=state)
    else:
        json_result = get_request(url)

    # print('json_result from line 31', json_result)    

    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result[]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer['doc']
            # print(dealer_doc)
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"], full_name=dealer_doc["full_name"],
                                
                                   st=dealer_doc["st"], zip=dealer_doc["zip"], short_name=dealer_doc["short_name"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    dealerId = kwargs['kwargs']['dealership']
    json_result = get_request(url, dealerId=dealerId)
    if json_result:
        # Get the row list in JSON as dealers
        reviews = json_result["body"]["data"]["docs"]
        # For each review object
        for review in reviews:
            review_obj = DealerReview(
                dealership=review["dealership"],
                name=review["name"],
                purchase=review["purchase"],
                review=review["review"],
                purchase_date=review["purchase_date"],
                car_make=review["car_make"],
                car_model=review["car_model"],
                car_year=review["car_year"],
                sentiment=analyze_review_sentiments(review["review"]),
                id=review['_id']
                )
            results.append(review_obj)
        
    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(dealerreview):
    api_key="wA2opsZiLa3sHYCjQ8rUIW-xWNIoff0phjBkXWMKx7cj"
    url="https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/089cac19-ce2a-4220-9806-169a9be726ad"
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator)
    natural_language_understanding.set_service_url(url)
    try:
        response = natural_language_understanding.analyze( text=dealerreview,features=Features(sentiment=SentimentOptions())).get_result()
        print(response)
        label=response["sentiment"]["targets"]["label"]
        return(label)
    except:
        return("neutral")
