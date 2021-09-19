#----------------------------------------------------------------------- Setting up the database

# from movement3 import db #type: ignore
# db.create_all()

#----------------------------------------------------------------------- Add User

# from momentum_flask import db
# from momentum_flask import User, Project, Time_Entry, Task_Entry

# user_1 = User(
#     username = "Luke Gabel",
#     email = "lmgabel@gmail.com",
#     password = "password",
#     admin = 1,
# )

# db.session.add(user_1)
# db.session.commit()

#----------------------------------------------------------------------- Common Queries

# from movement3 import db
# from movement3 import *

# #Object.query.all()

# users = User.query.all() #get a list of all the users
# print(users[0])
# users[0].admin = 1
# db.session.commit()

# first = User.query.first() #get the first user
# print(first)

# result = User.query.filter_by(username = "Luke Gabel").first() #get the first user with username "Luke Gabel"
# # could also have used .all()
# print(result)

# user_by_id = User.query.get(1) #user with id = 1
# print(user_by_id)

#----------------------------------------------------------------------- Add Project to User

# from momentum_flask import db
# from momentum_flask import User, Project, Time_Entry, Task_Entry

# user_by_id = User.query.get(1) #user with id = 1
# print(user_by_id)

# project_1 = Project(
#     name = "generic subject",
#     color = "#0000FF",
#     user_id = user_by_id.id, # this number is the id of the user to whom this project belongs
# )

# db.session.add(project_1)
# db.session.commit()

# print(project_1)
# print(user_by_id.projects[0])

#----------------------------------------------------------------------- Clear Database

# from movement3 import db
# from movement3 import *

# db.drop_all()
# db.create_all()


from movement3 import db
from movement3 import *
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

for user in User.query.all():
    user.password = bcrypt.generate_password_hash("1").decode('utf-8')

db.session.commit()


# molly = User.query.filter_by(username="Molly Caballero").first()
# for pn in molly.point_nodes:
#     print(pn,"   |   ",pn.points())

#----------------------------------------------------------------------- 


# #weighted
#                     #.01x^2 + .01x
# point_value = "res = ((.01*((x)**2))+(.01*(x)))"
# weight = 10
# reps = 50

# filled_in = point_value.replace("x",str(weight))

# print(filled_in)

# loc = {}
# exec(filled_in,loc)

# points_earned = round(loc['res']*reps,4)

# print(points_earned)


# #non weighted

# point_value = "res = (10)"
# weight = 10
# reps = 50

# filled_in = point_value.replace("x",str(weight))

# print(filled_in)

# loc = {}
# exec(filled_in,loc)

# points_earned = round(loc['res']*reps,4)

# print(points_earned)