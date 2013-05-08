import model
import feedparser
from model import session as db_session, Users, Stories, FC, CC, Queue
from classify.classifying import FisherClassifier
from apscheduler.scheduler import Scheduler
import sqlalchemy.exc
import requests

sched = Scheduler()

@sched.cron_schedule(hour='*/5')
def load_rss():
	# query the db: how long is it? Use this number later to empty db of old stories
    exstories = db_session.query(Stories).all()
    last_id = exstories[-1].id
    sources = {"NPR News": 'http://www.npr.org/rss/rss.php?id=1001', "BBC": 'http://feeds.bbci.co.uk/news/rss.xml'}
    for source in sources:
        print source
        # use feedparser to grab & parse the rss feed
        parsed = feedparser.parse(sources[source])
        print "parsed"
        # go through each entry in the RSS feed to pull out elements for Stories
        for i in range(len(parsed.entries)):
            title = parsed.entries[i].title
            url = parsed.entries[i].link
            source = source
            # pull abstract, parse out extra crap that is sometimes included
            abstract = (parsed.entries[i].description.split('<'))[0]
            print abstract

            # connect with db
            story = db_session.Stories(title=title, url=url, abstract=abstract, source=source)
            print "connected with db model??"
            # add story to db
            db_session.add(story)
            print "added story to db"
            # commit
        db_session.commit()
        print "committed"
    # delete from db old stories
    for l in range(1,last_id+1):
        db_session.query(Stories).filter_by(id=l).delete()
    db_session.commit()    



@sched.cron_scheduler(hour='*/6')
def classify():
    # perform Fisher Classifier method for ALL users in db
    # query db for users: put user_ids into a list to iterate through
    users = model.session.query(model.Users).all()
    # for each user create queue of most appropriate stories
    for i in users:
        # classifying all urls in db, add new best-rated stories to Queue, remove old stories from Queue
        FisherClassifier.perform(i.id)
        # grab all items in queue
        queue_list = model.session.query(model.Queue).all()        
        # pull story info by using queued story_id reference???
        story_list = []
        for i in queue_list:
            story_list.append(model.session.query(model.Stories).filter_by(id=i.story_id).first())

        return render_template("news.html", story_list=story_list)

sched.start()


while True:
    pass