import requests #http requests to login and verify.
import math #Calculate some encryption stuff
import time #Same as above.
import websocket #Connect to the NT live server
import json #Parse through responses from http request & live server
import threading #Used when typing the text
import random #used so bot does not get detected.
import socket


class racer():
    def __init__(self, usr, pwd, spd, acc, rcs, nitro):
        self.sesh = requests.Session() #HTTP session to be used

        self.username = usr
        self.password = pwd
        self.speed = spd
        self.accuracy = acc
        self.races = rcs
        self.nitros = nitro
    def getCookies(self, cookie_jar): #Turn cookies from a jar into a string.
        cookie_dict = cookie_jar.get_dict() #Dict
        if('2G8DA665' in cookie_dict):
            self.cookie_speed = str(cookie_dict['2G8DA665'])
        else:
            self.cookie_speed = "20"

        found = ['%s=%s' % (name, value) for (name, value) in cookie_dict.items()]
        return ';'.join(found)
    def get_time(self): #Hash a timestamp
        num = round(time.time())
        alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
        length = 64
        encoded = ''
        while num > 0:
            encoded = alphabet[num % length] + encoded
            num = math.floor(num / length)
        return encoded
    def login(self): #Login to account
        log = self.sesh.post("https://www.nitrotype.com/api/login", data = {"username": self.username, "password":self.password}).json()
        return log['success']
    def logout(self): #Logout of account
        log_out = self.sesh.post("https://www.nitrotype.com/api/logout")
        return log_out.text
    def raceRequests(self): #Requests for race verification
        sid_get_request = self.sesh.get("https://realtime1.nitrotype.com/realtime/?_primuscb=" + self.get_time() + "&EIO=3&transport=polling&t=" +  self.get_time() + "&b64=1").text
        sid = json.loads(sid_get_request.split("96:0")[1])['sid'] #SID is used in other requests
    
        raceCheck = self.sesh.post("https://realtime1.nitrotype.com/realtime/?_primuscb=" + self.get_time() + "&EIO=3&transport=polling&t=" + self.get_time() + "&b64=1&sid=" + sid, data = sid_get_request)

        cookieString = self.getCookies(self.sesh.cookies)
        raceUrl = "wss://realtime1.nitrotype.com/realtime/?_primuscb=" + self.get_time() + "&EIO=3&transport=websocket&sid=" + sid + "&t=" + self.get_time() + "&b64=1"
        return[cookieString, raceUrl] #Need cookies & url to connect to websocket.

    def on_open(self, ws): #Requests to send once the WS is open - verifies that websocket is good
        self.closed = False
        ws.send('2probe')
        ws.send("5")
        payload = '4{"stream":"race","msg":"join","payload":{"avgSpeed":' + self.cookie_speed + ',"update":3417}}'
        ws.send(payload)

    #ws.close()
    def on_message(self,ws, message):
        print(message)
        def scan_for_text(message): #Scanning messages to see if we can find the typing text.
            try:
                message = json.loads(message[1:])['payload']
                if "lessonLength" in message: #If message contains typing text
                    return message.popitem()[1]
            except:
                None
            return None

        def type(msg):
            if(len(msg) == 0 or str(msg[0]).startswith("{'user")): #These are wrong messages
                return
            delay1 = random.randrange(7, 9) / 10 #If the delays are longer apart, they have more variety. Put in race function
            delay2 = random.randrange(11, 14) / 10
            words = msg.split(" ") #Turn into a list
            wordString = ' '.join(words)#Sounds nicer than "msg"
            biggestWord = max([len(w) for w in (words[0:len(words)-1])]) #Get len of biggest word
            words = [w + ' ' for w in words[0:len(words)-1]] + [words[len(words)-1]] #add spaces
            numOfChars = len(wordString)
            numOfWords = numOfChars/5
            numOfSecs = (numOfWords/self.speed) * 60
            sleepTime = numOfSecs / numOfChars
            sleep1 = round((sleepTime * delay1), 6) * 10000000
            sleep2 = round((sleepTime * delay2), 6) * 10000000 #Get time to sleep after each char
            time.sleep(4.3) #wait until race starts
            if(self.nitros == 'true'):
                usedNitro = False
            elif(self.nitros == 'random'): #Random check to see if we should use nitros
                check = random.randrange(1,3)
                if(check == 1):
                    usedNitro = False
                else:
                    usedNitro = True
            else:
                usedNitro = True
            ws.send('4{"stream":"race","msg":"update","payload":{"t":1,"f":0}}') #First character has to have "f":0
            print('4{"stream":"race","msg":"update","payload":{"t":1,"f":0}}')
            t  = 2
            e = 1

            for w in words:
                if self.closed == True:
                    break
                if(int(len(w)) >= int(biggestWord) and usedNitro == False):
                    t += len(w)
                    payload = '4{"stream":"race","msg":"update","payload":{"n":1,"t":' + str(t) + ',"s":' + str(len(w)) + '}}' #Using nitro
                    ws.send(payload)
                    time.sleep(0.2)
                    payload = '4{"stream":"race","msg":"update","payload":{"t":' + str(t) + '}}' #sending another character
                    ws.send(payload)
                    t += 1
                    usedNitro = True
                else:
                    for c in w:
                        if self.closed == True:
                            break
                        errorProbability = random.randrange(0,75) / 100
                        accuracyWrongPercentage = 1 - self.accuracy
                        if(accuracyWrongPercentage >= errorProbability):
                            payload = '4{"stream":"race","msg":"update","payload":{"e":' + str(e) + '}}' #sending error
                            ws.send(payload)
                            e += 1
                        if t % 4 == 0 or t >= numOfChars - 4:
                            payload = '4{"stream":"race","msg":"update","payload":{"t":' + str(t) + '}}' #sending character
                            ws.send(payload)
                        t += 1
                        sleeptime = random.randrange(int(sleep1), int(sleep2)) / 10000000 #sleep between each character at a random interval according to the WPM
                        time.sleep(sleeptime)
            if self.closed == False:
                ws.close()
        words = scan_for_text(message)
        if words != None:

            typingTheText = threading.Thread(target = type, args  = [words]) #starting a thread to race
            typingTheText.start()
    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        self.closed = True
        print("### closed ###")
    def race(self):
        print("New Race: ")
        starting = self.raceRequests()
        cookieString = starting[0]
        socketLink = starting[1] #Connecting to websocket below, lambda so it can be used in a class
        self.ws = websocket.WebSocketApp(socketLink,
                              on_message = lambda ws,msg: self.on_message(ws, msg),
                              on_error   = lambda ws,msg: self.on_error(ws, msg),
                              on_close   = lambda ws:     self.on_close(ws),
                              header = {'cookie': cookieString, 'Origin':'https://www.nitrotype.com', 'User-Agent':"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/55.0.2883.87 Chrome/55.0.2883.87 Safari/537.36"})
        self.ws.on_open = lambda ws:     self.on_open(ws)                        
        self.ws.run_forever()
    def startBot(self):
        self.currentRaces = 0
        while self.currentRaces < self.races:
            if(self.currentRaces % 50 == 0):
                self.logout()
                logged = self.login() #every 100 races
                if str(logged) == 'False':
                    print("Invalid Username/Password! Please restart the program and try again.")
                    a = input()
                    return
                else:
                    print("Loggged in successfully!")
            print("Racing...")
            self.race()
            self.currentRaces += 1
            time.sleep(7)
            if self.currentRaces == self.races:
                print("Race completed! (Race #" + str(self.currentRaces) + ')')
            
        print("Completed Races!")
        a = input()
    def realStart(self):
        typingThread = threading.Thread(target = self.startBot, args = [])
        typingThread.start()

