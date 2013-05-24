filtr
=====

Filtr, final Hackbright project

Overview
--------
Filtr is a 'Pandora'-style web app for news selection. Written in Python, this project
implements a Naive Bayes Classifier optimized with the Fisher method to classify user 
preferences and prediction. News articles are currently sourced from NPR and BBC World 
New RSS feeds. Flask, SQLAlchemy, SQLite, PyRes, FlatUI and JavaScript are utilized.

Classifier (classify/classifying.py)
-------------------------------------
The Classifier trains the database with user preferences, as well as classifying the
probability that a user will like a new article. I wrote an implementation of the
Naive Bayes Classifier, gathering each 'significant' word from the rated article and
classifying it as a 'yes' or 'no' preference. I chose to normalize the NBC by
implementing the fisher method and considering a normalization under a given category.
Article text is fetched by using the urllib2 library, while a version of the original 
Readability code (Decruft) and PyQuery are used to scrape and parse.
I implemented the use of PyRes (a python clone of Resque) to manage asynchronous 
job queues (specifically classifying user preferences). 

Cron Jobs (clock.py)
---------------------
I used APScheduler to handle my cron scheduling to load designated RSS feeds (with 
the feedparser library) and to execute classification scripts for each user.

DB Model (model.py)
-------------------
Using SQLAlchemy, this model sets up database schema for the app. At this stage, all
user, article, and classification information is stored in a database. You can see 
the setup for classification with the tables CC (category count) and FC (feature count),
lines 77-91.

Web App (views.py)
------------------
This module handles web requests with python's Flask framework. Allows for
multiple user accounts, initiates a selection seed upon user signup in order to
begin a training corpus. Users recieve the most current news rated highly for them
and the ability to say 'yes' or 'no' to each article they see. 

Front End (static and templates folders)
----------------------------------------
Flask templates for page views
JQuery
FlatUI + some custom CSS
animate-custom.css for sliding animations


Future work
------------
While the project is in a demo-ready state, there's a lot of work to be done! 
Next steps will include making it faster over-all. This will mean playing with 
memcache to speed up database retreival (which currently is the slowest piece
of this application). 
Other goals/ideas:
  - tinker with a different algorithm that is more lightweight. Since this
    project was designed as a learning tool, it would be in the spirit of
    the project to see how using different feature selection or algorithm
    (such as a clustering algorithm) would affect the speed and accuracy 
    of the application.
  - pull in more news sources and allow users to select what they prefer 
  - social features: Pocket integration, twitter/facebook sharing capability,
    email option.
    
