import model
import sqlalchemy.exc
import feedparser # python library that parses feeds in RSS, Atom, and RDF
import random
from pyres import ResQ
from model import session as db_session, Users, Stories, FC, CC, Queue
<<<<<<< HEAD
=======
from classify.classifying import *
>>>>>>> demo_day

r = ResQ()

sources = {"BBC News":"http://feeds.bbci.co.uk/news/rss.xml", "NPR News":'http://www.npr.org/rss/rss.php?id=1001'}
<<<<<<< HEAD
=======

>>>>>>> demo_day

# seed db! open rss file, read it, parse it, create object, 
# add obj to session, commit, and repeat til done

def load_stories(source, session):
	# use feedparser to grab & parse the rss feed
	parsed = feedparser.parse(sources[source])
	# go through each entry in the RSS feed to pull out elements for Stories
	for i in range(len(parsed.entries)):
		title = parsed.entries[i].title
		url = parsed.entries[i].link
		source = source
		# pull abstract, parse out extra crap that is sometimes included 
		abstract = (parsed.entries[i].description.split('<'))[0]
		# connect with db
		story = model.Stories(title=title, url=url, abstract=abstract, source=source)
		# add story to db
		session.add(story)
		# commit 
		session.commit()
<<<<<<< HEAD
	# delete old stories, BUT HOW???
=======

def classify(session):
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


>>>>>>> demo_day

def main(session):
	# for item in sources:
	# 	load_stories(item, session)

<<<<<<< HEAD
=======
	classify(s)

>>>>>>> demo_day
if __name__ == "__main__":
	s = model.session
	main(s)