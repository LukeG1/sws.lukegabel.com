import requests
from requests.auth import HTTPBasicAuth
import urllib.parse
import json

class Groupme:
    """Luke version of the groupme api built around bot automation"""

    def __init__(self, access_token:str , debug=False):
        """
        Authenticates the instance and does a check to ensure they gave proper credientials
        """
        self.debug = debug
        self.master_url = 'https://api.groupme.com/v3'
        self.api_token = access_token
        headers = {"Content-Type": "application/json"}
        r = requests.get(
            self.master_url+f"/users/me?token={self.api_token}", 
            auth=HTTPBasicAuth(self.api_token, 'api_token'), 
            headers=headers
        )
        if(self.debug): print(r)
        if(r.status_code != 200): raise Exception('INVALID AUTHENTICATION, CHECK TOKEN OR INTERNET CONNECTION')


    def set_group_name(self, group_name:str):
        headers = {
            "Content-Type": "application/json",
        }
        r = requests.get(
            self.master_url+f"/groups?token={self.api_token}&per_page={25}", 
            auth=HTTPBasicAuth(self.api_token, 'api_token'), 
            headers=headers,
        )
        if(self.debug): print(r)
        #if(self.debug): print(r.content)
        
        
        #self.workspace_id = r.json()['data']['workspaces'][0]['id']
        if(r.status_code != 200): raise Exception('INVALID AUTHENTICATION, CHECK TOKEN OR INTERNET CONNECTION')

        flag = False
        groups_json = r.json()['response']

        for group in groups_json:
            if(group['name'] == group_name):
                self.group = group
                flag = True
                break
        
        if(not flag): raise Exception('GROUP NOT FOUND')

        self.group_id = self.group['id']
        self.group_name = self.group['name']
        #self.group_members = self.group['']
        self.group_members = []
        for member in self.group['members']:
            self.group_members.append({
                "name":member['nickname'],
                "user_id":member['user_id'],
            })

    
    def join_group(self, link:str):
        

        #/groups/:id/join/:share_token
        headers = {
            "Content-Type": "application/json",
        }
        r = requests.post(
            self.master_url+f"/groups/{link.split('/')[-2]}/join/{link.split('/')[-1]}?token={self.api_token}", 
            auth=HTTPBasicAuth(self.api_token, 'api_token'), 
            headers=headers,
        )
        print(self.master_url+f"/groups/{link.split('/')[-2]}/join/{link.split('/')[-1]}?token={self.api_token}")
        return r.json()['response']['group']['group_id']



    
    def add_bot_from_id(self, group_id:str, bot_name:str):
        payload = {
            "bot" : {
                "name" : bot_name,
                "group_id" : group_id,
            },
        }
        headers = {
            "Content-Type": "application/json",
        }
        r = requests.post(
            self.master_url+f"/bots?token={self.api_token}", 
            auth=HTTPBasicAuth(self.api_token, 'api_token'), 
            headers=headers,
            data=json.dumps(payload),
        )
        print(r)
        return r.json()['response']['bot']['bot_id']

    def set_bot(self, bot_id:str):
        self.bot_id = bot_id


    def send_message(self, message):
        headers = {
            "Content-Type": "application/json",
        }
        r = requests.post(
            self.master_url+f"/bots/post?bot_id={self.bot_id}&text={urllib.parse.quote(str(message))}", 
            auth=HTTPBasicAuth(self.api_token, 'api_token'), 
            headers=headers,
        )
        if(self.debug): print(r)
        
        #self.workspace_id = r.json()['data']['workspaces'][0]['id']
        if(r.status_code != 202): raise Exception('INVALID AUTHENTICATION, CHECK TOKEN OR INTERNET CONNECTION')

    def name_stuff(self):
        headers = {
            "Content-Type": "application/json",
        }
        payload = {
            "name":"Swoll Admin"
        }
        r = requests.post(
            self.master_url+f"/users/update?token={self.api_token}&per_page={25}", 
            auth=HTTPBasicAuth(self.api_token, 'api_token'), 
            headers=headers,
            data = json.dumps(payload),
        )
        if(self.debug): print(r)
        #if(self.debug): print(r.content)
        print(r.json())
        
        #self.workspace_id = r.json()['data']['workspaces'][0]['id']
        if(r.status_code != 200): raise Exception('INVALID AUTHENTICATION, CHECK TOKEN OR INTERNET CONNECTION')


#fake account id: cb6dd2b0b03b01392aed6ecce0eb34a6


#gpme = Groupme("cb6dd2b0b03b01392aed6ecce0eb34a6", debug=True)





#gpme.set_group_name("TEST1")
# gpme.set_bot("b2ae2927f79cdf45d5aa920ada")
# gpme.send_message("a")







# new_bot = gpme.add_bot_from_id(
#     group_id = "68798494",
#     bot_name = "Test Bot",
# )

# gpme.set_bot(new_bot)

# gpme.send_message("this bot worked?")





#https://groupme.com/join_group/68798494/9Ra827Hb
#syd test code: 68798494







# gpme = Groupme("cb6dd2b0b03b01392aed6ecce0eb34a6", debug=True)
# new_group_id = gpme.join_group("https://groupme.com/join_group/68798494/9Ra827Hb")
# new_bot = gpme.add_bot_from_id(
#     group_id = new_group_id,
#     bot_name = "Test Bot",
# )
# gpme.set_bot(new_bot)
# gpme.send_message("this bot worked?")


gpme = Groupme("cb6dd2b0b03b01392aed6ecce0eb34a6", debug=True)
gpme.name_stuff()

