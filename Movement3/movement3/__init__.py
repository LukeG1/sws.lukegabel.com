#----------------------------------------------------------------------- IMPORTS

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail #type:ignore
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from decimal import *

#https://groupme.com/join_group/52315417/4WhPRX9a

#----------------------------------------------------------------------- CONFIG

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hejgdfjlkhgjlkhg347ty7854hgudifg437895hgreoiu344t'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site012.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "fastfrisbees@gmail.com"
app.config['MAIL_PASSWORD'] = "whiteboards1!"
mail = Mail(app)

#----------------------------------------------------------------------- IMPORTS FOR ROUTES

#imports for routes
from flask import render_template, url_for, flash, redirect
from movement3.forms import LogExerciseForm, AddExerciseForm, UpdateExerciseForm, SignupForm, LoginForm, StartCompForm, JoinCompForm, ProfileForm, RequestResetForm, ResetPasswordForm # type: ignore
from movement3.models import Comp, User, Exercise, Point_Node # type: ignore
from flask_login import login_user, logout_user, current_user
from datetime import datetime, timedelta
from pprint import pprint
import secrets
import pytz
import json
import requests
import random
from requests.auth import HTTPBasicAuth
import urllib.parse
from flask_mail import Message #type:ignore

#----------------------------------------------------------------------- GroupMe API

