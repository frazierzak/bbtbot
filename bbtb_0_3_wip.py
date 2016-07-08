# while True:
#   try:
#Start
print "BBTBY 0.3 WIP Running..."

#Imports
import praw
import time
import datetime
import arrow
import pdb
import re
import os
from config_bot import *

#Check for config_bot.py
print "Checking for config_bot.py..."
if not  os.path.isfile("config_bot.py"):
  print "You must create a config file with your username and password."
  print "Please see config_skel.py"
  exit(1)

#Define User_Agent and Bot Name
user_agent = ("BBTB WIP by zuffdaddy 0.3")
r = praw.Reddit(user_agent = user_agent)

#Log In with Bot
print "Logging in..."
r.login(REDDIT_USERNAME, REDDIT_PASS, disable_warning=True)

#Check for comments_replied_to_test.txt and create if it doesn't exist
if not os.path.isfile("comments_replied_to_test.txt"):
    comments_replied_to = []

# If we have run the code before, load the list of comments we have replied to
else:
  # Read the file into a list and remove any empty values
  with open("comments_replied_to_test.txt", "r") as f:
    comments_replied_to = f.read()
    comments_replied_to = comments_replied_to.split("\n")
    comments_replied_to = filter(None, comments_replied_to)

if not os.path.isfile("comments_saved_test.txt"):
    comments_saved = []
else:
  # Read the file into a list and remove any empty values
  with open("comments_saved_test.txt", "r") as f:
    comments_saved = f.read()
    comments_saved = comments_saved.split("\n")
    comments_saved = filter(None, comments_saved)

#Choose Subreddit
subreddit = r.get_subreddit("bigbrother")
print "Loading Subreddit", subreddit

stream = praw.helpers.comment_stream(r, subreddit, limit=100, verbosity=1)
print stream
for comment in stream:
  if re.search("Frank", comment.body) and comment.id not in comments_replied_to:
    print '******* !BBT found in comment id: %s *******' % comment.id

    #Time Conversion
    print 'Converting to BBT'
    comment_time = comment.created_utc
    shifted_time = comment_time - 60
    arrow_time = arrow.get(shifted_time)    
    pst_time = arrow_time.to('US/Pacific')
    pst_time = pst_time.format('h:mma - MMM D') 

    #Comment Reply
    print 'Replying with BBT: %s' % pst_time
    #comment.reply(pst_time) #reply to comment
    print 'Reply Successful'
    
    #Save comment ID
    comments_replied_to.append(comment.id)
    with open("comments_replied_to_test.txt", "w") as f:
      for comment_id in comments_replied_to:
        f.write(comment_id + "\n")
    print "Comment id %s saved to prevent repeat replies" % comment.id
    
    #Grab comment content
    author = comment.author
    username = "/u/" + author.name
    score = '%s points' % comment.score
    body = comment.body

    #Save BBT, comment score, body, and author for future use
    comments_saved.append(pst_time + " | " + score + "  \n" + body + "  \n" + username + "  ")
    with open("comments_saved_test.txt", "w") as f:
      for comment_content in comments_saved:
        f.write(comment_content + "\n\n")

  # except:
  #   print 'Error! Restarting the script'
  #   time.sleep(30)