#############################################################################
# Steve Iannaccone
# March 2017
#
# Flask app for running NCAA March Madness predictions
#############################################################################
from flask import Flask, request, url_for, render_template, request
import cPickle as pickle
import numpy as np
import pandas as pd
from random import randrange, sample, choice

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/question', methods=['POST'])
def pnt_predicter():
    df_min = df[df.num_quest == min(df.num_quest)]
    stud_min = df_min.index.values.tolist()
    #times_asked = df.num_quest[sub_pop]
    random_index = choice(stud_min)

    avatar_link = avatar[random_index]
    member_name = roster[random_index]

    df.num_quest[random_index] += 1

    return render_template('question.html',
                            avatar=avatar_link,
                            name=member_name,
                            quest=df.num_quest[random_index])



if __name__ == '__main__':
    roster = pickle.load(open('data/roster', 'rb'))
    avatar = pickle.load(open('data/avatar', 'rb'))
    df = pd.DataFrame()
    df['roster'] = roster
    df['avatar'] = avatar
    df['num_quest'] = [0]*len(roster)
    app.run(host='0.0.0.0', port=8080, threaded=True)


#create a file tracking the number of times a student has popped up on
# Questionator so we can weight a distribution to make them less likely
# to be called on next time.

#with open('filename', 'w'):
#   num_questions_answ[random_index] += 1
