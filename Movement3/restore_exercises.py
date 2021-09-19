from movement3 import db
from movement3 import *
import json
db.session.commit()
path = r"C:\Users\lmgab\Desktop\mainEnv\webDevolpment\Movement3\exercise_save_state.json"

with open(path) as json_file:
    data = json.load(json_file)

for e in Exercise.query.all():
    #e.delete()
    db.session.delete(e)
db.session.commit()

for exercise in data:
    new_exercise = Exercise(
                name = exercise['name'],
                description = exercise['description'],
                link = exercise['link'],
                pointvalue = exercise['value'],
                unit = exercise['unit'],
                category = exercise['category'],
                weighted = exercise['weighted'],
            )



    db.session.add(new_exercise)


db.session.commit()