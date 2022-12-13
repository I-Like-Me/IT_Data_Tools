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
        self.keyword_choice = None
        self.found_record = None
        self.keyword_type_choice = None
        self.current_url = None
        self.action_choice = None
        self.s_m_a_choice = None
        self.get_or_post_choice = None
        self.query_string_assembled = None
        self.found_uid = None
        self.current_task_method = None
        self.csv_file = None

    
    def get_or_post_record(self):
        request = {
            "method": self.keyword_choice,
            "contentType": "application/json",
            "uri": self.current_url,
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
    
    def keyword_type_setter(self):
        print("Choose a keyword type?")
        self.keyword_type_choice = input("Please type either - name - serial - to proceed: ").lower()        
        if self.keyword_type_choice == 'name':
            print("Searching by name...")
            self.keyword_type_choice = "&deviceName="
        elif self.keyword_type_choice == 'serial':
            print("Searching by serial...")
            self.keyword_type_choice = "&serialNumber="
        else:
            print(self.keyword_type_choice)
            print("Invalid Entry")
            self.keyword_type_choice = None
            self.keyword_type_setter()        

    def s_m_a_setter(self):
        print("How many records are you searching for?")
        self.s_m_a_choice = input("Please type either - single - multiple - all - to proceed: ").lower()
        if self.s_m_a_choice == "single":
            self.keyword_setter()
            self.keyword_type_setter()
            print("Searching for a specific record...")
        elif self.s_m_a_choice == "multiple":
            self.file_setter()
            self.keyword_type_setter()
            print("Searching for multiple records...")       
        elif self.s_m_a_choice == "all" and self.get_or_post_choice == "GET":
            print("Getting all records...")  
        elif self.s_m_a_choice == "all" and self.get_or_post_choice == "POST":
            print("Selecting all not available for POST requests")
            self.s_m_a_choice = None
            self.s_m_a_setter()
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
        self.action_choice = input("Please type either - unenroll - to proceed: ").lower()
        if self.action_choice == "unenroll":
            print("Initializing unenrollment tool...")
        else:
            print(self.action_choice)
            print("Invalid Entry")
            self.action_choice = None
            self.action_setter()       

    def keyword_setter(self):
        print("Which record are you looking for?")
        self.keyword_choice = input("Type keyword to proceed (Cap-Sensitive): ")
        print("Searching for a specific record...")

    def query_string_maker(self):
        print("Building quary string...")

    def query_string_wiper(self):
        self.query_string_assembled = ''

    def get_post_checker(self):
        if self.get_or_post_choice == "GET" and self.current_task_method == None:
            self.current_task_method = "GET"
        elif self.get_or_post_choice == "GET" and self.current_task_method == "GET":
            print("Returning requested record.")
        elif self.get_or_post_choice == "POST" and self.current_task_method == None:
            self.current_task_method = "GET"
        elif self.get_or_post_choice == "POST" and self.current_task_method == "GET":
            self.current_task_method = "POST"

    def file_setter(self):
        print("Setting file location...")

    def url_setter(self):
        print("Setting URL...")

    def make_request(self):
        self.get_or_post_setter()
        self.get_post_checker()
        self.s_m_a_setter()

abs_tools_1 = AbsTools(my_secrets.ABS_API_KEY, my_secrets.ABS_API_SECRET)

#abs_data.get_specific_record("GZDQG42", "serial")
abs_tools_1.action_setter()
