# copy users to json then back to databse
# copy comps to json then back to databse
# copy exes to json then back to databse
# copy point_nodes to json then back to databse



from movement3 import db
from movement3 import *
from flask import jsonify
import json
import datetime

middle = r"C:\Users\lmgab\Desktop\mainEnv\webDevolpment\Movement3\migration_json"

user_data = []
for user in User.query.all():
    user_data.append({c.name: getattr(user, c.name) for c in user.__table__.columns})

with open(middle+r'\user.json', 'w+') as outfile:
    json.dump(
        user_data, 
        outfile, 
        indent=4
    )
    
exercise_data = []
for exercise in Exercise.query.all():
    exercise_data.append({c.name: getattr(exercise, c.name) for c in exercise.__table__.columns})

with open(middle+r'\exercise.json', 'w+') as outfile:
    json.dump(
        exercise_data, 
        outfile, 
        indent=4
    )
    
comp_data = []
for comp in Comp.query.all():
    temp = {c.name: getattr(comp, c.name) for c in comp.__table__.columns}
    for key in temp.keys():
        if(type(temp[key]) == datetime.datetime):
            temp[key] = temp[key].isoformat()
    comp_data.append(temp)

with open(middle+r'\comp.json', 'w+') as outfile:
    json.dump(
        comp_data, 
        outfile, 
        indent=4
    )
    
point_node_data = []
for point_node in Point_Node.query.all():
    temp = {c.name: getattr(point_node, c.name) for c in point_node.__table__.columns}
    for key in temp.keys():
        if(type(temp[key]) == datetime.datetime):
            temp[key] = temp[key].isoformat()
    point_node_data.append(temp)

with open(middle+r'\point_node.json', 'w+') as outfile:
    json.dump(
        point_node_data, 
        outfile, 
        indent=4
    )
    









