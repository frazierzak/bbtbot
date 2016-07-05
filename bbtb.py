while True:
  try:
    #Start
    print "BBTBY 0.1 Test Running..."

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
    user_agent = ("BBTB Test by zuffdaddy 0.1")
    r = praw.Reddit(user_agent = user_agent)

    #Log In with Bot
    print "Logging in..."
    r.login(REDDIT_USERNAME, REDDIT_PASS, disable_warning=True)

    #Check for comments_replied_to.txt and create if it doesn't exist
    if not os.path.isfile("comments_replied_to.txt"):
        comments_replied_to = []

    # If we have run the code before, load the list of comments we have replied to
    else:
      # Read the file into a list and remove any empty values
      with open("comments_replied_to.txt", "r") as f:
        comments_replied_to = f.read()
        comments_replied_to = comments_replied_to.split("\n")
        comments_replied_to = filter(None, comments_replied_to)

    #Choose Subreddit
    subreddit = r.get_subreddit("bigbrother")
    print "Loading Subreddit", subreddit

    #Get Top 2 Submissions
    print "Finding top 2 submissions in", subreddit
    for submission in subreddit.get_hot(limit = 2):
      title = submission.title
      title_list = re.sub("[^\w]", " ",  title).split()
      print "Making sure %s is a live feed thread" % title
      if "Feed" in title_list:
        print "It's a live feed thread!"
        submission.replace_more_comments(limit=None, threshold=0)
        all_comments = praw.helpers.flatten_tree(submission.comments)
        all_comments.sort(key=lambda x:x.created_utc, reverse=True)
        latest_hundred = all_comments[:200]
        for comment in latest_hundred:
          if re.search("!BBT", comment.body) and comment.id not in comments_replied_to:
            print '*******!BBT found in comment id:*******', comment.link_id
            comment_time = comment.created_utc
            arrow_time = arrow.get(comment_time)
            print 'Converting to BBT'
            pst_time = arrow_time.to('US/Pacific')
            pst_time = pst_time.format('h:mma - MMM D')            
            print 'Replying with BBT'
            comment.reply(pst_time) #reply to comment
            comments_replied_to.append(comment.id) #add comment link id to comments replied to
      else:
        print "Not a live feed thread!"
        pass

    # Write our updated list back to the file
    with open("comments_replied_to.txt", "w") as f:
      for comment_id in comments_replied_to:
        f.write(comment_id + "\n")
    print 'Done! Waiting for half a minute before I go postin again!'
  except:
    print 'Error! Restarting the script'
  time.sleep(30)
