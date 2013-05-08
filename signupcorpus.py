import model
import sqlalchemy.exc


def load_stories(session):
	f = open('preferenceseed.txt', 'r')
	n = 1
	for line in f:
		# split on '|'' to add to db
		a = line.split('|')
		# clean out whitespace
		for i in a:
			i.strip()
		story = model.InitStories(id=n, url=a[0], title=a[1], abstract=a[2])
		session.add(story)
		session.commit()
		n += 1

def main(session):
	load_stories(session)

if __name__ == "__main__":
    s= model.connect()
    main(s)


