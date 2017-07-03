![Header Image](https://github.com/whsky/questionator/blob/master/readme_images/QuestionatorHeader.png?raw=true "Header Image")

# The Questionator

## The lazy way to ask a random student a question

The Questionator is a Flask based web app that automatically collects student
names and profile pictures from the Slack channel used for class.

It filters out any member with an `@galvanize.com` email address so you won't
ask any support staff or instructors who are also on the channel questions.

Because this interacts with Slack's API, you will need an API token. You can get
an API key [here](https://api.slack.com/tokens). Set this key to a local
environment alias in your `.bash_profile`, `.bashrc`, or `.zshrc` resource
file. Use the alias name `SLACK_TOKEN` so the python script will pull it in
automatically when launched.

For example:
```bash
export SLACK_TOKEN="your token string here..."
```
Don't forget that you have to re-source you bash profile after editing it...

```bash
$ source ~/.bash_profile
```

API calls are made through python using the [Slacker package](https://github.com/os/slacker). You will need to install this before you run the script.

```bash
$ pip install slacker
```

You will also have to specify what channel your class is using. You can do this
by using a system argument when you call the script.

You can also specify whether our not you want the Questionator to send a
Slack message to the user selected with the `qbot` Slack app built into the
Questionator. This is set with `True` or `False` as the `--ping` system argument.

An example run code looks like this:
```bash
$ python questionator.py --chan='channel_name' --ping=False
```

This would collect student names, Slack usernames, and profile pics for members
in the 'channel_name' channel, and would not send messages to the channel when
a student is called on.

The script takes about 20 seconds to initialize with all the necessary info
from the Slack API. After which, it will launch the Flask App
_(running on port 8080)_.

## What It Does
After collecting all the class members, it initializes the number of questions
asked to zero for everyone. When you press the button `Ask a question` it gets
the list of students who have answered the fewest questions _(initially, this
will be everyone since they have all answered zero questions)_. It then makes a
random selection from this list of whom to ask the question. The username and
profile pic for that student are collected and displayed on screen. That student
then has their "number of questions asked" incremented by one. This helps track
how many questions have been asked, as well as remove the possibility of asking
the same student two or more consecutive questions.
