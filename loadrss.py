import requests
import model
import sqlalchemy.exc
import feedparser
from model import session as db_session, Stories


def load_stories(session):

	sources = {"New York Times":'http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml', "NPR News":'http://www.npr.org/rss/rss.php?id=1001', "BBC":'http://feeds.bbci.co.uk/news/rss.xml', "CNN":'http://rss.cnn.com/rss/cnn_topstories.rss'}
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
			story = model.Stories(title=title, url=url, abstract=abstract, source=source)
			print "connected with db model??"
			# add story to db
			session.add(story)
			print "added story to db"
			# commit 
			session.commit()
			print "committed"


load_stories(model.session)


#marketing education post