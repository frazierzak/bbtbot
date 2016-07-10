# while True:
#   try:
#Start
print "1. BBTBY 0.5 Running..."

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
print "2. Checking for config_bot.py..."
if not  os.path.isfile("config_bot.py"):
  print "You must create a config file with your username and password."
  print "Please see config_skel.py"
  exit(1)

#Define User_Agent and Bot Name
print "3. Creating Agent"
user_agent = ("BBTB WIP by zuffdaddy 0.5")
r = praw.Reddit(user_agent = user_agent)

#Log In with Bot
print "4. Logging In"
r.login(REDDIT_USERNAME, REDDIT_PASS, disable_warning=True)

#Check for comments_replied_to.txt and create variable if it doesn't exist
print "5. Checking for comments_replied_to.txt"
if not os.path.isfile("comments_replied_to.txt"):
  print "comments_replied_to.txt does not exist, creating comments_replied_to variable"
  comments_replied_to = []

#If it does exist, load txt into variable
else:
  print "6. Comments_replied_to.txt does not exist, creating..."
  with open("comments_replied_to.txt", "r") as f:
    comments_replied_to = f.read()
    comments_replied_to = comments_replied_to.split("\n")
    comments_replied_to = filter(None, comments_replied_to)

#Choose Subreddit
print "7. Choosing Subreddit"
subreddit = r.get_subreddit("bigbrother")

#Create current_feed_thread variable
print "8. Creating blank current_thread variable"
current_thread = ""

#Set search phrase
phrase = "!BBT"

