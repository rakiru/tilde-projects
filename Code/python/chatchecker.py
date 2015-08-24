#!/usr/bin/python
import fileinput
import json
import time
import calendar
import shutil

logfile = "/home/jumblesale/Code/irc/log"
outfile = "/home/krowbar/logs/userData.json"
userData = {} #hash keyed by "user" that contains an array of timestamps
#we only care about recent chats, let's say for the past two weeks
timeCutoff = calendar.timegm(time.gmtime()) - (2 * 7 * 24 * 60 * 60)

with open(logfile, "r") as log:
    for line in log:
        try:
            time, user, message = line.split("\t", 3)
            time = int(time)
        except ValueError:
            continue #There are some bad lines in the log file that we'll ignore if we can't parse
        if time > timeCutoff:
            #if the user already exists in the list
            if user in userData:
                userData[user].append(time) #append the new time
            else: #if they are new
                userData[user] = [time] #create a new list
with open(outfile + ".tmp", "w") as tmpFile:
    tmpFile.write(json.dumps(userData))
shutil.move(outfile + ".tmp", outfile)
