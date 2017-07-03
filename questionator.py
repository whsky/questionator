#############################################################################
# Steve Iannaccone
# April 2017
#
# Flask app for randomly selecting a student to ask a question
#   This requires that Slacker installed (https://github.com/os/slacker),
#   and that you have Slack API token saved to your bash profile as
#   'SLACK_TOKEN' (https://api.slack.com/tokens), and that the :qbot: custom
#   emoji is available on the channel you are using (if you are messaging
#   the channel)
#
# Run this script from the terminal, it needs two additional arguements.
#   1: --chan for what Slack channel on gStudents to pull the class roster from
#   2: --ping whether or not to send a bot message to the channel when a
#            question is asked
#
# e.g.:
#   $ python questionator.py --chan='g39ds_platte' --ping=False
# This will use #g39ds_platte members as the class roster, and will not send a
#   message to that channel when a question is asked.
#
# This should take about 20sec to start up.
#############################################################################

import os
import sys
import argparse
from slacker import Slacker
import pandas as pd
from flask import Flask, request, url_for, render_template, request
import cPickle as pickle
from pyfiglet import Figlet
import numpy as np
import pandas as pd
from random import randrange, sample, choice

def init_slack_channel(api_token, channel_name):
    slack = Slacker(api_token)
    print("Collecting available Slack channels...")
    chnls = slack.channels.list().body['channels']
    chnl_names = []
    for x in range(len(chnls)):
        chnl_names.append(chnls[x]['name'])

    #find where our channel is in the list:
    chan_idx = chnl_names.index(channel_name)

    #Collect all channel's member IDs:
    print("Collecting members from channel #{}...".format(channel_name))
    all_members = chnls[chan_idx]['members']
    #Filter out any member with an @galvanize email address:
    print("Filter out any member with an @galvanize email address...")
    students = []
    for idx, member in enumerate(all_members):
        email = slack.users.profile.get(member).body['profile']['email']
        if '@galvanize.com' not in email and member not in students:
            students.append(member)

    return slack, students

def get_member_info(slack, member_id):
    """
    INPUT: slacker slack API object, str of Slack member ID
    OUTPUT: User name, and URL to User avatar
    """
    name = slack.users.profile.get(member_id).body['profile']['real_name']
    avatar = slack.users.profile.get(member_id).body['profile']['image_192']

    return name, avatar

def id_to_username(slack_member_list, member_id):
    """
    INPUT: list of members in Slack channel, String of member ID to convert
        to username
    OUTPUT: String of member's Username
    """
    name = slack.users.profile.get(member_id).body['profile']['real_name']
    for member in slack_member_list:
        if member['profile']['real_name'] == name:
            return member['name']

def getUserMap(slack_member_list):
  #get all users in the slack organization
  """
  I modified this from the `slack_history.py` script from Chandler Abraham
  """
  userIdNameMap = {}
  for user in slack_member_list:
    userIdNameMap[user['id']] = user['name']
  return userIdNameMap

def direct_message(user_map, user_id):
    """
    INPUT: Dict of {userID:username}, Slack user ID as String
    OUTPUT: None (Post a direct message to user_id on Slack)
    --------------------------------------------------------------------------
    We have to open a DM channel on slack to be able to post directly to a user.
        afterwords we collect the new DM channel ID and use it to post a message
        from the qbot questionator Slack bot.
    """
    #Open DM channel with the user:
    new_dm = slack.im.open(user=user_id)
    dm_id = new_dm.body['channel']['id']

    #Get username for user ID paseed in
    username = user_map[user_id]

    #Select one of the following messages at random to send to student:
    message_list = \
        ["Oh snap! That's a tough one @{}...glad I'm not in your shoes."\
            .format(username),
        "Hmmmmm, think it over @{}...you got this!"\
            .format(username),
        "Psssst...The instructor just asked you a question @{}."\
            .format(username),
        "Uh-oh, better look up @{}, you just got asked a question!"\
            .format(username)
        ]
    qbot_message = choice(message_list)
    #requires that `:qbot:` custom emoji is available for your channel...
    #Also set parse='full', and don't set the link_names variable for
    #   hot-linking to username
    slack.chat.post_message(channel=dm_id,
                            text=qbot_message,
                            username='Questionator',
                            icon_emoji=':qbot:',
                            parse='full',
                            as_user=False)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', class_name=channel_name)


@app.route('/question', methods=['POST'])
def qbot():
    #Find students who have answered the fewest questions:
    df_min = df[df.num_quest == min(df.num_quest)]
    stud_min = df_min.index.values.tolist()
    #Pick a student with minimal questions asked at random:
    random_index = choice(stud_min)

    #Collect Student's Slack user ID and avatar pic link:
    member_name, avatar_link = get_member_info(slack, df.roster[random_index])
    #+1 on the number of questions answered:
    df.num_quest[random_index] += 1
    #slack.users.list().body['members'][1]['name']
    username = df.username[random_index]
    user_id = df.roster[random_index]

    if ping_slack:
        #Have the Questionator Slack the user a message:
        direct_message(user_map, user_id)

    return render_template('question.html',
                            avatar=avatar_link,
                            name=member_name,
                            quest=df.num_quest[random_index],
                            class_name=channel_name)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=\
        'The Questionator, a lazy way to ask the class a question.')

    parser.add_argument(
      '--chan',
      help="Pick the gStudents slack channel name from which you want to collect user profiles.")

    parser.add_argument(
      '--ping',
      default=False,
      help="Set if the `qbot` should ping the user on Slack when their name comes up.")

    args = parser.parse_known_args()

    # if len(sys.argv) >= 2:
    #     channel_name = sys.argv[1]
    #     if len(sys.argv) == 3:
    #         ping_slack = sys.argv[2]
    #         ping_slack = ping_slack == 'True'
    #     else:
    #         ping_slack = False
    # else:
    #     raise ValueError("Please supply a Slack channel name as an arguement when calling questionator.py!")

    channel_name = args[0].chan
    ping_slack = args[0].ping == 'True'

    api_token = os.environ['SLACK_TOKEN']

    ban = Figlet(font='doh')
    print ban.renderText('Qbot')
    print("*")*50
    print("Initializing Slack API")
    print("*")*50
    slack, students = init_slack_channel(api_token, channel_name)

    print("*")*50
    print("Getting usernames and avatars")
    slack_member_list = slack.users.list().body['members']
    usernames = [id_to_username(slack_member_list, x) for x in students]

    user_map = getUserMap(slack_member_list)

    df = pd.DataFrame()
    df['roster'] = students
    # df['id'] = slack_member_list
    df['username'] = usernames
    df['num_quest'] = [0]*len(students)

    print("*")*50
    print("Starting up Flask app")
    print("*")*50
    app.run(host='0.0.0.0', port=8080, threaded=True)
