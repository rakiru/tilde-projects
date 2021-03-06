#!/usr/bin/python
# http://wiki.shellium.org/w/Writing_an_IRC_bot_in_Python

# Import some necessary libraries.
import socket
import os
import sys
from optparse import OptionParser
import fileinput
import random
import time
import re
import operator

import msgformatter
import madlib

class State:
    idle = 0 # When the bot is started and after it has finished a story
    thinking = 1 # I intentionally speed throttle this bot so it feels a little more natural
    story_selection = 2 # When the bot is waiting for a user input for story selection
    word_input = 3 # When the bot is waiting for user input after prompted for a word

# Globals
MAX_LINE = 80 # The maximum number of characters in a line
MAX_STORIES = 5 # The maximum number of stories a user can pick from
THROTTLE_FACTOR = 1 # A factor by which all sleep event durations will be multiplied
# Allow madlbibbot to run multiple simultaneous stories 
state = {} # The current state of the bot
stories = {} # The list of stories available to users
story = {} # The madlib story currently being worked on
nextword = {} # The word that the bot is currently expecting data for

parser = OptionParser()

parser.add_option("-s", "--server", dest="server", default='127.0.0.1',
                  help="the server to connect to", metavar="SERVER")
parser.add_option("-c", "--channel", dest="channel", default='#madlibs',
                  help="the channel to join", metavar="CHANNEL")
parser.add_option("-n", "--nick", dest="nick", default='madlibbot',
                  help="the nick to use", metavar="NICK")

(options, args) = parser.parse_args()

def resetGlobals(channel=""):
    global state
    global stories
    global story
    global nextword

    if channel == "":
        state = {}
        stories = {}
        story = {}
        nextword = {}
    else:
        state[channel] = State.idle
        stories[channel] = []
        story[channel] = ""
        nextword[channel] = {}

def get_stories(channel):
    global state
    global stories
    state[channel] = State.thinking
    stories[channel] = madlib.find_stories(MAX_STORIES, True)
    if len(stories[channel]) == 0:
        sendmsg(channel, "Uh oh! There are no stories!")
        state[channel] = State.idle
    else:
        sendmsg(channel, "Here are a couple good stories:")
        time.sleep(1 * THROTTLE_FACTOR)
        for idx, story in enumerate(stories[channel]):
            sendmsg(channel, "[{}] {} ({} words)".format(idx, story[0], story[2]))
            time.sleep(0.5 * THROTTLE_FACTOR)
        sendmsg(channel, "Please select a story by index:")
        state[channel] = State.story_selection

# Handle user input when the bot is directly addressed
def handle_bot_msg(channel, msg):
    global state
    global stories

    if channel not in state:
        state[channel] = State.idle

    saved_state = state[channel]
    state[channel] = State.thinking
    time.sleep(1 * THROTTLE_FACTOR)

    # First check if we should quit the current game
    if saved_state != State.idle and msg == "!quit":
        quit_game(channel)
    elif saved_state == State.idle and msg == "startgame":
        get_stories(channel)
    elif saved_state == State.story_selection:
        handle_story_selection(channel, msg)
    elif saved_state == State.word_input:
        handle_story_step(channel, msg)
    else:
        state[channel] = State.idle

# Handle how to quit the game
def quit_game(channel):
    resetGlobals(channel)
    sendmsg(channel, "Ok, quitting the current game.")

# Handle user input when we are in story selection mode
def handle_story_selection(channel, msg):
    global stories
    global state
    try:
        imsg = int(msg)
        if imsg < 0 or imsg > len(stories[channel]):
            sendmsg(channel, "Selection out of bounds. Try again!")
            return
        time.sleep(1 * THROTTLE_FACTOR)
        sendmsg(channel, "Give me a second to load up {}".format(stories[channel][imsg][0]))

        with open(stories[channel][imsg][1], "r") as storyFile:
            story[channel] = storyFile.read()
        stories[channel] = {} # Clear out the saved selectable stories in memory
        story_start(channel)
    except ValueError:
        sendmsg(channel, "Invalid selection. Try again!")
        state[channel] = State.story_selection

# Handle when a story is being started
def story_start(channel):
    global story
    global state
    global nextword

    state[channel] = State.thinking
    sendmsg(channel, "Alright! Let's get started!")
    nextword[channel] = madlib.find_next_word(story[channel], True)
    time.sleep(0.5 * THROTTLE_FACTOR)
    sendmsg(channel, "Give me {}:".format(nextword[channel][1]))
    state[channel] = State.word_input

# Handle user input when we have asked the user for input and are expecting a
# response
def handle_story_step(channel, msg):
    global state
    global story
    global nextword

    state[channel] = State.thinking
    word = nextword[channel] #madlib.find_next_word(story[channel])
    if word is not None:
        story[channel] = madlib.replace_word(story[channel], nextword[channel][0], msg)
    time.sleep(1 * THROTTLE_FACTOR)

    nextword[channel] = madlib.find_next_word(story[channel], True)
    if nextword[channel] is None:
        finish_story(channel)
        return
    #else
    count = madlib.count_words(story[channel])
    sendmsg(channel, "Thanks! Now give me {} ({} words left)".format(nextword[channel][1], count))
    state[channel] = State.word_input

# Finish the story
def finish_story(channel):
    global state
    global story

    sendmsg(channel, "Ok, here's the story...");
    sendmsg(channel, '=' * MAX_LINE)
    for line in story[channel].splitlines():
        for part in madlib.yield_lines(line, MAX_LINE):
            time.sleep(0.4 * THROTTLE_FACTOR)
            sendmsg(channel, part)
    padlen = (MAX_LINE - 9)/2
    mod = (MAX_LINE - 9) % 2
    sendmsg(channel, '=' * padlen + ' THE END ' + '=' * (padlen + mod))

    story[channel] = ""
    state[channel] = State.idle

# System things
def ping():
    ircsock.send("PONG :pingis\n")

def sendmsg(chan , msg):
    ircsock.send("PRIVMSG {} :{}\n".format(chan, msg))

def joinchan(chan):
    ircsock.send("JOIN {}\n".format(chan))

def rollcall(channel, botnick):
    sendmsg(channel, "Do you like MadLibs? Start a collaborative story by saying '{}: startgame'".format(botnick))

def connect(server, channel, botnick):
    ircsock.connect((server, 6667))
    ircsock.send("USER {} {} {} :krowbar\n".format(botnick, botnick, botnick)) # user authentication
    ircsock.send("NICK {}\n".format(botnick))
    joinchan(channel)

def listen(botnick):
    botmsgre = re.compile('^{}\:?\s*(.*)$'.format(botnick)) # re to strip the bot's name from a message
    while 1:
        ircmsg = ircsock.recv(2048)
        ircmsg = ircmsg.strip('\n\r')

        if ircmsg.find("PING :") != -1:
            ping()

        formatted = msgformatter.format_message(ircmsg)
        if "" == formatted:
            continue
        # print formatted

        split = formatted.split("\t")
        msgtime = split[0]
        user = split[1]
        command = split[2]
        channel = split[3]
        message = split[4]

        if message.startswith("!rollcall") == True or message.startswith("!help") == True:
            rollcall(channel, botnick)
        elif message.startswith(botnick) == True:
            botmsg = botmsgre.match(message).group(1)
            handle_bot_msg(channel, botmsg)

        sys.stdout.flush()
        time.sleep(1 * THROTTLE_FACTOR)

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connect(options.server, options.channel, options.nick)
listen(options.nick)