class Groupme:
    def __init__(self, access_token:str , debug=False):
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

    def add_bot_from_id(self, group_id:str, bot_name:str, bot_pic=None):
        payload = {
            "bot" : {
                "name" : bot_name,
                "group_id" : group_id,
                "avatar_url" : bot_pic,
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


gpme = Groupme("cb6dd2b0b03b01392aed6ecce0eb34a6")

#----------------------------------------------------------------------- Admin Stuff

admin = Admin(app)

class AuthModelView(ModelView):
    def is_accessible(self):
        if(current_user.is_authenticated):
            if(current_user.admin == 1):
                return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('dashboard'))

admin.add_view(AuthModelView(Comp, db.session))
admin.add_view(AuthModelView(User, db.session))
admin.add_view(AuthModelView(Exercise, db.session))
admin.add_view(AuthModelView(Point_Node, db.session))

#----------------------------------------------------------------------- General Functions

unit_types = ["Reps","Minutes","Miles","Calories","Yards"]
unit_types = [(x,x) for x in unit_types]
category_types = ["Aerobic","Anerobic","Sport","Warm up"]
category_types = [(x,x) for x in category_types]

def time_ago(t):
    dur = (datetime.utcnow() - t).total_seconds()
    if(dur < 60):
        return f"{round(dur)} seconds ago"
    if(dur >= 60 and dur < 3600):
        return f"{round(dur/60)} minutes ago"
    if(dur >= 3600 and dur < 86400):
        return f"{round((dur/60)/60)} hours ago"
    if(dur >= 86400 ):
        return f"{round(((dur/60)/60)/24)} days ago"
    return "A while ago"

def add_user_to_comp(user : User, comp : Comp):
    users_list = comp.get_users()
    users_list.append(user.id)
    comp.set_users(users_list)

    db.session.commit()

    comps_list = user.get_comps()
    comps_list.append(comp.id)
    user.set_comps(comps_list)

    db.session.commit()

def generate_join_code():
    current_codes = []
    for comp in Comp.query.all():
        current_codes.append(comp.join_code)
    token = secrets.token_hex(4)
    while token in current_codes:
        token = secrets.token_hex(4)
    return token
    
def utc_to_est(utc):
    tz_est = pytz.timezone('US/Eastern')
    offset = tz_est.utcoffset(utc)
    offset_seconds = (offset.days * 86400) + offset.seconds
    offset_hours = offset_seconds // 3600
    return timedelta(hours=offset_hours)

def strip_time(time):
    return time - timedelta(
        hours=time.hour,
        minutes=time.minute,
        seconds=time.second,
    )

def split_by_space(s):
    return [s[:s[::-1].index(" ")*-1-1],int(s[s[::-1].index(" ")*-1-1:])]

#----------------------------------------------------------------------- Bring in the routes

@app.route('/') 
@app.route('/landing') 
def landing():
    return render_template(
        "landing.html",
        title = 'Movement',
        Comp = Comp,
    )

@app.route('/dashboard') 
def dashboard():
    if(current_user.is_authenticated == False):
        return redirect(url_for("login"))

    # for comp in Comp.query.all():
    #     pprint(comp.calculate())
    all_comp_data = []
    for comp in Comp.query.all():

        #comp.calculate()

        if(comp.running()):
            if(current_user.id in comp.get_users()):
                all_comp_data.append(comp.get_data())



    #comp_data = Comp.query.get(1).calculate()
    #pprint(all_comp_data)

    all_comp_data = sorted(all_comp_data, key = lambda i: len(i['users']),reverse=True)

    #print(all_comp_data)

    return render_template(
        "dashboard.html",
        title = 'Dashboard',
        all_comp_data = all_comp_data,
        User = User,
    )


@app.route('/stats') 
def stats():
    if(current_user.is_authenticated == False):
        return redirect(url_for("login"))

    all_comp_data = []
    for comp in Comp.query.all():
        print(comp)
        if(comp.repeating == 1 and comp.head == 1):
            if(current_user.id in comp.get_tail().get_users()):
                temp = comp
                all_pts = []
                full_data = [['Total','Name']]
                while(temp is not None):
                    pts = temp.calculate_swoll_points()
                    all_pts.append(pts)
                    full_data[0].append(temp.name)
                    temp = temp.get_next()

                #if(current_user.id in comp.get_users()):
                #print(all_pts[-1])


                for user in all_pts[-1].keys():
                    temp = [User.query.get(user),0,all_pts[-1][user]['user'].username]
                    flag = False
                    for pts in all_pts:
                        try:
                            temp.append(round(Decimal(pts[user]['swoll_pts']),2))
                        except:
                            temp.append(0)
                    temp[1] = sum(temp[3:])
                    full_data.append(temp)
                

                full_data2 = sorted(full_data[1:], key = lambda i: i[1],reverse=True)
                full_data[1:] = full_data2
                all_comp_data.append({
                    "comp":comp,
                    "data":full_data,
                })


    #all_comp_data = sorted(all_comp_data, key = lambda i: len(i['swoll_pts']),reverse=True)


    return render_template(
        "stats.html",
        title = 'Stats',
        all_comp_data = all_comp_data,
        User = User,
        sbs = split_by_space,
    )


@app.route('/logexercises', methods=["GET", "POST"]) 
def log_exercises():
    if(current_user.is_authenticated == False):
        return redirect(url_for("login"))

    form = LogExerciseForm()
    #form.exercise.choices = [(e.id,e.name) for e in Exercise.query.all()]

    uses = {}
    for pn in current_user.point_nodes:
        if(pn.exercise_id not in uses.keys()):
            uses.update({
                pn.exercise_id:1
            })
        else:
            uses[pn.exercise_id]+=1
    

    choices = []
    for e in Exercise.query.all():
        if(e.public == 1):
            choices.append((e.id,e.name))

    choices2 = []
    for choice in choices:
        ex_uses = 0
        if(choice[0] in uses.keys()):
            ex_uses = uses[choice[0]]

        choices2.append([ex_uses,choice])

    choices2 = sorted(choices2, key = lambda i: i[0],reverse=True)
    choices = [i[1] for i in choices2]
    #pprint(choices2)
    #print([i[1] for i in choices2])


    form.exercise.choices = choices
    
    if(form.validate_on_submit()):#form.reps.data is not None): #SHOULD BE VALIDATE ON SUBMIT
        # print(form.selection.data)
        # print(form.reps.data)
        # print(form.weight.data)

        reps = float(form.reps.data)
        weight = 0
        if(form.weight.data != None): weight = form.weight.data
        if(weight == ""): weight = 0
        found_ex = Exercise.query.filter_by(name=form.selection.data).first()
        
        #print(found_ex.calculate(reps, weight))

        new_point_node = Point_Node(
            timestamp = datetime.utcnow(),
            reps = reps,
            weight = weight,
            user_id = current_user.id,
            exercise_id = found_ex.id
        )

        #check for double log
        # test0 = new_point_node.exercise_id == current_user.point_nodes[-1].exercise_id
        # test1 = new_point_node.reps == current_user.point_nodes[-1].reps
        # test2 = new_point_node.weight == current_user.point_nodes[-1].weight
        # test3 = (new_point_node.timestamp-current_user.point_nodes[-1].timestamp).total_seconds()<10
        # if(test0 and test1 and test2 and test3):
        #     return redirect(url_for("dashboard"))

        db.session.add(new_point_node)
        db.session.commit()


        for comp in current_user.get_comps_ref():
            comp.update_data(new_point_node)
            db.session.commit()

            if(comp.end_time == None and comp.start <= datetime.utcnow()):

                info = comp.get_data()

                
                if(info['users'][0]['points'] >= comp.goal):
                    if(comp.group_link != None):
                        gpme.set_bot(comp.group_bot_id)
                        gpme.send_message(f"{current_user.username} has hit 100%, you now have {comp.bonus_time} minutes log your remaining points.")

                    if(comp.repeating != 0):

                        next_start = datetime.utcnow()
                        next_start += utc_to_est(next_start)
                        next_start = strip_time(next_start)
                        next_start += timedelta(days=comp.off_days+1) - utc_to_est(datetime.utcnow())

                        new_comp = Comp(
                            name = split_by_space(comp.name)[0] + " " + str(split_by_space(comp.name)[1]+1),
                            start = next_start,
                            goal = comp.goal,
                            accept_new = comp.accept_new,
                            join_code = generate_join_code(),
                            repeating = 1,
                            exercises = comp.exercises,
                            creator = comp.creator,
                            group_link = comp.group_link,
                            group_bot_id = comp.group_bot_id,
                            bonus_time = comp.bonus_time,
                            off_days = comp.off_days,
                        )

                        db.session.add(new_comp)
                        db.session.commit()

                        if(comp.global_comp == 1):
                            new_comp.global_comp = 1

                        comp.next = new_comp.id
                        db.session.commit()

                        for user in comp.get_users_ref():
                            add_user_to_comp(user, new_comp)

                        new_comp.calculate()

                        db.session.commit()

                        comp.goal_met = datetime.utcnow()
                        comp.end_time = datetime.utcnow() + timedelta(minutes=comp.bonus_time)

                    if(comp.group_link != None):
                        gpme.set_bot(comp.group_bot_id)
                        temp_time = (new_comp.start+utc_to_est(new_comp.start)).strftime("%m/%d/%Y, %H:%M:%S")
                        gpme.send_message(f"The next iteration of {comp.name} will start at {temp_time} eastern time")
                    
                    else:

                        comp.goal_met = datetime.utcnow()
                        comp.end_time = datetime.utcnow() + timedelta(minutes=comp.bonus_time)   


        db.session.commit()

        bonus_text = ""
        if(found_ex.weighted == 1 and weight != 0): bonus_text = f" at {form.weight.data} modifier"
        flash(f"Logged {form.reps.data} of {form.selection.data}"+bonus_text, "success")


        if(form.submit.data == True):
            return redirect(url_for('dashboard'))
        elif(form.submit_more.data == True):
            return redirect(url_for('log_exercises'))  

    exercise_metadata = []
    for choice in choices:
        e = Exercise.query.get(choice[0])
        if(e.public == 1):
            exercise_metadata.append([e.weighted,e.unit])

    return render_template(
        "log_exercises.html",
        title = 'Log Exercises',
        form=form,
        exercise_metadata=exercise_metadata,
        Exercise = Exercise,
    )

@app.route('/history', methods=["GET", "POST"]) 
def history():
    if(current_user.is_authenticated == False):
        return redirect(url_for("login"))

    return render_template(
        "history.html",
        title = 'History',
        Exercise = Exercise,
    )


@app.route('/friends', methods=["GET", "POST"]) 
def friends():
    if(current_user.is_authenticated == False):
        return redirect(url_for("login"))

    people = []
    for user in User.query.all():
        people.append([user.username, user.id in current_user.get_friends(), user.id])

    return render_template(
        "friends.html",
        User = User,
        Exercise = Exercise,
        people = json.dumps(people),
        title = 'friends',
    )


@app.route('/add_friend/<user_id>', methods=["GET", "POST"]) 
def add_friend(user_id):
    user = User.query.get(user_id)
    if(user is not None and user.id not in current_user.get_friends()):
        temp_friends = current_user.get_friends()
        temp_friends.append(int(user_id))
        current_user.set_friends(temp_friends)
        db.session.commit()
        flash(f"Added {user.username} to your friends!", "success")
        return redirect(url_for("friends"))

    flash("couldnt add friend", "danger")
    return redirect(url_for("friends"))


@app.route('/remove_friend/<user_id>', methods=["GET", "POST"]) 
def remove_friend(user_id):
    user = User.query.get(user_id)
    if(user is not None and user.id in current_user.get_friends()):
        temp_friends = current_user.get_friends()
        temp_friends.remove(int(user_id))
        current_user.set_friends(temp_friends)
        db.session.commit()
        flash(f"Removed {user.username} from your friends!", "success")
        return redirect(url_for("dashboard"))

    flash("couldnt remove friend", "danger")
    return redirect(url_for("friends"))
    

@app.route('/exercises', methods=["GET", "POST"]) 
def exercises():
    if(current_user.is_authenticated == False):
        return redirect(url_for("login"))

    form = AddExerciseForm()
    form.unit.choices = unit_types
    form.category.choices = category_types

    #samples = random.sample(Exercise.query.all(),3)

    if(form.validate_on_submit()):
        new_exercise = Exercise(
            name = form.name.data,
            description = form.description.data,
            link = form.link.data,
            pointvalue = form.value.data.replace("^","**"),
            unit = form.unit.data,
            category = form.category.data,
            weighted = form.weighted.data,
            public = 0,
        )

        db.session.add(new_exercise)
        db.session.commit()

        for comp in Comp.query.filter_by(accept_new=1):
            current_exes = comp.get_exercises()
            current_exes.append(new_exercise.id)
            comp.set_exercises(current_exes)

        db.session.commit()

        flash("Exercise added pending aproval!", "success")
        return redirect(url_for("dashboard"))
    
    else:
        if(request.method == 'POST'):
            flash("Check your form and try again", "danger")

    return render_template(
        "exercises.html",
        title = 'Exercises',
        form=form,
        Exercise=Exercise, # .__dict__ PRESENT DATA AS A DICT SO THAT IT CAN BE SORTED VARIOUS WAYS
    )

@app.route('/exercises/<ex_id>', methods=["GET", "POST"]) 
def admin_exercise_page(ex_id):
    if(current_user.admin != 1):
        return redirect(url_for("dashboard"))

    exercise = Exercise.query.get(ex_id)


    form = UpdateExerciseForm()
    form.unit.choices = unit_types
    form.category.choices = category_types

    if(form.validate_on_submit()):
        #exercise.name = form.name.data
        if(form.name.data != exercise.name):
            exercise.name = form.name.data
        #exercise.description = form.description.data
        if(form.description.data != exercise.description):
            exercise.description = form.description.data
        #exercise.link = form.link.data
        if(form.link.data != exercise.link):
            exercise.link = form.link.data
        #exercise.pointvalue = form.value.data.replace("^","**"),
        if(form.value.data != exercise.pointvalue):
            exercise.pointvalue = form.value.data
        #exercise.unit = form.unit.data
        if(form.unit.data != exercise.unit):
            exercise.unit = form.unit.data
        #exercise.category = form.category.data
        if(form.category.data != exercise.category):
            exercise.category = form.category.data
        #exercise.weighted = form.weighted.data
        if(form.weighted.data != exercise.weighted):
            exercise.weighted = form.weighted.data
        #exercise.public = form.public.data
        if(form.public.data != exercise.public):
            exercise.public = form.public.data

        db.session.commit()
        for comp in Comp.query.all():
            if(comp.running()):
                if(exercise.id in comp.get_exercises()):
                    comp.calculate()
        db.session.commit()

        return redirect(url_for("exercise_aproval"))


    return render_template(
        "exercise_edit.html",
        exercise = exercise,
        Exercise = Exercise,
        title = exercise.name,
        form=form
    )

@app.route('/remove_point_node/<pn_id>', methods=["GET", "POST"]) 
def remove_point_node(pn_id):
    pn = Point_Node.query.get(pn_id)
    if(pn is not None and pn.user_id == current_user.id):

        for comp in Comp.query.all():
            if(comp.running()):
                comp.remove_node(pn)
        
        db.session.delete(pn)
        db.session.commit()
    return redirect(url_for("history"))


@app.route('/exerciseaproval', methods=["GET", "POST"]) 
def exercise_aproval():
    if(current_user.admin != 1):
        return redirect(url_for("dashboard"))


    return render_template(
        "exercise_aproval.html",
        title = 'Exercise Aproval',
        #form=form,
        exercises=Exercise.query.filter_by(public=0),
    )

@app.route('/startcomp', methods=["GET", "POST"]) 
def start_comp():
    if(current_user.is_authenticated == False):
        return redirect(url_for("login"))
    
    form = StartCompForm()
    temp = []
    for u in User.query.all():
        if(u.id in current_user.get_friends()):
            temp.append((u.id,u.username))
    form.users.choices = temp

    #form.users.choices = [(u.id,u.username) for u in User.query.all()]

    temp = []
    for e in Exercise.query.all():
        if(e.public == 1):
            temp.append((e.id,e.name))
    form.exercises.choices = temp
    #form.exercises.choices = [(e.id,e.name) for e in Exercise.query.all()]

    if(form.validate_on_submit()):
        if(len(Comp.query.filter_by(name=form.name.data).all())>0):
            flash('name is already in use.','danger')
            return redirect(url_for('start_comp'))

        if(len(form.users.data)<2):
            flash('Add more users','danger')
            return redirect(url_for('start_comp'))

        if(len(form.exercises.data)==0):
            flash('Add more exercises','danger')
            return redirect(url_for('start_comp'))

        new_comp = Comp(
            name = form.name.data,
            start = datetime.utcnow(),
            goal = int(form.goal.data),
            accept_new = form.accept_new.data,
            join_code = generate_join_code(),
            creator = current_user.id,
            repeating = form.repeating.data,
            global_comp = form.global_comp.data
        )
            #         users = form.users.data,
            # exercises = form.exercises.data,
        #new_comp.set_users(form.users.data)
        new_comp.set_exercises(form.exercises.data)

        db.session.add(new_comp)
        db.session.commit()

        if(len(form.group_link.data)>10):
            new_comp.group_link = form.group_link.data
            db.session.commit()

            new_group_id = gpme.join_group(new_comp.group_link)
            new_bot = gpme.add_bot_from_id(
                group_id = new_group_id,
                bot_name = f"{new_comp.name} Admin",
                bot_pic = "https://sws.lukegabel.com/static/icon.png",
            )
            gpme.set_bot(new_bot)
            gpme.send_message(f"{User.query.get(new_comp.creator).username} has just started a new comp called {new_comp.name} within Movement. This chat will now be kept updated by a bot.")

            new_comp.group_bot_id = new_bot

        if(new_comp.repeating == 1):
            new_comp.head = 1
            new_comp.name = new_comp.name + " " + str(1)
            new_comp.bonus_time = int(form.bonus_time.data)
            new_comp.off_days = int(form.days_off.data)

        db.session.commit()

        if(form.global_comp.data == 1):
            for user in User.query.all():
                if(user.id in new_comp.get_users()):
                    temp_user_comps = user.get_comps()
                    temp_user_comps.append(new_comp.id)
                    user.set_comps(temp_user_comps)
                else:
                    add_user_to_comp(user, new_comp)

        else:
            for user in form.users.data:
                add_user_to_comp(User.query.get(user), new_comp)

        new_comp.calculate()

        db.session.commit()

        return redirect(url_for("dashboard"))
    else:
        print(form.errors)
    return render_template(
        "start_comp.html",
        title = 'Start Comp',
        form=form,
    )


@app.route('/joincomp', methods=["GET", "POST"]) 
def join_comp():
    if(current_user.is_authenticated == False):
        return redirect(url_for("login"))

    form = JoinCompForm()
    if(form.validate_on_submit()):
        selected_comp = Comp.query.filter_by(join_code=form.code.data).first()

        if(selected_comp == None):
            flash(f"Invalid code, try again.", "danger")
            return redirect(url_for("join_comp"))
        
        if(current_user.id in selected_comp.get_users()):
            flash(f"You are already in {selected_comp.name}.", "danger")
            return redirect(url_for("join_comp"))

        add_user_to_comp(current_user, selected_comp)
        selected_comp.calculate()

        flash(f"Succesfully added you to {selected_comp.name}.", "success")
        return redirect(url_for("dashboard"))

    else:
        if(len(form.errors.keys())>0):
            flash("Invalid, try again", "danger")
            return redirect(url_for("join_comp"))


    return render_template(
        "join_comp.html",
        title = 'Join Comp',
        form = form,
        #Comp = Comp,
    )

@app.route('/user/<id>', methods=["GET", "POST"]) 
def user_page(id):
    user = User.query.get(id)
    if(user == None):
        return render_template("404.html")
    return render_template(
        "profile.html",
        user=user,
        title = user.username,
    )

@app.route('/profile', methods=["GET", "POST"]) 
def profile():

    form = ProfileForm()
    if(form.validate_on_submit()):
        if(form.username.data != current_user.username):
            if(len(User.query.filter_by(username=form.username.data).all())>0):
                flash(f"username '{form.username.data}' is already in use","danger")
                return redirect(url_for("profile"))
            current_user.username = str(form.username.data)
            flash(f"Changed username to '{form.username.data}'","success")
        if(form.email.data != current_user.email):
            if(len(User.query.filter_by(email=form.email.data).all())>0):
                flash(f"email '{form.email.data}' is already in use","danger")
                return redirect(url_for("profile"))
            current_user.wmail = str(form.email.data).lower()
            flash(f"Changed email to '{form.email.data}'","success")
        if(form.color.data != current_user.color):
            current_user.color = str(form.color.data)
            flash(f"Changed color to {form.color.data}","success")
        if(form.height.data != current_user.height):
            current_user.height = float(form.height.data)
            flash(f"Changed height to {form.height.data}","success")
        if(form.weight.data != current_user.weight):
            current_user.weight = float(form.weight.data)
            flash(f"Changed weight to {form.weight.data}","success")

        db.session.commit()
        return redirect(url_for("dashboard"))

    else:
        #print(form.errors)
        pass

    return render_template(
        "profile_private.html",
        title = current_user.username,
        form=form,
    )

@app.route('/comp/<join_code>', methods=["GET", "POST"]) 
def comp_page(join_code):
    comp = Comp.query.filter_by(join_code=join_code).first()
    if(comp == None):
        return render_template("404.html")

    
    comp_data = comp.calculate_by_exercise()
    #pprint(comp.calculate_by_exercise(), width=500)

    output_data = ["Exercise",]
    colors = ["#ffffff",]
    for user in comp.get_users_ref():
        output_data.append(user.username)
        colors.append(user.color)
    output_data = [output_data]

    for e_id in comp_data.keys():
        temp = [Exercise.query.get(e_id).name]
        for user in comp.get_users_ref():
            temp.append(float(round(Decimal(comp_data[e_id][user.id]),2)))
        output_data.append(temp)

    output_data[1:] = sorted(output_data[1:], key = lambda i: sum(i[1:]),reverse=True)

    output_data.insert(0,colors)
    #pprint(output_data, width=500)

    return render_template(
        "comp_data.html",
        comp=comp,
        title = comp.name,
        output_data = output_data,
    )

@app.route('/signup', methods=["GET", "POST"]) 
def signup():
    if(current_user.is_authenticated == True):
        return redirect(url_for("dashboard"))
    form = SignupForm()
    if(form.validate_on_submit()):
        if(len(User.query.filter_by(email=form.email.data.lower()).all())>0):
            flash('Email is already in use.','danger')
            return redirect(url_for('signup'))
        if(len(User.query.filter_by(username=form.username.data).all())>0):
            flash('Username is already in use.','danger')
            return redirect(url_for('signup'))
        if(int(form.height_ft.data) != form.height_ft.data):
            flash('You entered your height incorrectly, remember to enter it in inches','danger')
            return redirect(url_for('signup'))
        if(int(form.height_in.data) != form.height_in.data):
            flash('You entered your height incorrectly, remember to enter it in inches','danger')
            return redirect(url_for('signup'))
        if(int(form.height_in.data) <= 0 or int(form.height_ft.data) <= 0):
            flash('You entered your height incorrectly, remember to enter it in inches','danger')
            return redirect(url_for('signup'))


        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        temp_height_ft = 5
        temp_height_in = 7
        if(form.height_ft.data != None): temp_height_ft = form.height_ft.data
        if(form.height_in.data != None): temp_height_in = form.height_in.data
        temp_height = (temp_height_ft*12)+temp_height_in
        print(temp_height_ft)
        print(temp_height_in)
        temp_weight = 160
        if(form.weight.data != None): temp_weight = form.weight.data

        new_user = User(
            username = form.username.data,
            email = form.email.data.lower(),
            height = temp_height,
            weight = temp_weight,
            password = hashed_password,
            color = form.color.data,
            admin = 1, #DELETE THIS!!!!!!!!!!!!!!!!!!!!!!!
        )

        db.session.add(new_user)
        db.session.commit()

        temp_friends = new_user.get_friends()
        temp_friends.append(int(new_user.id))
        new_user.set_friends(temp_friends)
        db.session.commit()

        for comp in Comp.query.all():
            if(comp.global_comp == 1):
                if(comp.end_time == None):
                    add_user_to_comp(new_user, comp)
                    comp.calculate()

        db.session.commit()

        flash("Account created! You may now log in.", "success")
        return redirect(url_for("login"))
    
    else:
        if(len(form.errors.keys())>0):
            print(form.errors)
            flash("Account Creation unsucessful, check info and try again.", "danger")
        

    return render_template(
        "signup.html",
        form = form,
        title = 'signup'
    )


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        "Password Reset Request", 
        sender=app.config['MAIL_USERNAME'], 
        recipients=[user.email]
    )
    msg.body = f"""To reset your password you have 30 minutes to visit the following link:
{url_for("reset_token", token=token, _external=True)}

If you did not make this reequest ignore this email and no changes will be made
"""
    mail.send(msg)


