# while True:
#   try:
#Start
print "1. BBTBY 0.4 WIP Running..."

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
user_agent = ("BBTB WIP by zuffdaddy 0.4")
r = praw.Reddit(user_agent = user_agent)

#Log In with Bot
print "4. Logging In"
r.login(REDDIT_USERNAME, REDDIT_PASS, disable_warning=True)

#Check for comments_replied_to_test.txt and create variable if it doesn't exist
print "5. Checking for comments_replied_to_test.txt"
if not os.path.isfile("comments_replied_to_test.txt"):
  print "comments_replied_to_test.txt does not exist, creating comments_replied_to variable"
  comments_replied_to = []

#If it does exist, load txt into variable
else:
  print "6. Comments_replied_to_test.txt does not exist, creating..."
  with open("comments_replied_to_test.txt", "r") as f:
    comments_replied_to = f.read()
    comments_replied_to = comments_replied_to.split("\n")
    comments_replied_to = filter(None, comments_replied_to)

#Choose Subreddit
print "7. Choosing Subreddit"
subreddit = r.get_subreddit("bigbrother")

#Create current_feed_thread variable
print "8. Creating blank current_feed_thread and current_thread_comment_ids variables"
current_live_feed = "4rxpw3"
current_live_feed_comments = []

#Load Comment Stream
print "9. Loading comment stream"
stream = praw.helpers.comment_stream(r, subreddit, limit=None, verbosity=1)
while True:
  #Parse Comments in Stream
  print "10. Parsing comments"
  for comment in stream:
    #Search for term in comment
    print "Searching for phrase in comment"
    if re.search("!BBT", comment.body):

      #Check if comment.id is not in comments_replied to
      print "Phrase found, is it a new comment?"
      if comment.id not in comments_replied_to:

        #Make sure we're not replying to ourself
        print "New comment! But are we replying to BBTBot?"
        if "BBTBot" == comment.author.name:
          print "Yep! Moving along..."
        else:
          print "Nope!"

          #If term found, convert comment time to BBT 
          print "Converting comment_time to BBT"
          comment_time = comment.created_utc
          shifted_time = comment_time - 60
          arrow_time = arrow.get(shifted_time)    
          pst_time = arrow_time.to('US/Pacific')
          pst_time = pst_time.format('h:mma - MMM D')

          #Comment Reply with BBT
          print "Replying with BBT"
          #comment.reply(pst_time)

          #Save comment's replied to comments_replied_to_test.txt
          print "Saving comment to comments_replied_to_test.txt"
          comments_replied_to.append(comment.id)
          with open("comments_replied_to_test.txt", "w") as f:
            for comment_id in comments_replied_to:
              f.write(comment_id + "\n")

          #Get submission and title
          print "Grabbing submission and title"
          submission = comment.submission
          title = submission.title
          print "Comment belongs to: %s" % title

          #Get submitter
          print "Grabbing submission author"
          author = submission.author.name
          print "Author is %s" % author

          #Check if live feed and submitter is AutoModerator
          print "Checking if submission is a live feed and posted by automoderator"
          if "Live Feed Discussion" in title and "AutoModerator" in author: 
            #Check if current_live_feed equals submission.id and comment.id is not in current_live_feed_comments
            print "It's a live feed! Checking if its the CURRENT live feed and hasn't been seen before"
            if current_live_feed == submission.id and comment.permalink not in current_live_feed_comments:

              #Check for comments_replied_to.txt and create if it doesn't exist
              print "current_live_feed_comments_%s_test.txt does not exist!" % submission.id
              if not os.path.isfile("current_live_feed_comments_%s_test.txt" % submission.id):
                  current_live_feed_comments = []

              #Save comment id to current_thread_comment_ids.txt
              print "It's the current live feed and an unseen comment. Saving comment id and writing it to txt file"
              current_live_feed_comments.append(comment.permalink)
              with open("current_live_feed_comments_%s_test.txt" % submission.id, "w") as f:
                for comment_permalink in current_live_feed_comments:
                  f.write(comment_permalink + "\n")

            #If its not the current live feed and the comment has not been seen before
            elif comment.permalink not in current_live_feed_comments:
              print "Not current live feed and unseen comment"
              
              #Get top 2 hot threads
              print "Getting Hot 2 submissions"
              hot = subreddit.get_hot(limit=2)

              #Check if submission is in hot
              print "Checking if submission is in hot"
              if submission in hot:
                print "Submission in hot. This is the new live feed."

                #Begin gathering up previous live feed comments and prepping them to post
                print "Gathering current_live_feed_comments"
                #Check for comments_replied_to.txt and create if it doesn't exist
                if not os.path.isfile("current_live_feed_comments_%s_test.txt" % submission.id):
                    print "current_live_feed_comments_%s_test.txt does not exist!" % submission.id
                    current_live_feed_comments = []
                else:
                  print "current_live_feed_comments_%s_test.txt exist!" % submission.id
                  with open("current_live_feed_comments_%s_test.txt" % submission.id, "r") as f:
                    current_live_feed_comments = f.read()
                    current_live_feed_comments = current_live_feed_comments.split("\n")
                    current_live_feed_comments = filter(None, current_live_feed_comments)

                #Get submission and title
                print "Grabbing submission and title"
                old_submission = r.get_submission(submission_id=current_live_feed)
                old_title = old_submission.title
                print old_title
                old_url = old_submission.url
                print old_url

                #Start loop for each comment_permalink in current_live_feed_comments
                for comment_permalink in current_live_feed_comments:

                  #Grab comment object from id and put it into old_comment variable
                  old_comment = r.get_submission(comment_permalink).comments[0]
                  print "old_comment is %s" % old_comment
                  
                  #Make sure comment score is equal or greater than 3
                  print "Check if comment score is equal or greater than 3"
                  score = old_comment.score
                  print "Comment Karma is %d" % score
                  if score >= 3:

                    #Create worthy_comments.txt if it doesnt exist
                    print "Comment score equal or greater than 3, checking if worthy_comments.txt exist"
                    if not os.path.isfile("worthy_comments_%s_test.txt" % old_submission.id):
                      print "worthy_comments.txt does not exist, creating worthy_comments variable"
                      worthy_comments = ["###["+ old_title + "](" + old_url + ")" + "  \n  \n/u/BBTBot's Live Feed Summary. *Here I go summarizing again!* Add **!BBT** to your posts to get a timestamp and help make the summary  \n  \n" + "Time | Karma | Comment | User\n---|---|---|---"]  
                    else:
                      # Read the file into a list and remove any empty values
                      with open("worthy_comments_%s_test.txt" % old_submission.id, "r") as f:
                        worthy_comments = f.read()
                        worthy_comments = worthy_comments.split("\n")
                        worthy_comments = filter(None, worthy_comments)          

                    #Convert comment time to BBT
                    print "Converting time to BBT"
                    comment_time = old_comment.created_utc
                    shifted_time = comment_time - 60
                    arrow_time = arrow.get(shifted_time)    
                    pst_time = arrow_time.to('US/Pacific')
                    pst_time = pst_time.format('h:mma - MMM D')

                    #Grab comment author username, body, permalink
                    print "Grabbing username, body, and permalink to comment"
                    author = old_comment.author
                    username = "/u/" + author.name
                    body = old_comment.body
                    body = body.strip("[]()~*#_|-")
                    body = body.replace("\n", "  ")
                    permalink = comment_permalink

                    #Add comment content to worthy_comments.txt
                    print "Add worthy_comment to worthy_comments.txt"
                    worthy_comments.append("[" + pst_time + "](" + permalink + ")" + " | " + str(score) + " pts | " + body + " | " + username + "\n")
                    with open("worthy_comments_%s_test.txt" % old_submission.id, "w") as f:
                      for worthy_comment in worthy_comments:
                        f.write(worthy_comment + "\n")

                  else:
                    print "Score too low"

                #Post worthy_comments.txt to old thread
                print "Posting worthy_comments.txt to old thread"

                #Delete worthy_comments.txt
                print "Deleting worthy_comments.txt"
                #os.remove("worth_comments_%s_test.txt" % current_live_feed)

                #Delete current_thread_comment_ids.txt
                print "Deleting current_thread_comment_ids.txt"
                #os.remove("current_live_feed_comments_%s_test.txt" % current_live_feed)

                #Set current feed to comment's thread
                print "Setting current_live_feed to submission.id"
                current_live_feed = submission.id

                print "Done! Starting over with new current_live_feed"

              else:
                print "Submission not in hot"

            else:
              print "Old live feed or old comment"

          else:
            print "Not live feed or posted by automoderator"

      else:
        print "Old Comment!"

    else:
      print "Phrase not found"

  # except:
  #   print 'Error! Restarting the script'
  #   time.sleep(5)
