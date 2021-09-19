#----------------------------------------------------------------------- Imports

from re import I
from movement3 import db, login_manager, app # type: ignore
from flask_login import UserMixin
from datetime import datetime
import json
from itsdangerous import TimedJSONWebSignatureSerializer as serilaizer
from pprint import pprint
import copy
from decimal import *

#----------------------------------------------------------------------- User Loader (for flask)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#----------------------------------------------------------------------- DATABASE OBJECTS

class Comp(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(), unique=True, nullable=False)                  #name of the comp
    bonus_time = db.Column(db.Integer, nullable=False, default=15)              #15 minute rule
    start =  db.Column(db.DateTime, nullable=False, default=datetime.utcnow)    #when the comp starts
    goal = db.Column(db.Integer, nullable=False, default=1000)                  #how many points to end it
    goal_met = db.Column(db.DateTime, nullable=True)                            #when the goal is met
    end_time = db.Column(db.DateTime, nullable=True)                            #when the comp is officially over
    repeating = db.Column(db.Integer, nullable=False, default=0)                #weather or not the comp repeats
    accept_new = db.Column(db.Integer, nullable=False, default=0)               #weather or not the comp accepts all new exes
    join_code = db.Column(db.String(), unique=True, nullable=True)              #how new users can join
    creator =  db.Column(db.Integer, nullable=False)
    off_days = db.Column(db.Integer, nullable=True)
    group_link = db.Column(db.String(), nullable=True)
    group_bot_id = db.Column(db.String(), nullable=True)
    global_comp = db.Column(db.Integer, nullable=True)
    head = db.Column(db.Integer, nullable=True)
    next = db.Column(db.Integer, nullable=True)

    exercises = db.Column(db.String(),unique=False,nullable=False,default="[]") #string list of ids of the exercises, get and set
    users = db.Column(db.String(), unique=False, nullable=False,default="[]")   #string list of ids of the users, get and set

    data = db.Column(db.String(), unique=False, nullable=False,default="{}") 

    def get_tail(self):
        if(self.repeating == 0):
            return False
        if(self.next == None):
            return self
        temp = self
        while(temp.get_next() is not None):
            temp = temp.get_next()
        return temp
    def running(self):
        if((self.end_time == None or datetime.utcnow() < self.end_time)): # and datetime.utcnow() > comp.start
            if(self.start <= datetime.utcnow()):
                return True
        return False
    def get_next(self):
        if(self.next == None):
            return None
        return Comp.query.get(self.next)
    def get_exercises(self):                                                    #get a list of the comps exercises
        return json.loads(self.exercises)
    def set_exercises(self,l):                                                  #set the exercises to a list dumped to a string
        self.exercises = json.dumps(l)
    def get_users(self):                                                        #get a list of the comps users
        return json.loads(self.users)
    def get_users_ref(self):                                                        #reterns a list of refrences to comps
        user_ids = json.loads(self.users)
        result = []
        for user_id in user_ids:
            result.append(User.query.get(user_id))
        return result
    def set_users(self,l):                                                      #set the users to a list dumped to a string
        self.users = json.dumps(l)

    def checkNode(self, pn):
        if(pn.timestamp > self.start):
            if(pn.exercise_id in self.get_exercises()):
                if(self.end_time == None or pn.timestamp < self.end_time):
                    if(pn.user_id in self.get_users()):
                        return True
        return False

    def calculate(self):
        result = {
            "comp":self,
            "users":[],
            "latest":None,
        }
        most_recent = None
        min_dur = 10**10
        for user in self.get_users_ref():
            user_data = {"user":user}
            total = 0
            for pn in user.point_nodes:
                if(self.checkNode(pn)): 
                    total += pn.points()
                    dur = (datetime.utcnow() - pn.timestamp).total_seconds()
                    if(dur < min_dur):
                        most_recent = pn
                        min_dur = dur
            total = float(round(Decimal(total),2))
            user_data.update({"points":round(total,2)})
            user_data.update({"percent":str(round((total/self.goal)*100,2))+"%"})
            result['users'].append(user_data)
        result['users'] = sorted(result['users'], key = lambda i: i['points'],reverse=True)
        result['latest'] = most_recent

        result_json = result
        result_json['comp'] = result_json['comp'].id
        if(result_json['latest'] != None):
            result_json['latest'] = result_json['latest'].id
        for user in result_json['users']:
            user['user'] = user['user'].id

        self.data = json.dumps(result_json)
        db.session.commit()

    def get_data(self):
        result_json = json.loads(self.data)
        result_json['comp'] = Comp.query.get(result_json['comp'])
        if(result_json['latest'] != None):
            result_json['latest'] =  Point_Node.query.get(result_json['latest'])
        for user in result_json['users']:
            user['user'] =  User.query.get(user['user'])
        return result_json

    def update_data(self,point_node):
        if(self.checkNode(point_node)):
            result_json = self.get_data()
            if(len(result_json.keys()) == 0):
                self.calculate()
            for user in result_json['users']:
                if(user['user'].id == point_node.user_id):
                    user['points'] += point_node.points()
                    user['points'] = float(round(Decimal(user['points']),2))
                    user['percent'] = str(round((user['points']/self.goal)*100,2))+"%"
                    
                    result_json['users'] = sorted(result_json['users'], key = lambda i: i['points'],reverse=True)

                    result_json2 = copy.deepcopy(result_json)
                    result_json2['comp'] = result_json2['comp'].id
                    result_json2['latest'] = point_node.id
                    for user in result_json2['users']:
                        user['user'] = user['user'].id

                    self.data = json.dumps(result_json2)
                    db.session.commit()

    def remove_node(self,point_node):
        if(self.checkNode(point_node)):
            result_json = self.get_data()
            if(len(result_json.keys()) == 0):
                self.calculate()
            for user in result_json['users']:
                if(user['user'].id == point_node.user_id):
                    user['points'] -= point_node.points()
                    user['points'] = float(round(Decimal(user['points']),2))
                    user['percent'] = str(round((user['points']/self.goal)*100,2))+"%"
                    
                    result_json['users'] = sorted(result_json['users'], key = lambda i: i['points'],reverse=True)

                    result_json2 = copy.deepcopy(result_json)
                    result_json2['comp'] = result_json2['comp'].id
                    if(result_json2['latest'] != None):
                        result_json2['latest'] = result_json2['latest'].id
                    for user in result_json2['users']:
                        user['user'] = user['user'].id

                    self.data = json.dumps(result_json2)
                    db.session.commit()

                    return result_json

    def calculate_swoll_points(self):
        data = self.get_data()
        data_users = data['users']
        output_data = {}
        i = 1
        for user in data_users:
            rank = i
            if(float(user['percent'].replace("%","")) >= 100):
                rank = 1
            if(float(user['percent'].replace("%","")) == 0):
                rank = len(data_users)
            temp = {
                "user":user['user'],
                "rank":rank,
                "swoll_pts":round(((float(user['percent'].replace("%",""))/100)*2) + (2/(2**(rank/2))),2)
            }
            output_data.update({
                user['user'].id:temp
            })
            i+=1
        return output_data

    def calculate_by_exercise(self):
        data = {}
        for e_id in self.get_exercises():
            temp = {}
            for u_id in self.get_users():
                temp.update({u_id : 0})
            data.update({e_id : temp})
        for user in self.get_users_ref():
            for pn in user.point_nodes[::-1]:
                if(self.checkNode(pn)):
                    data[pn.exercise_id][pn.user_id] += pn.points()
                elif(pn.timestamp < self.start): break
        return data


    def time_ago(self):
        dur = (datetime.utcnow() - self.start).total_seconds()
        if(dur < 60):
            return f"{round(dur)} seconds ago"
        if(dur >= 60 and dur < 3600):
            return f"{round(dur/60)} minutes ago"
        if(dur >= 3600 and dur < 86400):
            return f"{round((dur/60)/60)} hours ago"
        if(dur >= 86400 ):
            return f"{round(((dur/60)/60)/24)} days ago"
        return "A while ago"

    def __str__(self):
        return f"COMP({self.id},'{self.name}')"




