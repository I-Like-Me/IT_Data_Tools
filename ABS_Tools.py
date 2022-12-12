import time
import requests
import json
import my_secrets
from authlib.jose import JsonWebSignature
import pandas as pd

class AbsTools:
    def  __init__(self, token_id, token_secret):
        self.token_id = token_id
        self.token_secret = token_secret
        self.wanted_record = None
        self.found_record = None
        self.keyword_type_choice = None
        self.action_url = None
        self.s_m_a_choice = None
        self.get_or_post_choice = None
        self.query_string_assembled = None

    
    def get_abs_record(self):
        request = {
            "method": self.get_or_post_choice,
            "contentType": "application/json",
            "uri": self.action_url,
            "queryString": self.query_string_assembled,
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
    
    def keyword_type_setter(self, choose_keyword_type):
        if choose_keyword_type == 'name':
            self.keyword_type_choice = f"pageSize=1&select=deviceName,serialNumber&deviceName={self.wanted_record}"
        elif choose_keyword_type == 'serial':
            self.keyword_type_choice = f"pageSize=1&select=deviceName,serialNumber&serialNumber={self.wanted_record}"

    def s_m_a_setter(self):
        print("How many records are you searching for?")
        self.s_m_a_choice = input("Please type either - single - multiple - all - to proceed: ").lower()
        if self.s_m_a_choice == "single":
            print("Searching for a specific record...")
        elif self.s_m_a_choice == "multiple":
            print("Searching for multiple records...")       
        elif self.s_m_a_choice == "all":
            print("Getting all records...")  
        else:
            print(self.s_m_a_choice)
            print("Invalid Entry")
            self.s_m_a_choice = None
            self.s_m_a_setter()

    def get_or_post_setter(self):
        print("Is this a GET or POST?")
        self.get_or_post_choice = input("Please type either - GET - POST - to proceed: ").upper()
        if self.get_or_post_choice == "GET":
            print("Getting reporting tools...")
            self.action_url = "/v3/reporting/devices"
            print("URL")
        elif self.get_or_post_choice == "POST":
            print("Getting action tools...")
        else:
            print(self.get_or_post_choice)
            print("Invalid Entry")
            self.get_or_post_choice = None
            self.get_or_post_setter()   

    def action_setter(self):
        print("What action would you like to take?")
        self.action_url = input("Please type either - unenroll - to proceed: ").lower()
        if self.action_url == "unenroll":
            print("Initializing unenrollment tool...")
        else:
            print(self.action_url)
            print("Invalid Entry")
            self.action_url = None
            self.action_setter()       

    def get_specific_record(self, choose_id, choose_type):
        self.wanted_record = choose_id
        self.type_setter(choose_type)
        self.get_abs_record()

    def unenroll_single(self, choice):
        self.wanted_record = choice
        self.get_abs_record()
        self.unenroll_abs_record()

abs_data = AbsTools(my_secrets.ABS_API_KEY, my_secrets.ABS_API_SECRET)

#abs_data.get_specific_record("GZDQG42", "serial")
abs_data.get_or_post_choice()
