from movement3 import db #type: ignore
from movement3.models import Comp, User, Exercise, Point_Node #type: ignore
import matplotlib.pyplot as plt
import json
import numpy as np
import scipy
from scipy.interpolate import make_interp_spline, BSpline
from pprint import pprint

data = []


timestamps = []
for pn in Point_Node.query.all():
    timestamps.append(pn.timestamp)

# print(min(timestamps))
# print(max(timestamps))

users = User.query.all()
for user in users:
    temp_data = {
        "name":user.username,
        "color":user.color,
        "x":[min(timestamps)],
        "y":[0],
    }
    tot = 0
    for pn in user.point_nodes:
        tot += pn.points()
        temp_data['x'].append(pn.timestamp)
        temp_data['y'].append(tot)

    data.append(temp_data)


pprint(data)


for user in data:
    color = "#000000"
    if(user['color'] != ''):
        color = user['color']
    # T = np.array([i for i in range(len(user['y']))])
    # xnew = np.linspace(T.min(), T.max(), 300)
    # spl = make_interp_spline(T, user['y'], k=2)
    # power_smooth = spl(xnew)
    #plt.plot(xnew, power_smooth, color=user['color'], label=user['name'])
    plt.plot(user['x'], user['y'], color=color, label=user['name'])
plt.title('All data')
plt.ylabel('Points Earned')
plt.xlabel('time')
#plt.legend()
plt.show()





#plt.plot(xnew,power_smooth, color=person['color'], label=person['name'])
#plt.plot(T,stripList(MA), color=person['color'], label=person['name'])
# temp = plt.twiny()
# temp.plot(xnew,power_smooth, color=person['color'], label=person['name'])