@app.route('/reset_password', methods=["GET", "POST"]) 
def reset_request():
    if(current_user.is_authenticated == True):
        return redirect(url_for("dashboard"))

    form = RequestResetForm()

    if(form.validate_on_submit()):
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if(user is None):
            flash("There is no user with this email",'warning')
            return redirect(url_for("reset_request"))
        send_reset_email(user)
        flash(f"A reset email has been sent to {form.email.data.lower()}, be sure to check your spam folder.",'info')
        return redirect(url_for("login"))

    return render_template(
        "reset_request.html",
        form = form,
        title = 'Reset Password'
    )

@app.route('/reset_password/<token>', methods=["GET", "POST"]) 
def reset_token(token):
    if(current_user.is_authenticated == True):
        return redirect(url_for("dashboard"))

    user = User.verify_reset_token(token)
    if(user is None):
        flash("Your token is invalid or expired", 'warning')
        return redirect(url_for("reset_request"))
    
    form = ResetPasswordForm()



    if(form.validate_on_submit()):
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash("Password successfully reset!", 'success')
        return redirect(url_for("login"))


    else:
        print(form.errors)


    return render_template(
        "reset_token.html",
        form = form,
        title = 'Reset Password'
    )



@app.route('/login', methods=["GET", "POST"]) 
def login():
    if(current_user.is_authenticated == True):
        return redirect(url_for("logout"))
    form = LoginForm()
    if(form.validate_on_submit()):
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if(user is not None and bcrypt.check_password_hash(user.password, form.password.data)):
            login_user(user, remember=form.remember.data)
            return redirect(url_for("dashboard"))

        else:
            flash("Incorrect password, try again.", "danger")  

    return render_template(
        "login.html",
        form = form,
        title = 'login'
    )




@app.errorhandler(404)
def error404(error):
    return render_template(
        "404.html",
        title = '404 Error'
    )

@app.errorhandler(500)
def error500(error):
    return render_template(
        "500.html",
        title = '500 Error'
    )
@app.errorhandler(503)
def error503(error):
    return render_template(
        "500.html",
        title = '503 Error'
    )

@app.route('/tutorial') 
def tutorial():
    return render_template(
        "tutorial.html",
        title = 'Tutorial'
    )


@app.route('/logout') 
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route('/admin') 
def admin():
    pass
