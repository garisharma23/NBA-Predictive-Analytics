import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.image as mpimg
import seaborn as sns
import time
start_time = time.time()
from sklearn import tree, neighbors

teams = ['ATL','BOS','BRO','CHA','CHI','CLE',
         'DAL','DEN','DET','GSW','HOU','IND',
         'LAC','LAL','MEM','MIA','MIL','MIN',
         'NOP','NYK','OKL','ORL','PHI','PHX',
         'POR','SAC','SAS','TOR','UTA','WAS']

found = False

while not found:
    
    print("Enter Player Name: ")
    curr_player = input().title()

    #features
    # - location x
    # - location y
    # - player
    # - shot outcome (0 or 1)

    x = []
    y = []
    player = []
    outcome = []
    change = []
    # 1 means on right court
    # 0 means on left court

    for m in teams:
        #getting data
        df = pd.read_csv('datasets/shot log ' + m + '.csv', parse_dates = True)
        

        for i in df[['location x']]:
            for j in df[i]:
                if math.isnan(j):
                    x_temp = 235
                else:
                    x_temp = j

                if x_temp < 470:
                    x.append(-1*x_temp + 470)
                    change.append(0)
                else:
                    x.append(x_temp - 470)
                    change.append(1)


        for i in df[['location y']]:
            count = 0
            for j in df[i]:
                if math.isnan(j):
                    y_temp = 250
                else:
                    y_temp = j

                if change[count] == 0:
                    y.append(500 - y_temp)
                else:
                    y.append(y_temp)
                    
                count += 1
                

        for i in df[['shoot player']]:
            for j in df[i]:
                if j.title() == curr_player:
                    found = True
                player.append(j)

        for i in df[['current shot outcome']]:
            for j in df[i]:
                outcome.append(j)



print("Select Type of Analysis")
print("------------------------------------")
print("1 - Player's Shooting Analysis")
print("2 - Most Likely Shooting Spots for the current player")

mode = 0
while not (mode > 0 and mode < 3):
    
    mode = int(input())
acc = 20
# top 25 spots for player to shoot from
total_spots = 25


features = []
labels = []

for i in range(len(player)):
    if player[i].title() == curr_player:
        features.append([x[i],y[i]])
        if outcome[i] == "SCORED":
            labels.append(1)
        else:
            labels.append(0)


features_standard = []
labels_standard = []

for i in range(len(player)):  
    features_standard.append([x[i],y[i]])
    if outcome[i] == "SCORED":
        labels_standard.append(1)
    else:
        labels_standard.append(0)
            
clf = neighbors.KNeighborsClassifier()
clf_standard = neighbors.KNeighborsClassifier()
clf.fit(features, labels)
clf_standard.fit(features_standard, labels_standard)


test = []
predictions = []
predictions_standard = []


for i in range(0,951,acc):
    for j in range(0,501,acc):
        test.append([i,j])
        predictions.append(clf.predict([[i,j]]))
        predictions_standard.append(clf_standard.predict([[i,j]]))

xs_made =[]
ys_made = []
xs_missed =[]
ys_missed = []

for i in range(len(features)):
    if labels[i] == 1:
        xs_made.append(features[i][0])
        ys_made.append(features[i][1])
    else:
        xs_missed.append(features[i][0])
        ys_missed.append(features[i][1])

# if mode == 4:
#     xs_made =[]
#     ys_made = []
#     xs_missed =[]
#     ys_missed = []
#     xs = []
#     ys = []

#     for i in range(len(test)):
#         if predictions[i] == predictions_standard[i]:
#             xs.append(test[i][0])
#             ys.append(test[i][1])
#         elif predictions[i] > predictions_standard[i]:
#             xs_made.append(test[i][0])
#             ys_made.append(test[i][1])
#         else:
#             xs_missed.append(test[i][0])
#             ys_missed.append(test[i][1])


# if mode == 3:
#     xs_made =[]
#     ys_made = []
#     xs_missed =[]
#     ys_missed = []
#     xs = []
#     ys = []

#     for i in range(len(test)):
#         if predictions[i] > 0:
#             xs_made.append(test[i][0])
#             ys_made.append(test[i][1])
#         else:
#             xs_missed.append(test[i][0])
#             ys_missed.append(test[i][1])


#split court into grid of squares with side length 20 (2 feet)
#cannot pick shot spot that is adjacent to a previous one
#counts number of shots attempted in each square within and adjacent to the current spot
#(i,j) represent to the top left corner of each square
spots = [] #list of spot coordinates with num_shots in each spot
spot_shots = []
summ_spots = []
accuracy = acc

