import re
import math
import sqlite3 as sqlite
import sys
from sys import argv
from decruft import Document
import urllib2
from pyquery import PyQuery
import time
from model import session as db_session, Users, Stories, FC, CC, Queue
import sqlalchemy.exc
import feedparser
from pyres import ResQ

r = ResQ()


# This class encapsulates what the classifier has learned so far
# With this, we can instantiate multiple classifiers for different 
# users, groups, or queries & can train differently to respond to 
# particular needs
class Classifier:
	# queue method to work with pyres, defines a queue for classify actions
	queue = "training"

	def __init__(self, getfeatures, user_id):
		self.user_id = user_id

		# fc stores counts for different features in diferent 
		# classifications: {'python':{'bad':0, 'good':6}...}
		self.fc = {}

		# cc: dict of hwo many times each classification has
		# been used -> needed for probability calculations
		self.cc = {}

		# function used to extract features from the items
		# being classified (here, it's the getwords funct)

		# TODO: UNDERSTAND THIS CONNECTION????
		self.getfeatures = getfeatures

	@staticmethod
	def gettext(url):
		# use decruft methods to grab article from page html
		f = urllib2.urlopen(url)
		html = (Document(f.read()).summary())

		# use pyquery to get rid of all markup: just leave article text
		doc = PyQuery(html)
		article = doc.text()
		return article

	@staticmethod
	def getwords(doc):
		# list of common words we want to ignore from our corpus
		commonWords = ('the','be','to','of','and','a','in','that','have','it','is','im','are','was','for','on','with','he','as','you','do','at','this','but','his','by','from','they','we','say','her','she','or','an','will','my','one','all','would','there','their','what','so','up','out','if','about','who','get','which','go','me','when','make','can','like','time','just','him','know','take','person','into','year','your','some','could','them','see','other','than','then','now','look','only','come','its','over','think','also','back','after','use','two','how','our','way','even','because','any','these','us')
		# split word by non-alpha characters	
		# TODO: also remove numbers??
		splitter = re.compile('\\W*')
		# lowercase all words, discount short & common words
		words = [s.lower() for s in splitter.split(doc) if len(s)>2 and s not in commonWords and not s.isdigit()]
		# return a list of words from source
		return words

	@staticmethod 
	def perform(url, user_id, classification):
		# grab article text, parse out markup and return list of significant words
		artwords = Classifier.getwords(Classifier.gettext(url))
		# need to make a Classifier instance in order to reference a class method
		classifier = Classifier(artwords, user_id)
		# set up db (or connect if exists)
		classifier.setdb('news.db')
		# train db w/new words and their classifications
		for item in artwords:
			classifier.train(item, classification)



	# method that opens the dbfile for this classifier and creates
	# tables if necessary
	def setdb(self, dbfile):
		self.con = sqlite.connect(dbfile)


	# HELPER FUNCTIONS!!!! --> interact w/database
	
	# increase count of a feature/category pair by 1 in fc table
	def incf(self, f, cat):
		count = self.fcount(f, cat)
		if count == 0:
			self.con.execute("INSERT INTO fc VALUES (NULL, '%s', '%s', 1, %d)" % (f, cat, self.user_id))
		else:
			self.con.execute("UPDATE fc SET count=%d WHERE feature='%s' AND category='%s' AND user_id=%d" % (count+1, f, cat, self.user_id))

	# number of times a feature has appeared in a category in fc table
	def fcount(self, f, cat):
		res = self.con.execute("SELECT count FROM fc WHERE feature='%s' AND category='%s' AND user_id=%d" %(f, cat, self.user_id)).fetchone()
		if res == None:
			return 0
		else:
			return res[0]

	# increase the count of a category in cc table
	def incc(self, cat):
		count = self.catcount(cat)
		if count == 0:
			self.con.execute("INSERT INTO cc VALUES (NULL, '%s', 1, %d)" % (cat, self.user_id))
		else:
			self.con.execute("UPDATE cc SET count=%d WHERE category='%s' AND user_id=%d"%(count+1, cat, self.user_id))

	# query db for current category count
	def catcount(self, cat):
		res = self.con.execute("SELECT count FROM cc WHERE category='%s' AND user_id=%d"%(cat, self.user_id)).fetchone()

		if res == None:
			return 0
		else:
			return float(res[0])

	# the list of all existing categories:
	def categories(self):
		cur = self.con.execute("SELECT category FROM cc WHERE user_id=%d"%(self.user_id));
		return [d[0] for d in cur]

	# total number of items
	def totalcount(self):
		res = self.con.execute("SELECT sum(count) FROM cc WHERE user_id=%d"%(self.user_id)).fetchone();
		if res == None:
			return 0
		else:
			return res[0]

	# train method: takes doc item (a word in our case) and a classification 
	# (in our case, yes or no). Uses getfeatures func to break items into separate features,
	# then increases counts for this classification for each feature, then increases total 
	# count for classification
	def train(self, item, cat):
		# increment count the item of this category
		self.incf(item, cat)
		# increment count for this category
		self.incc(cat)
		# save to db
		self.con.commit()

	# calculate probability that a word is in yes or no cats by dividing
	# the number of times the word appears in a doc in that cat by total number
	# of docs in that cat?
	def fprob(self, f, cat):
		# check to see the current count of category occurances
		if self.catcount(cat)==0: 
			return 0
		# total number of times this feature appeared in this category divided by total items in this category
		# Pr(A|B) --> conditional probability
		return self.fcount(f, cat)/self.catcount(cat) #works! theoretically

	# calculate a weighted probabiity with an assumed probability of 0.5
	def weightedprob(self, f, cat, prf, weight=1.0, ap=0.5):
		# calculate current probability FOR THIS USER
		basicprob=prf(f, cat)
		# count times the feature has appeared in all categories FOR THIS USER
		totals = sum([self.fcount(f,c) for c in self.categories()])
		# calculate weighted average
		bp = ((weight*ap)+(totals*basicprob))/(weight+totals)
		return bp 