class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(), unique=True, nullable=False)              #username
    email = db.Column(db.String(), unique=True, nullable=False)                 #email
    height = db.Column(db.Float, nullable=False, default=65)                    #height
    weight = db.Column(db.Float, nullable=False, default=160)                   #weight
    password = db.Column(db.String(), nullable=False)                           #hashed password
    color = db.Column(db.String(), nullable=False, default="#292929")           #color
    admin = db.Column(db.Integer, nullable=False, default=0)                    #weather or not they are an admin
    group_link = db.Column(db.String(), nullable=True)

    point_nodes = db.relationship('Point_Node', backref='user', lazy=True)      #2 way relationship one->many all their point nodes
    comps = db.Column(db.String(), unique=False, nullable=True,default="[]")    #string list of users comp ids
    friends = db.Column(db.String(), unique=False, nullable=True,default="[]") 

    def get_comps(self):                                                        #get a list of the users comps (id)
        return json.loads(self.comps)
    def get_comps_ref(self):                                                        #reterns a list of refrences to comps
        comp_ids = json.loads(self.comps)
        result = []
        for comp_id in comp_ids:
            result.append(Comp.query.get(comp_id))
        return result
    def set_comps(self,l):                                                      #set the comps to a list dumped to a string
        self.comps = json.dumps(l)
    
    def get_users(self):                                                        #get a list of the users comps (id)
        return json.loads(self.users)
    def get_users_ref(self):                                                        #reterns a list of refrences to comps
        users_ids = json.loads(self.users)
        result = []
        for users_id in users_ids:
            result.append(User.query.get(users_id))
        return result
    def set_friends(self,l):                                                      #set the comps to a list dumped to a string
        self.users = json.dumps(l)
        
    def get_friends(self):                                                        #get a list of the users comps (id)
        return json.loads(self.friends)
    def get_friends_ref(self):                                                        #reterns a list of refrences to comps
        friends_ids = json.loads(self.friends)
        result = []
        for friends_id in friends_ids:
            result.append(User.query.get(friends_id))
        return result
    def set_friends(self,l):                                                      #set the comps to a list dumped to a string
        self.friends = json.dumps(l)
        
    def get_reset_token(self, expires_sec=30*60):
        s = serilaizer(app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = serilaizer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
            return User.query.get(user_id)
        except:
            return None


    def __str__(self):
        return f"USER({self.id},'{self.username}')"

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(), unique=True, nullable=False)                  #name of the exercise
    description = db.Column(db.String(), unique=True, nullable=False)           #description of the exercise
    link = db.Column(db.String(), unique=False, nullable=False)                  #link to a good source on the exercise
    unit = db.Column(db.String(), unique=False, nullable=False)                  #how is this exercise measured
    category = db.Column(db.String(), unique=False, nullable=False)              #what type of exercise is this
    weighted = db.Column(db.Integer, nullable=False, default=0)                 #weather or not this is a weighted exercise
    pointvalue = db.Column(db.String(), unique=False, nullable=False)            #string function for how much its worth
    public = db.Column(db.Integer, nullable=False, default=1)                   #weather or not an exercise is visible to the public

    def calculate(self,reps,weight=0):
        run_str = "res = "+self.pointvalue.replace("M",str(weight))
        loc = {}
        exec(run_str, loc)
        val = round(loc['res']*reps,4)
        return val

    def __str__(self):
        return f"EXERCISE({self.id},'{self.name}','{self.pointvalue}')"

class Point_Node(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)    #when the points were logged
    reps = db.Column(db.Float, nullable=False)                                     #how many units of the exercise you did     
    weight = db.Column(db.Float, nullable=False)                                   #how much weight you did those reps with

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)       #id of the user who logged it
    exercise_id = db.Column(db.Integer, nullable=False)                            #id of the exercise logged 

    def points(self):                                                              #returns the number of points earned from this node
        val = Exercise.query.get(self.exercise_id).calculate(self.reps,self.weight)
        return val

    def time_ago(self):
        dur = (datetime.utcnow() - self.timestamp).total_seconds()
        if(dur < 60):
            return f"{round(dur)} seconds ago"
        if(dur >= 60 and dur < 3600):
            return f"{round(dur/60)} minutes ago"
        if(dur >= 3600 and dur < 86400):
            return f"{round((dur/60)/60)} hours ago"
        if(dur >= 86400 ):
            return f"{round(((dur/60)/60)/24)} days ago"
        return "A while ago"

    def __str__(self):
        return f"POINT_NODE({self.id},{self.reps},{self.weight},{User.query.get(self.user_id)},{Exercise.query.get(self.exercise_id)})"

