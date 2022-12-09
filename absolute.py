import time
import requests
import json
import my_secrets
from authlib.jose import JsonWebSignature
import pandas as pd


# Fill in the Token ID for your API token
#token_id = secrets.ABS_API_KEY
# Fill in the Secret Key for your API token
#token_secret = secrets.ABS_API_SECRET

class AccessAbs:
    def  __init__(self, token_id, token_secret):
        self.token_id = token_id
        self.token_secret = token_secret

    def get_abs_data(self, next_page = None):
        # Build the request
        quarystring_var = "pageSize=100&select=deviceName,username"
        if next_page != None:
            quarystring_var = f"pageSize=100&select=deviceName,username&nextPage={next_page}"
        request = {
            "method": "GET",
            "contentType": "application/json",
            "uri": "/v3/reporting/devices",
            "queryString": quarystring_var,
            "payload": {}
        }
        #"&sortBy=deviceName:desc"
        request_payload_data = {
            "data": request["payload"]
        }
        headers = {
            "alg": "HS256",
            "kid": self.token_id,
            "method": request["method"],
            "content-type": request["contentType"],
            "uri": request["uri"],
            "query-string": request["queryString"],
            "issuedAt": round(time.time() * 1000)
        }

        jws = JsonWebSignature()
        signed = jws.serialize_compact(headers, json.dumps(request_payload_data), self.token_secret)

        request_url = "https://api.absolute.com/jws/validate"
        r = requests.post(request_url, signed, {"content-type": "text/plain"})
        r_json = r.json()
        df = pd.DataFrame(r_json['data'])
        if next_page == None:
            df.to_csv(r'C:\Users\cass.golkin\Documents\Python\Learn_API\file_output\abs_computers.csv', index=False, header=True)
        else:
            df.to_csv(r'C:\Users\cass.golkin\Documents\Python\Learn_API\file_output\abs_computers.csv', mode='a', index=False, header=False)
        if "pagination" in r_json['metadata']:
            #print(r_json['metadata']["pagination"]['nextPage'])
            #for d in r_json['data']:
                #if 'deviceName' in d:
                    #print(d['deviceName'])
                #else:
                    #print("no device name")
            self.get_abs_data(r_json['metadata']["pagination"]['nextPage'])

            

#print(r.content)
#r_json = r.json()
#print(r_json)
#for d in r_json['data']:
    #if 'deviceName' in d:
        #print(d['deviceName'])
    #else:
        #print("no device name")
#while "pagination" in r_json['metadata']:
#if "pagination" in r_json['metadata']:
    #print(r_json['metadata']["pagination"]['nextPage'])
#else:
    #print('Not present')

abs_data = AccessAbs(my_secrets.ABS_API_KEY, my_secrets.ABS_API_SECRET)

abs_data.get_abs_data()