#################################################################################
# Fisher classifier: begin by calculating how likely it is that a doc fits into
# a certian category given that a particular feature is in that dcument (Pr(cat|feature))
# Considers normalization (given uneven categorization):
# clf = Pr(feature|category) for this category
# freqsum = Sum of Pr(feature|category) for ALL categories
# cprob = clf / (clf + nclf)
###############################################################################
class FisherClassifier(Classifier):
	
	# queue method to work with pyres, defines a queue for classify actions
	# moved this to feedseed.py (which then talks to this doc)
	# queue = "predict"

	# init method w/variable to store cutoffs
    def __init__(self, getfeatures, user_id):
        Classifier.__init__(self, getfeatures, user_id)
        self.minimums={}
	

	# classify and pull relevant news stories for user's feed!
    @staticmethod 
    def perform(user_id):
        # grab range of current queue ids for user
        exist_q = db_session.query(Queue).filter_by(user_id=user_id).all()
        exist = []
        for s in exist_q:
            exist.append(s.id)

	    # grab all RSS stories from Story table of db
        stories = db_session.query(Stories).all()
	    # set up a queue for ranked stories
        queue = []
        for item in stories:
		    # determine probability that the user will like this item
            try:
                doc = Classifier.gettext(item.url) # strong of article words
            except Exception:
                pass
            cl = FisherClassifier(Classifier.getwords, user_id) # returns FC instance

            cl.setdb('news.db')
            # find the probability that a user will like a given article
            probability = cl.fisherprob(doc, 'yes')
            if probability > 0:
            # add item's probability to the queue dictionary
               tup = (item.id, probability)
               queue.append(tup)
        	    # queue[item.id]=probability
		# sort queue by probability, lowest --> highest
	    queue = sorted(queue, key=lambda x: x[1])
		
		# grab top and lower rated stories, add to Queue 
	    if len(queue)>=10:
		    for i in queue[:2]:
			    story_id = i[0]
			    score = i[1]
			    # add story, user, and probabiilty to the db for pulling articles for users
			    story = Queue(story_id=story_id, score=score, user_id=user_id)
			    db_session.add(story)
		    for i in queue[-8:]:
			    story_id = i[0]
			    score = i[1]
				# add story, user, and probabiilty to the db for pulling articles for users
			    story = Queue(story_id=story_id, score=score, user_id=user_id)
			    db_session.add(story)
		    db_session.commit()
	    else:
		    for i in queue:
			    story_id = i[0]
			    score = i[1]
			    # add story, user, and probabiilty to the db for pulling articles for users
			    story = Queue(story_id=story_id, score=score, user_id=user_id)
			    db_session.add(story)
		    db_session.commit()

		# clear old stories out of queue once new have been added
	    for i in exist:
		    d = db_session.query(Queue).filter_by(id=i).first()
		    db_session.delete(d)
	    db_session.commit()


	# set mins and get values (default to 0)
	def setminimum(self, cat, min):
		self.minimums[cat] = min


	def getminimum(self, cat):
		if cat not in self.minimums:
			return 0
		return self.minimums[cat]


	def cprob(self, f, cat):
		# frequency of this feature in this category
		clf = self.fprob(f, cat)
		if clf == 0: 
			return 0
		# frequency of this feature in all categories
		freqsum = sum([self.fprob(f,c) for c in self.categories()])
		# probability is the frequency in this category divided by overall frequency
		p = clf / (freqsum)
		return p # the probability that an item w/feature belongs in specified category, assuming equal items in each cat.


	# estimate overall probability: mult all probs together, take log, mult by -2
	def fisherprob(self, item, cat):
		# multiply all probabilities together	
		features = self.getwords(item) # list of words
		p = 1
		for f in features: # iterate through list
			p = p*(self.weightedprob(f, cat, self.cprob)) 
			# account for articles that are wildly not aligned with user's interests, since log(0) will break the classifier...
			if p == 0:
				return 0
		# take natural log and multiply by -2
		fscore = (-2)*math.log(p)

		# use inverse chi2 function to get a probability
		return self.invchi2(fscore, len(features)*2)

	# inverse chi-square function
	# by feeding fisher calculation to this, we get the probability that
	# a random  set of probabilities would return a high number for 
	# an item belonging in the category (eq. from CI book, p. 130)
	def invchi2(self, chi, df):
		m = chi / 2.0
		sum = term = math.exp(-m)
		for i in range(1, df//2):
			term *= m / i
			sum += term
		return min(sum, 1.0)


def main():
	print "Main 1"
	# FisherClassifier.perform(url="http://www.bbc.co.uk/news/technology-22368287", user_id=0)

	

if __name__ == "__main__":
    main()
