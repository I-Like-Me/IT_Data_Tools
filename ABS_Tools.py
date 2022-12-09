import time
import requests
import json
import my_secrets
from authlib.jose import JsonWebSignature
import pandas as pd

class AbsTools:
    def  __init__(self, token_id, token_secret, wanted_record=None, found_record=None, type_choice=None):
        self.token_id = token_id
        self.token_secret = token_secret
        self.wanted_record = wanted_record
        self.found_record = found_record
        self.type_choice = type_choice
    
    def get_abs_record(self):
        request = {
            "method": "GET",
            "contentType": "application/json",
            "uri": "/v3/reporting/devices",
            "queryString": self.type_choice,
            "payload": {}
        }
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
        self.found_record = pd.DataFrame(r_json['data'])
        print(self.found_record)
    
    def unenroll_abs_record(self):
        request = {
            "method": "POST",
            "contentType": "application/json",
            "uri": "/v3/actions/requests/unenroll",
            "queryString": "",
            "payload": {
                "deviceUids": [
                    self.found_record.at[0,"deviceUid"]
                ],
                "excludeMissingDevices": True
            }
        }
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
        print("Unenrolling")
        print(r_json)
    
    def type_setter(self, choose_type):
        if choose_type == 'name':
            self.type_choice = f"pageSize=1&select=deviceName,serialNumber&deviceName={self.wanted_record}"
        elif choose_type == 'serial':
            self.type_choice = f"pageSize=1&select=deviceName,serialNumber&serialNumber={self.wanted_record}"
    
    def get_specific_record(self, choose_id, choose_type):
        self.wanted_record = choose_id
        self.type_setter(choose_type)
        self.get_abs_record()

    def unenroll_single(self, choice):
        self.wanted_record = choice
        self.get_abs_record()
        self.unenroll_abs_record()

abs_data = AbsTools(my_secrets.ABS_API_KEY, my_secrets.ABS_API_SECRET)

abs_data.get_specific_record("GZDQG42", "serial")
