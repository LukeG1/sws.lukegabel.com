import datetime
from movement3 import db  # type: ignore
from movement3.models import Comp, User, Exercise, Point_Node  # type: ignore
import matplotlib.pyplot as plt
import json
import numpy as np
import scipy
from scipy.interpolate import make_interp_spline, BSpline
import scipy.interpolate
from pprint import pprint


print("canclulating times")

inc = 60
total_days = (Point_Node.query.order_by(Point_Node.id.desc()).first().timestamp-Point_Node.query.first().timestamp).days+1
times = []
timeI = Point_Node.query.first().timestamp
for _ in range(((total_days)*24)*int(60/inc)):
    times.append(timeI)
    timeI += datetime.timedelta(minutes=inc)


# pprint(times)
# print(len(times))


users = []

for user in User.query.all():
    print(f"getting data for {user.username}")
    temp = {
        "name": user.username,
        "color": user.color,
        "x": [],
        "y": [],
    }
    start = 0
    tot = 0
    i = 0
    for time in times:
        temp["x"].append(i)
        c = 0
        for pn in user.point_nodes[start:]:
            if(pn.timestamp >= time):
                break
            tot += pn.points()
            c += 1
        start += c
        temp["y"].append(tot)
        i += 1

    users.append(temp)
    #break


for user in users:
    color = "#000000"
    if(user['color'] != ''):
        color = user['color']

    coefs = np.polyfit(user['x'], user['y'], 132)
    newY = []
    for num in user['x']:
        tot = 0
        i = 1
        for coef in coefs[:-1]:
            tot += (num ** (len(coefs)-i)) * coef
            i += 1
        tot += coefs[-1]
        newY.append(tot)

    #plt.plot(user['x'], user['y'], color=color, label=user['name'])
    plt.plot(user['x'], newY, color=color, label=user['name'])


plt.title('All data')
plt.ylabel('Points Earned')
plt.xlabel('time')
plt.show()

# for num in range(len(users[0]['x'])):
#     print("[",users[0]['x'][num]/215,",",users[0]['y'][num]/1561,"]",",")



