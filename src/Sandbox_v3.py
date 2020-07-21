import typerace
import json
import eel
import bottle_websocket
import os
#Other imports
import requests #http requests to login and verify.
import math #Calculate some encryption stuff
import time #Same as above.
import websocket #Connect to the NT live server
import threading #Used when typing the text
import random #used so bot does not get detected.
import socket





@eel.expose
def starting(username, password, races, WPM, accuracy, nitros):
  WPM = int(WPM)
  races = int(races)
  accuracy = int(accuracy) / 100
  if str(nitros) == 'True':
      nitros = 'true'
  elif str(nitros) == 'False':
      nitros = 'false'
  else:
      nitros = 'random'
  user = typerace.racer(username, password, WPM, accuracy, races, nitros)
  user.realStart()




arr = os.listdir()

if('config.json' in arr):
    usernameList = []
    passwordList = []
    racesList = []
    WPMList = []
    accuracyList = []
    nitrosList = []
    try:
        with open ('config.json') as json_file:
            data = json.load(json_file)
            for x in data:
                usernameList.append(data[x]['username'])
                passwordList.append(data[x]['password'])
                WPMList.append(int(data[x]['speed']))
                accuracyList.append(int(data[x]['accuracy']) / 100)
                racesList.append(int(data[x]['races']))
                nitrosList.append(data[x]['nitros'].lower())
        print('Settings | Username: ' + str(usernameList) + " | Password: " + str(passwordList))
        print('Settings | Speed: ' + str(WPMList) + " | Accuracy: " + str(accuracyList) + "% | Races: " + str(racesList))
        print('Settings | Nitros: ' + str(nitrosList))
    except Exception as e:
      print(e)
      print("JSON File configured incorrectly!")
      a = input()

    classList = []
    for x in range(len(usernameList)):
        classList.append(typerace.racer(usernameList[x], passwordList[x], WPMList[x], accuracyList[x], racesList[x], nitrosList[x]))
    for x in range(len(classList)):
        classList[x].realStart()
        

else:
    eel.init('web')
    eel.start("index.html")