#Load Comment Stream
print "9. Loading comment stream"
stream = praw.helpers.comment_stream(r, subreddit, limit=None, verbosity=1)
while True:
  #Parse Comments in Stream
  #print "10. Parsing comments"
  for comment in stream:

    #Search for term in comment
    #print "Searching for phrase in comment"
    if not re.search(phrase, comment.body):
      #print "No Phrase Found..."
      break

    #Check if comment.id is not in comments_replied to
    print "Phrase found, is it a new comment?"
    if comment.id in comments_replied_to:
      print "Old Comment..."
      break

    #Make sure we're not replying to ourself
    print "New comment! But are we replying to BBTBot?"
    if "BBTBot" == comment.author.name:
      print "Yep! Moving along..."
      break

    #Convert comment time to BBT 
    print "Converting comment_time to BBT"
    comment_time = comment.created_utc
    shifted_time = comment_time - 60
    arrow_time = arrow.get(shifted_time)    
    pst_time = arrow_time.to('US/Pacific')
    pst_time = pst_time.format('h:mma - MMM D')

    #Reply to comment with BBT
    print "Replying with BBT"
    comment.reply(pst_time)

    #Save comment's replied to comments_replied_to.txt
    print "Saving comment to comments_replied_to.txt"
    comments_replied_to.append(comment.id)
    with open("comments_replied_to.txt", "w") as f:
      for comment_id in comments_replied_to:
        f.write(comment_id + "\n")

    #Get submission title and author
    print "Grab submission title and author"
    comment_sub = comment.submission
    sub_title = comment_sub.title
    sub_author = comment_sub.author.name
    print "Comment belongs to: \n%s \nCreated by %s" % (sub_title, sub_author)

    # Check if live feed and submitter is AutoModerator
    print "Checking if submission is a live feed and posted by automoderator"
    if "Live Feed Discussion" not in sub_title or "AutoModerator" not in sub_author:
      print "Not a live feed thread"
      break

    #Grab comment's submission id
    print "Grab comment's sub_id"
    sub_id = comment_sub.id

    #Grab comment permalink and append it to current_thread_comments
    print "Grab comment's permalink"
    comment_link = comment.permalink
  
    #Check if it's the current live feed
    print "Check if its the current feed"
    if sub_id == current_thread:

      print "This is the current feed"

      #Make sure current_thread_comments.txt exist
      print "Check if current_thread_comments.txt exist"
      if not os.path.isfile("current_thread_comments_%s.txt" % sub_id):
        print "Can't find current_thread_comments.txt"
        current_thread_comments = []

      else:
        print "Found current_thread_comments.txt"
        with open("current_thread_comments_%s.txt" % sub_id, "r") as f:
          current_thread_comments = f.read()
          current_thread_comments = current_thread_comments.split("\n")
          current_thread_comments = filter(None, current_thread_comments)

      print "Appending to current_thread_comments"
      current_thread_comments.append(comment_link)

      print "Writing to current_thread_comments.txt"
      #Save new comment to current_thread_comments
      with open("current_thread_comments_%s.txt" % sub_id, "w") as f:
        for comment_link in current_thread_comments:
          f.write(comment_link + "\n")
    
    #If this comment's thread is NOT the current feed
    else:
      print "This is NOT the current feed"

      #Grab hot subreddits
      print "Getting hot subreddits"      
      hot = subreddit.get_hot(limit=2)

      print "Checking if submission is in hot"
      #If comment_sub is in hot
      if comment_sub in hot:
        print "Submission in hot, new live feed detected"

        #Check if current_thread_comments exists
        if not os.path.isfile("current_thread_comments_%s.txt" % current_thread):

          #Current_thread_comments does not exist, creating variable
          print "Can't find current_thread_comments.txt"
          current_thread_comments = []

          #Adding comment to current_thread_comments variable
          print "Appending to current_thread_comments"
          current_thread_comments.append(comment_link)

          #Saving current_thread_comments.txt
          print "Writing to current_thread_comments.txt"
          with open("current_thread_comments_%s.txt" % sub_id, "w") as f:
            for comment_link in current_thread_comments:
              f.write(comment_link + "\n")

          #Assign new sub_id to current_thread
          print "Making new submission the current thread"
          current_thread = sub_id

        #If Current_thread_comments.txt exists
        else:
          print "Found current_thread_comments.txt"

          #Get submission and title
          print "Grabbing old submission and title"
          old_submission = r.get_submission(submission_id=current_thread)
          old_title = old_submission.title
          print "Old title:\n%s" % old_title
          old_url = old_submission.url
          print "Old url:\n%s" % old_url

          #Load current_thread_comments.txt
          with open("current_thread_comments_%s.txt" % current_thread, "r") as f:
            current_thread_comments = f.read()
            current_thread_comments = current_thread_comments.split("\n")
            current_thread_comments = filter(None, current_thread_comments)

          #Create thread_recap.txt
          if not os.path.isfile("thread_recap_%s.txt" % current_thread):
            print "Can't find thread_recap.txt"
          else:
            print "Removing previous thread_recap.txt"
            os.remove("thread_recap_%s.txt" % current_thread)

          #Add meta data to top of thread_recap
          print "Adding meta data to the top of thread_recap"
          thread_recap = ["###["+ old_title + "](" + old_url + ")" + "  \n  \n/u/BBTBot's Live Feed Summary. Add **!BBT** to your posts to help make the summary!  \n  \n" + "Time | Karma | Comment | User\n---|---|---|---"]

          print "Begin parsing current_thread_comments"
          #Start loop for each comment_link in current_thread_comments
          for comment_link in current_thread_comments:

            print "Getting comment data from comment_link"
            comment = r.get_submission(comment_link).comments[0]

            print "Getting comment_score"
            comment_score = comment.score

            print "Checking if comment_score is greater than or equal to 5"
            if comment_score >= 5:
              print "Score is greater than or equal to 5"

              print "Converting score to have leading 0"
              comment_score = "%02d" % (comment_score,)

              print "Getting comment body"
              comment_body = comment.body

              comment_body = comment_body.strip("~*#_|-")
              comment_body = comment_body.replace("\n", "  ")
              comment_body = comment_body.replace(phrase, "")

              print "Truncating body to 75 characters and add link at end"
              #comment_body = (comment_body[:75] + '[...](' + comment_link + ')') if len(comment_body) > 75 else comment_body + ' [link](' + comment_link + ')'
              comment_body = (comment_body[:75] + '...') if len(comment_body) > 75 else comment_body

              print "Getting comment author"
              comment_author = "/u/" + comment.author.name

              #Convert comment time to BBT
              print "Converting time to BBT"
              comment_time = comment.created_utc
              shifted_time = comment_time - 60
              arrow_time = arrow.get(shifted_time)    
              pst_time = arrow_time.to('US/Pacific')
              pst_time = pst_time.format('h:mma - MMM D')

              #Add comment to thread_recap.txt
              print "Add comment to thread_recap.txt"
              thread_recap.append(pst_time + " | " + str(comment_score) + " | " + comment_body + " | " + comment_author)
            else:
              print "Score is too low, skipping"
              pass

          print "Adding saved comments to thread_recap.txt"    
          with open("thread_recap_%s.txt" % current_thread, "w") as f:
            for comment in thread_recap:
              f.write(comment + "\n")

          with open("thread_recap_%s.txt" % current_thread, 'r') as f:
            thread_recap=f.read()

          #Assign new sub_id to current_thread
          current_thread = sub_id

          #Post thread_recap.txt to new thread
          print "Making new submission the current thread"
          new_thread = r.get_submission(submission_id=current_thread)
          new_thread.add_comment(thread_recap)

          #Get submission and title
          print "Grabbing new submission and title"
          new_title = new_thread.title
          new_url = new_thread.url

          #Post link to new thread
          old_submission.add_comment("Found New Live Feed Discussion:  \n###[%s](%s)" % (new_title, new_url))

          #Make sure current_thread_comments.txt exist
          print "Check if current_thread_comments.txt exist"
          if not os.path.isfile("current_thread_comments_%s.txt" % sub_id):
            print "Can't find current_thread_comments.txt"
            current_thread_comments = []

          else:
            print "Found current_thread_comments.txt"
            with open("current_thread_comments_%s.txt" % sub_id, "r") as f:
              current_thread_comments = f.read()
              current_thread_comments = current_thread_comments.split("\n")
              current_thread_comments = filter(None, current_thread_comments)

          print "Appending to current_thread_comments"
          current_thread_comments.append(comment_link)

          print "Writing to current_thread_comments.txt"
          #Save new comment to current_thread_comments
          with open("current_thread_comments_%s.txt" % sub_id, "w") as f:
            for comment_link in current_thread_comments:
              f.write(comment_link + "\n")

  # except:
  #   print 'Error! Restarting the script'
  #   time.sleep(5)
