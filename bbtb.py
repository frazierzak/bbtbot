while True:
  try:
    #Start
    print "BBTB OTT 0.7 Running"

    #Imports
    import praw
    import arrow
    import re
    import os
    import time
    import traceback
    import urllib2, urllib
    from config_bbtb import *

    #Check for config_bbtb.py
    if not  os.path.isfile("config_bbtb.py"):
      print "You must create a config file with your username and password."
      print "Please see config_skel.py"
      exit(1)

    #Define User_Agent and Bot Name
    user_agent = ("BBTB OTT 0.7 by zuffdaddy")
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

    #Check for current_thread.txt which contains the last current thread id
    print "Checking for current_thread.txt"
    if not os.path.isfile("current_thread.txt"):
      print "Current_thread.txt not found"
      current_thread = ""
    else:
      print "Current_thread.txt found"
      with open("current_thread.txt", "r") as f:
        current_thread = f.read()

    #Declare Variables
    subreddit = r.get_subreddit("bigbrother")
    phrase = "!BBT"
    thread_check_counter = 10

    #Declare Functions
    def RepresentsInt(s):
      #This function checks if the string can be turned into an integer
      try:
        s.isdigit()
        return True
      except ValueError:
        return False

    def convertBBT(comment, comment_body):
      #Convert comment time to BBT
      print "Converting time to BBT"
      comment_time = comment.created_utc
      #Check for characters after phrase for time_shift
      time_shift = re.search('!BBT-(\d+)', comment.body)
      #If time shift detected, subtract from current BBT
      if time_shift and RepresentsInt(time_shift.group(1)):
        shifted_time = comment_time + (-int(time_shift.group(1)) * 60)
        arrow_time = arrow.get(shifted_time)
        comment_body = comment_body.replace("!BBT-" + str(time_shift.group(1)), "")
      else:
        shifted_time = comment_time - 60
        arrow_time = arrow.get(shifted_time)    
        comment_body = comment_body.replace("!BBT", "")
      pst_time = arrow_time.to('US/Pacific')
      pst_time = pst_time.format('h:mma - MMM D')
      return (pst_time, comment_body, shifted_time)

    def convertBBTnormal(comment):
      #Convert comment time to BBT
      print "Converting time to BBT"
      comment_time = comment.created_utc
      #Check for characters after phrase for time_shift
      time_shift = re.search('!BBT-(\d+)', comment.body)
      #If time shift detected, subtract from current BBT
      if time_shift and RepresentsInt(time_shift.group(1)):
        shifted_time = comment_time + (-int(time_shift.group(1)) * 60)
        arrow_time = arrow.get(shifted_time)
      else:
        shifted_time = comment_time - 60
        arrow_time = arrow.get(shifted_time)    
      pst_time = arrow_time.to('US/Pacific')
      pst_time = pst_time.format('h:mma - MMM D')
      return (pst_time)

    def bbvPost(bbv_title, bbv_desc, bbv_time):
      #Post to BBV Bookmarks
      #Hidden

    #Load Comment Stream
    print "Loading comment stream"
    stream = praw.helpers.comment_stream(r, subreddit, limit=1000, verbosity=1)
    while True:
      for comment in stream:
        print "New Comment found\n"

        #Check if replied to already
        print "Checking if replied to"
        if comment.id in comments_replied_to:
          print "Previous replied comment, skipping..."
          continue

        #Setup thread_check_counter to countdown from 5
        thread_check_counter -= 1
        print "Checking for new thead in %d" % thread_check_counter
        if thread_check_counter <= 0:
          print "Checking for new thread"
          thread_check_counter = 10

          #Grab relevant comment data
          if comment.submission is None:
            print "No comment submission found, skipping..."
            print comment.permalink
            break
          comment_sub = comment.submission
          comment_sub_id = comment_sub.id
          comment_sub_title = comment_sub.title
          if comment.submission.author is None or comment.submission.author.name is None:
            print "No submission author name found, skipping..."
            print comment.permalink
            break
          comment_sub_author = comment_sub.author.name
          hot = subreddit.get_hot(limit=2)

          #Check if in current_thread
          if comment_sub_id == current_thread and current_thread != "":
            print "Still the current thread"
          elif comment_sub not in hot:
            print "Not in hot"
          elif "Live Feed Discussion" not in comment_sub_title:
            print "Not a live feed discussion"
          elif "AutoModerator" not in comment_sub_author:
            print "Not made by AutoModerator"
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
            thread_recap = ["###["+ old_title + "](" + old_url + ") Recap\n___\n^**!BBT** ^Get ^the ^current ^house ^time ^minus ^1 ^minute.  \n^**!BBT-#** ^Replace ^**#** ^with ^minutes ^to ^go ^back\n\nTime|Karma|Comment|Link|User\n---|---|---|---|---"]

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
                #If comment deleted, remove from current_thread comments and continue to next
                current_thread_comments.remove(comment_link)
                continue

              #If comment deleted, remove from current_thread comments and continue to next
              if comment.body is None or comment.author is None or comment.author.name is None:
                print "Deleted comment found, removing from list"
                current_thread_comments.remove(comment_link)
                continue

              #If at least 35 rows are made from comments, put them in their own thread_recap.txt to prevent reaching reddit comment limit    
              if row_counter > 29:
                print "30 rows reached"
                
                #Reset the row_counter
                row_counter = 0

                #Write thread_recap to thread_recap_%s_%s.txt
                print "Saving to thread_recap_%s_%s.txt" % (current_thread, post_counter)
                with open("thread_recap_%s_%s.txt" % (current_thread, post_counter), "w") as f:
                  for recap in thread_recap:
                    f.write(recap + "\n")

                #Add one to post_counter
                post_counter += 1

                #Clear thread_recap and add header for comment replies
                thread_recap = ["Time|Karma|Comment|Link|User\n---|---|---|---|---"]        

              #Grab comment's score to filter out good/bad comments
              comment_score = comment.score
              if comment_score > 2:
                row_counter += 1
                print "In %d comments, we'll start a new post" % (30 - row_counter)
                comment_score = "%02d" % (comment_score,)
                comment_body = comment.body
                comment_body = comment_body.replace("\n", " ")
                comment_body = comment_body.replace("\r", " ")
                comment_link = comment.permalink
                comment_link = comment_link.replace("https://www.reddit.com/r/BigBrother", "")
                comment_author = "/u/" + comment.author.name
                pst_time, comment_body, shifted_time = convertBBT(comment, comment_body)
                comment_body = re.sub('\W+', ' ', comment_body)
                comment_body = comment_body.strip()
                if comment_score > 4:
                  bbv_title = comment_body[:100]
                  bbv_desc = comment_body[:300]
                  bbv_time = shifted_time
                  bbvPost(bbv_title, bbv_desc, bbv_time)
                comment_body = (comment_body[:140] + '...|[URL](' + comment_link + ')') if len(comment_body) > 140 else comment_body + '|[URL](' + comment_link + ')'
                thread_recap.append(pst_time + "|" + str(comment_score) + "|" + comment_body + "|" + comment_author)

            if row_counter > 0:
              #Write thread_recap to thread_recap_%s_%s.txt
              print "Saving to thread_recap_%s_%s.txt" % (current_thread, post_counter)
              with open("thread_recap_%s_%s.txt" % (current_thread, post_counter), "w") as f:
                for recap in thread_recap:
                  f.write(recap + "\n")

            #Declare the new thread
            new_thread = comment_sub

            #Get submission and title
            print "Grabbing new submission and title"
            new_title = new_thread.title
            new_url = new_thread.url

            #Post link to new thread
            old_submission.add_comment("New Live Feed Discussion:\n###[%s](%s)\n___\n^**!BBT** ^Get ^the ^current ^house ^time ^minus ^1 ^minute.  \n^**!BBT-#** ^Replace ^**#** ^with ^minutes ^to ^go ^back" % (new_title, new_url))
            
            #Post recap_post
            if os.path.isfile("thread_recap_%s_0.txt" % current_thread):
              with open("thread_recap_%s_0.txt" % current_thread, "r") as f:
                thread_recap = f.read()
              print "\n|------------------------------|\n|---Posting thread_recap.txt---|\n|------------------------------|\n"
              recap_post = new_thread.add_comment(thread_recap)

            #If one or more posts, start making replies
            print "%d extra posts to make" % post_counter
            if post_counter > 0:
              #While there are posts left, keep posting replies
              while post_counter != 0:
                print "%d posts left to make" % post_counter
                if os.path.isfile("thread_recap_%s_%s.txt" % (current_thread, post_counter)):
                  with open("thread_recap_%s_%s.txt" % (current_thread, post_counter), "r") as f:
                    thread_recap = f.read()
                post_counter -= 1
                print "\n|----------------------------------------------|\n|---Posting thread_recap_%d.txt to reply_post---|\n|----------------------------------------------|\n" % post_counter
                reply_post = recap_post.reply(thread_recap)
                recap_post = reply_post

            #Set the new curent thread
            current_thread = comment_sub_id

            #Write current_thread to current_thread.txt
            with open("current_thread.txt", "w") as f:
              f.write(current_thread)

        #Check for phrase
        if comment.body is None:
          print "No comment body found, skipping..."
          print comment.permalink
          continue
        if not re.search(phrase, comment.body):
          print "Phrase not found"
          continue

        #Check if posted by BBTBot
        if comment.author is None or comment.author.name is None:
          print "No comment author found, skipping..."
          print comment.permalink
          continue 
        if "BBTBot" == comment.author.name:
          print "Not replying to BBTBot"
          continue

        #Convert BBT
        print "Converting BBT"
        pst_time = convertBBTnormal(comment)

        #Reply with BBT
        print "\n|-------------------|\n|-Replying with BBT-|\n|-------------------|\n"
        #comment.reply(pst_time + "^**!BBT** ^Get ^the ^current ^house ^time ^minus ^1 ^minute.  \n^**!BBT-#** ^Replace ^**#** ^with ^minutes ^to ^go ^back")
        comment.reply(pst_time)

        #Add to comments_replied_to.txt
        print "Adding to comments_replied_to.txt"
        comments_replied_to.append(comment.id)
        with open("comments_replied_to.txt", "w") as f:
          for comment_id in comments_replied_to:
            f.write(comment_id + "\n")

        comment_sub = comment.submission
        comment_sub_id = comment_sub.id

        #Add to current_thread_comments.txt if in current_thread
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
  except:
    print "\n|---------------|\n|-Error Occured-|\n|---------------|\n"
    traceback.print_exc()
    time.sleep(10)
