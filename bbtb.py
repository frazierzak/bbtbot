#Start
print "BBTB 0.7 Running"

#Imports
import praw
import arrow
import re
import os
from config_bbtb import *

#Check for config_bbtb.py
if not  os.path.isfile("config_bbtb.py"):
  print "You must create a config file with your username and password."
  print "Please see config_skel.py"
  exit(1)

#Define User_Agent and Bot Name
user_agent = ("BBTB 0.7 by zuffdaddy")
r = praw.Reddit(user_agent = user_agent)

#Log In with Bot
r.login(REDDIT_USERNAME, REDDIT_PASS, disable_warning=True)

#Check for comments_replied_to.txt
print "Checking for comments_replied_to.txt"
if not os.path.isfile("comments_replied_to.txt"):
  print "comments_replied_to.txt not found"
  comments_replied_to = []
else:
  with open("comments_replied_to.txt", "r") as f:
    print "comments_replied_to.txt found"
    comments_replied_to = f.read()
    comments_replied_to = comments_replied_to.split("\n")
    comments_replied_to = filter(None, comments_replied_to)

#Check for current_thread.txt
print "Checking for current_thread.txt"
if not os.path.isfile("current_thread.txt"):
  print "current_thread.txt not found"
  current_thread = ""
else:
  print "current_thread.txt found"
  with open("current_thread.txt", "r") as f:
    current_thread = f.read()

#Declare Variables and Functions
subreddit = r.get_subreddit("bigbrother")
phrase = "!BBT"
thread_check_counter = 5
def RepresentsInt(s):
  try:
    s.isdigit()
    return True
  except ValueError:
    return False
def convertBBT(comment):
  #Convert comment time to BBT
  print "Converting time to BBT"
  comment_time = comment.created_utc
  time_shift = re.search('!BBT-(\d+)', comment.body)
  if time_shift and RepresentsInt(time_shift.group(1)):
    print "time shift!"
    print "shift request is %d minutes" % -int(time_shift.group(1))
    shifted_time = comment_time + (-int(time_shift.group(1)) * 60)
    print "shifted time is %d seconds" % shifted_time
    arrow_time = arrow.get(shifted_time)
  else:
    print "no time shift"
    arrow_time = arrow.get(comment_time)  
  #arrow_time = arrow.get(comment_time) 
  pst_time = arrow_time.to('US/Pacific')
  pst_time = pst_time.format('h:mma - MMM D')
  return pst_time

