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
        self.found_record_as_json = None
        self.found_record_as_df = None
        self.records_as_df_list = []
        self.combined_multiple_records = None
        self.keyword_type_choice = None
        self.current_url = None
        self.action_choice = None
        self.s_m_a_choice = None
        self.get_or_post_choice = None
        self.query_string_assembled = None
        self.found_uid = None
        self.current_task_method = None
        self.multiple_keywords = None
        self.next_page = None
        self.request_return_format = None

    
    def get_or_post_record(self):
        request = {
            "method": self.current_task_method,
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
        self.found_record = requests.post(request_url, signed, {"content-type": "text/plain"})
    
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
            self.csv_to_df()
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

    def csv_to_df(self):
        self.multiple_keywords = pd.read_csv(r"multi_search_file\keyword_list.csv")
    
    def convert_to_json(self):
        self.found_record_as_json = self.found_record.json()

    def json_to_df(self):
        self.found_record_as_df = pd.DataFrame(self.found_record_as_json['data'])

    def query_string_maker(self, row=0):
        print("Building quary string...")
        if self.s_m_a_choice == "single":
            self.query_string_assembled = f"pageSize=1&select=deviceName,serialNumber{self.keyword_type_choice}{self.keyword_choice}"
            self.get_or_post_record()
            self.convert_to_json()
            self.json_to_df()
        elif self.s_m_a_choice == "multiple":
            self.csv_to_df()
            while row < len(self.multiple_keywords):
                self.keyword_choice = self.multiple_keywords.loc[row, self.keyword_type_choice[1:-7]]
                self.query_string_assembled = f"pageSize=1&select=deviceName,serialNumber{self.keyword_type_choice}{self.keyword_choice}"
                self.multi_run()
                row += 1
            self.combined_multiple_records = pd.concat(self.records_as_df_list, ignore_index=True)
            self.found_record_as_df = self.combined_multiple_records
        elif self.s_m_a_choice == "all":
            self.page_turner()
            self.get_or_post_record()
            self.convert_to_json()
            self.json_to_df()
            self.records_as_df_list.append(self.found_record_as_df)
            self.next_page_detect()
            self.all_run()
            self.combined_multiple_records = pd.concat(self.records_as_df_list, ignore_index=True)
            self.found_record_as_df = self.combined_multiple_records
                     
    def page_turner(self):
        if self.next_page == None:
            self.query_string_assembled = "pageSize=100&select=deviceName,serialNumber"
        elif self.next_page != None:
            self.query_string_assembled = f"pageSize=100&select=deviceName,serialNumber&nextPage={self.next_page}"  

    def next_page_detect(self):
        if "pagination" in self.found_record_as_json['metadata']:
            self.next_page = self.found_record_as_json['metadata']["pagination"]['nextPage']
        else:
            self.next_page = self.found_record_as_json['metadata']

    def query_string_wiper(self):
        self.query_string_assembled = ''

    def get_post_checker(self):
        if self.get_or_post_choice == "GET" and self.current_task_method == None:
            self.current_task_method = "GET"
        elif self.get_or_post_choice == "GET" and self.current_task_method == "GET":
            print("Returning requested record...")
            self.return_request()
        elif self.get_or_post_choice == "POST" and self.current_task_method == None:
            self.current_task_method = "GET"
        elif self.get_or_post_choice == "POST" and self.current_task_method == "GET":
            self.current_task_method = "POST"

    def url_setter(self):
        if self.current_task_method == "GET":
            self.current_url = "/v3/reporting/devices"
        elif self.current_task_method == "POST":
            self.current_url = f"/v3/actions/requests/{self.action_choice}"

    def return_request(self):
        print("Would you like your request saved or displayed?")
        self.request_return_format = input("Please type either - save - display - to proceed: ").lower()
        if self.request_return_format == "display":
            self.s_or_m_display()
        elif self.request_return_format == "save":
            print("Saving requested record to file...")
            self.put_in_csv()


    def multi_run(self):
        self.get_or_post_record()
        self.convert_to_json()
        self.json_to_df()
        self.records_as_df_list.append(self.found_record_as_df)

    def all_run(self):
        while "pagination" in self.found_record_as_json['metadata']:
            self.page_turner()
            self.get_or_post_record()
            self.convert_to_json()
            self.json_to_df()
            self.records_as_df_list.append(self.found_record_as_df)
            self.next_page_detect()

    def s_or_m_display(self):
        if self.s_m_a_choice == "single":
            print(self.found_record_as_df)
        elif self.s_m_a_choice == "multiple":
            print(self.combined_multiple_records)
        elif self.s_m_a_choice == "all":
            print(self.combined_multiple_records)

    def put_in_csv(self):
        if self.s_m_a_choice == "single":
            self.found_record_as_df.to_csv(r'file_output\abs_single.csv', index=False, header=True)
        elif self.s_m_a_choice == "multiple":
            self.found_record_as_df.to_csv(r'file_output\abs_multiple.csv', index=False, header=True)
        elif self.s_m_a_choice == "all":
            self.found_record_as_df.to_csv(r'file_output\abs_all.csv', index=False, header=True)

    def make_request(self):
        self.get_or_post_setter()
        self.get_post_checker()
        self.url_setter()
        self.s_m_a_setter()
        self.query_string_maker()
        self.get_post_checker()

abs_tools_1 = AbsTools(my_secrets.ABS_API_KEY, my_secrets.ABS_API_SECRET)

#abs_data.get_specific_record("GZDQG42", "serial")
abs_tools_1.make_request()
