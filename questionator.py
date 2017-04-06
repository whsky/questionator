#############################################################################
# Steve Iannaccone
# March 2017
#
# Flask app for running NCAA March Madness predictions
#############################################################################
from flask import Flask, request, url_for, render_template, request
import cPickle as pickle
import numpy as np
from random import randrange

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/question', methods=['POST'])
def pnt_predicter():
    random_index = randrange(0,len(roster))

    avatar_link = avatar[random_index]
    member_name = roster[random_index]

    return render_template('question.html',
                            avatar=avatar_link,
                            name=member_name)



if __name__ == '__main__':
    roster = pickle.load(open('data/roster', 'rb'))
    avatar = pickle.load(open('data/avatar', 'rb'))
    app.run(host='0.0.0.0', port=8080, threaded=True)