#Load Comment Stream
print "Loading comment stream"
stream = praw.helpers.comment_stream(r, subreddit, limit=30, verbosity=1)
while True:
  for comment in stream:

    if comment.body == "NoneType" or comment.author == "NoneType":
      print "Deleted comment, skipping..."
      break

    print "Checking if replied to"
    if comment.id in comments_replied_to:
      print "Previous replied comment, skipping..."
      break

    #Setup thread_check_counter to countdown from 5
    thread_check_counter -= 1
    print "Checking for new thead in %d" % thread_check_counter
    if thread_check_counter <= 0:
      print "Checking for new thread"
      thread_check_counter = 5

      comment_sub = comment.submission
      comment_sub_id = comment_sub.id
      comment_sub_title = comment_sub.title
      comment_sub_author = comment_sub.author.name
      hot = subreddit.get_hot(limit=2)

      #Check if in current_thread
      if comment_sub_id == current_thread and current_thread != "":
        print "Still the current thread"
      elif comment_sub not in hot:
        print "Not in hot"
      elif "Live Feed Discussion" not in comment_sub_title or "AutoModerator" not in comment_sub_author:
        print "Not a live feed discussion or made by AutoModerator"
      elif not os.path.isfile("current_thread_comments_%s.txt" % current_thread) or current_thread == "":
        print "current_thread_comments_%s.txt not found, making this the current thread" % current_thread
        current_thread_comments = []
        current_thread = comment_sub_id
        with open("current_thread.txt", "w") as f:
          f.write(current_thread)
      else:
        print "New current thread detected, posting recap..."
        with open("current_thread_comments_%s.txt" % current_thread, "r") as f:
          current_thread_comments = f.read()
          current_thread_comments = current_thread_comments.split("\n")
          current_thread_comments = filter(None, current_thread_comments)

        #Get old current_thread and submission.title
        old_submission = r.get_submission(submission_id=current_thread)
        old_title = old_submission.title
        old_url = old_submission.short_link

        #Add meta header to top of thread_recap
        thread_recap = ["###["+ old_title + "](" + old_url + ")" + "  \n  \n/u/BBTBot's Live Feed Summary. Add **!BBT** to your posts to help make the summary!  \n  \n" + "Time|Karma|Comment|Link|User\n---|---|---|---|---"]

        #Create row_counter and post_counter variable that will count how many posts are added to the recap
        row_counter = 0
        post_counter = 0

        #Start loop for each comment_link in current_thread_comments
        print "Parsing current_thread_comments"
        for comment_link in current_thread_comments:

          #Get comment from comment_link
          try:
              comment = r.get_submission(comment_link).comments[0]
          except IndexError:
              current_thread_comments.remove(comment_link)
              continue

          #If comment is deleted, remove from current_thread_comments
          if comment.body == None or comment.author == None or comment.author.name == None:
            print "Deleted comment found, removing from list"
            current_thread_comments.remove(comment_link)
            continue

          #If at least 35 rows are made from comments, put them in their own thread_recap.txt to prevent reaching reddit comment limit    
          if row_counter > 34:
            print "35 rows reached"
            
            row_counter = 0

            #Write thread_recap to thread_recap_%s_%s.txt
            print "Saving to thread_recap_%s_%s.txt" % (current_thread, post_counter)
            with open("thread_recap_%s_%s.txt" % (current_thread, post_counter), "w") as f:
              for recap in thread_recap:
                f.write(recap + "\n")

            post_counter += 1

            #Clear thread_recap and add header for comment replies
            thread_recap = ["Time|Karma|Comment|Link|User\n---|---|---|---|---"]        

          #Grab comment's score to filter out good/bad comments
          comment_score = comment.score
          if comment_score >= 1:
            row_counter += 1
            print "In %d comments, we'll start a new post" % (35 - row_counter)
            comment_score = "%02d" % (comment_score,)
            comment_body = comment.body
            comment_body = comment_body.replace("~*#_|-", "")
            comment_body = comment_body.replace("\n", " ")
            comment_body = comment_body.strip()
            comment_link = comment.permalink
            comment_link = comment_link.replace("https://www.reddit.com/r/BigBrother", "")
            comment_body = (comment_body[:75] + '...|[URL](' + comment_link + ')') if len(comment_body) > 75 else comment_body + '|[URL](' + comment_link + ')'
            comment_author = "/u/" + comment.author.name
            pst_time = convertBBT(comment)
            thread_recap.append(pst_time + "|" + str(comment_score) + "|" + comment_body + "|" + comment_author)

        #Write thread_recap to thread_recap_%s_%s.txt
        print "Saving to thread_recap_%s_%s.txt" % (current_thread, post_counter)
        with open("thread_recap_%s_%s.txt" % (current_thread, post_counter), "w") as f:
          for recap in thread_recap:
            f.write(recap + "\n")

        new_thread = comment_sub
        
        #Post recap_post
        if os.path.isfile("thread_recap_%s_0.txt" % current_thread):
          with open("thread_recap_%s_0.txt" % current_thread, "r") as f:
            thread_recap = f.read()
          print "\n|---Posting thread_recap_%s_0.txt---|\n" % current_thread
          recap_post = new_thread.add_comment(thread_recap)

        #If one or more posts, start making replies
        if post_counter > 0:
          while post_counter != 0:
            if os.path.isfile("thread_recap_%s_%s.txt" % (current_thread, post_counter)):
              with open("thread_recap_%s_%s.txt" % (current_thread, post_counter), "r") as f:
                thread_recap = f.read()
            post_counter -= 1
            print "\n|---Posting reply_post = recap_post.add_comment(%s)---|\n" %  thread_recap
            reply_post = recap_post.add_comment(thread_recap)
            recap_post = reply_post

        current_thread = comment_sub_id

        #Write current_thread to current_thread.txt
        with open("current_thread.txt", "w") as f:
          f.write(current_thread)

    if not re.search(phrase, comment.body):
      print "Phrase not found"
      break

    if "BBTBot" == comment.author.name:
      print "Not replying to BBTBot"
      break

    print "Converting BBT"
    pst_time = convertBBT(comment)

    print "Replying with BBT"
    comment.reply(pst_time)

    print "Adding to comments_replied_to.txt"
    comments_replied_to.append(comment.id)
    with open("comments_replied_to.txt", "w") as f:
      for comment_id in comments_replied_to:
        f.write(comment_id + "\n")

    comment_sub = comment.submission
    comment_sub_id = comment_sub.id

    if comment_sub_id == current_thread:
      print "Adding to current_thread_comments_%s.txt" % current_thread
      if not os.path.isfile("current_thread_comments_%s.txt" % current_thread):
        current_thread_comments = []
      else:
        with open("current_thread_comments_%s.txt" % current_thread, "r") as f:
          current_thread_comments = f.read()
          current_thread_comments = current_thread_comments.split("\n")
          current_thread_comments = filter(None, current_thread_comments)

      current_thread_comments.append(comment.permalink)

      with open("current_thread_comments_%s.txt" % current_thread, "w") as f:
        for comment_link in current_thread_comments:
          f.write(comment_link + "\n")
