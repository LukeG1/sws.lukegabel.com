from movement3 import db
from movement3 import *
from flask import jsonify
import json
import datetime

db.drop_all()
db.create_all()

middle = r"C:\Users\lmgab\Desktop\mainEnv\webDevolpment\Movement3\migration_json"

with open(middle+r'\user.json', 'r') as json_file:
    user_data = json.load(json_file)

for user in user_data:
    new_user = User(
            id = user['id'],
            username = user['username'],
            email = user['email'],
            height = user['height'],
            weight = user['weight'],
            password = user['password'],
            color = user['color'],
            admin = user['admin'], 
            comps = user['comps'],
            freinds = user['friends'],
        )

    db.session.add(new_user)
    db.session.commit()



with open(middle+r'\exercise.json', 'r') as json_file:
    exercise_data = json.load(json_file)

for exercise in exercise_data:
    new_exercise = Exercise(
            id = exercise['id'],
            name = exercise['name'],
            description = exercise['description'],
            link = exercise['link'],
            pointvalue = exercise['pointvalue'],
            unit = exercise['unit'],
            category = exercise['category'],
            weighted = exercise['weighted'],
            public = exercise['public'],
        )

    db.session.add(new_exercise)
    db.session.commit()



with open(middle+r'\comp.json', 'r') as json_file:
    comp_data = json.load(json_file)

for comp in comp_data:
    new_comp = Comp(
        id = comp['id'],
        name = comp['name'],
        start = datetime.datetime.fromisoformat(comp['start']),
        goal = comp['goal'],
        accept_new = comp['accept_new'],
        join_code = comp['join_code'],
        repeating = comp['repeating'],
        exercises = comp['exercises'],
        users = comp['users'],
        creator = comp['creator'],
        group_link = comp['group_link'],
        group_bot_id = comp['group_bot_id'],
        bonus_time = comp['bonus_time'],
        off_days = comp['off_days'],
        global_comp = comp['global_comp'],
        head = comp['head'],
        data = comp['data'],
        next = comp['next'],
    )
    if(comp['end_time'] != None):
        new_comp.end_time = datetime.datetime.fromisoformat(comp['end_time'])
    if(comp['goal_met'] != None):
        new_comp.goal_met = datetime.datetime.fromisoformat(comp['goal_met']) 

    db.session.add(new_comp)
    db.session.commit()


with open(middle+r'\point_node.json', 'r') as json_file:
    point_node_data = json.load(json_file)

for point_node in point_node_data:
    new_point_node = Point_Node(
            id = point_node['id'],
            timestamp = datetime.datetime.fromisoformat(point_node['timestamp']),
            reps = point_node['reps'],
            weight = point_node['weight'],
            user_id = point_node['user_id'],
            exercise_id = point_node['exercise_id'],
        )

    db.session.add(new_point_node)
    db.session.commit()