for i in range(0,940,accuracy):
    for j in range(0,500,accuracy):
        num_shots = 0
        for k in range(0,len(features)):
            if features[k][0] >= i - accuracy and features[k][0] < i + 2*accuracy and features[k][1] >= j - accuracy and features[k][1] < j + 2*accuracy:
                num_shots += 1
                
        spots.append([i,j])
        spot_shots.append(num_shots)
                
for i in range(total_spots):
    curr = max(spot_shots)
    index = 0
    for j in range(0,len(spot_shots)):
        if spot_shots[j] == curr:
            index = j
            break
    another_temp = spots[index]    
    summ_spots.append(another_temp)
    summ_spots[-1].append(curr)
    
    #removing adjacent squares
    to_remove = []
    for j in range(-1*accuracy,2*accuracy,accuracy):
        if [spots[index][0] + j,spots[index][1] - accuracy] in spots:
            to_remove.append(spots.index([spots[index][0] + j,spots[index][1] - accuracy]))
            
        if [spots[index][0] + j,spots[index][1]] in spots:
            to_remove.append(spots.index([spots[index][0] + j,spots[index][1]]))
            
        if [spots[index][0] + j,spots[index][1] + accuracy] in spots:
            to_remove.append(spots.index([spots[index][0] + j,spots[index][1] + accuracy]))

    spots.remove(spots[index])
    spot_shots.remove(spot_shots[index])
    for j in reversed(to_remove):    
        spot_shots.remove(spot_shots[j])
        spots.remove(spots[j])
    
    
summ_xs = []
summ_ys = []
summ_shot_perc = []
summ_shot_acc = []
for i in summ_spots:
    
    num_shots_made = 0
    num_shots_missed = 0

    s_x = 0
    s_y = 0
    
    for k in range(0,len(features)):
        if features[k][0] >= i[0] - accuracy and features[k][0] < i[0] + 2*accuracy and features[k][1] >= i[1] - accuracy and features[k][1] < i[1] + 2*accuracy:
            if labels[k] == 1:
                num_shots_made += 1
            else:
                num_shots_missed += 1
            s_x += features[k][0]
            s_y += features[k][1]

    if num_shots_made + num_shots_missed == 0 or round((num_shots_made + num_shots_missed)/len(features)*100,2) < 0.5:
         summ_xs.append(s_x)
         summ_ys.append(s_y)
         summ_shot_perc.append(0)      
         summ_shot_acc.append(0)
            
    else:
        summ_xs.append(int(s_x/(num_shots_made + num_shots_missed)))
        summ_ys.append(int(s_y/(num_shots_made + num_shots_missed)))

        summ_shot_perc.append(round((num_shots_made + num_shots_missed)/len(features)*100,2))      
        summ_shot_acc.append(round(num_shots_made/(num_shots_made + num_shots_missed),2))



img = plt.imread('images/court.png')

fig = plt.figure(num = curr_player)
plt.title(curr_player + " Shot Analysis \n 2016-2017 Regular Season")
plt.xlabel('')
plt.ylabel('')
# if mode == 4:
#     plt.scatter(xs, ys, color='yellow', alpha = 1,zorder=2,s=40)
if mode == 1:
    plt.scatter(xs_missed, ys_missed, color='red', alpha = 0.5,zorder=1,s=40)
    plt.scatter(xs_made, ys_made, color='blue', alpha = 0.5,zorder=3,s=40)

if mode < 3:
    for i in range(len(summ_xs)):
        plt.scatter(summ_xs[i], summ_ys[i], color='black', alpha = summ_shot_acc[i],zorder=4,s=((summ_shot_perc[i]**0.5)*12)**2)

plt.imshow(img,zorder=0)
plt.axis('off')

def onclick(event):

    xbasket = 423
    ybasket = 248

    dist_basket = round((((event.xdata - xbasket)**2 + (event.ydata - ybasket)**2)**0.5)/10,2)
    print("\nDistance from Basket: " + str(dist_basket) + " feet")
        
    #prints info of position
    if mode < 3:
        
        for i in range(len(summ_xs)):
            
            if ((event.xdata - summ_xs[i])**2 + (event.ydata - summ_ys[i])**2)**0.5 < 10:
                #print(summ_xs[i], summ_ys[i])
                print("Shot Accuracy: " + str(round(summ_shot_acc[i]*100,2))) 
#                       "% \nPercent of All Shots Taken at this Position: "
#                       + str(round(summ_shot_perc[i],2)) + "%")
#                 break
        #print(event.x, event.y, event.xdata, event.ydata)
            
    else:
        
        for i in range(len(xs_made)):
            
            if ((event.xdata - xs_made[i])**2 + (event.ydata - ys_made[i])**2)**0.5 < 10:
                #print(summ_xs[i], summ_ys[i])
                print("Shot is Projected to Score")

        
cid = fig.canvas.mpl_connect('button_press_event', onclick)

plt.show()




        
        
