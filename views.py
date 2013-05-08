import os, sys
from flask import Flask, render_template, redirect, request, jsonify, session
from flask import url_for, g, flash
import model
from model import session as db_session, Users, Stories, InitStories, FC, CC, Queue
import pyres
from pyres import ResQ
from classify.classifying import Classifier, FisherClassifier
from apscheduler.scheduler import Scheduler
from local_settings import SECRET_KEY


app = Flask(__name__)
app.secret_key = SECRET_KEY

# define redis server
r = ResQ(server="localhost:6379")


<<<<<<< HEAD:views.py
=======

>>>>>>> demo_day:routes.py
@app.teardown_request
def shutdown_session(exception = None):
    db_session.remove()


@app.before_request
def load_user_id():
    g.user_id = session.get('user_id')


@app.route("/")
def index():
    # build this page so users can sign up, take a tour, log in
    return render_template("login.html")


@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


@app.route("/validate", methods=['POST'])
def validate_login():
    # TODO: GO THROUGH AND SANITIZE STUFF --> will need to encode form input to match what's encoded in the database (using urllib.quote())
    form_email = request.form['email']
    form_password = request.form['password']
    #form_email and form_password must both exist and match in db for row to be an object. Row is the entire row from the users table, including the id
    row = model.session.query(model.Users).filter_by(email=form_email, password=form_password).first()

    if row:
        session['email'] = request.form['email']
        session['user_id'] = row.id
        return redirect("/news")
    else:
        flash('Please enter a valid email address and password.')
        return redirect("/login")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/validate", methods=['POST'])
def validate_login():
    # TODO: GO THROUGH AND SANITIZE STUFF --> will need to encode form input to match what's encoded in the database (using urllib.quote())
    form_email = request.form['email']
    form_password = request.form['password']
    #form_email and form_password must both exist and match in db for row to be an object. Row is the entire row from the users table, including the id
    row = model.session.query(model.Users).filter_by(email=form_email, password=form_password).first()

    if row:
        session['email'] = request.form['email']
        session['user_id'] = row.id

        flash('Logged in as: ' + session['email'])
        # classifying all urls in db.
        FisherClassifier.perform(session['user_id'])
        # grab all items in queue
        queue_list = model.session.query(model.Queue).all()
        # pull story info by using queued story_id reference???
        story_list = []
        for i in queue_list:
            story_list.append(model.session.query(model.Stories).filter_by(id=i.story_id).first())

        return render_template("news.html", story_list=story_list)

    else:
        flash('Please enter a valid email address and password.')
        return redirect("/login")


@app.route("/signup", methods=['POST'])
def signup():
    email = request.form['email']
    password = request.form['password']
    existing = db_session.query(Users).filter_by(email=email).first()
    if existing:
        flash("Email already in use")
        return redirect(url_for("index"))

    u = Users(email=email, password=password)
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    session['user_id'] = u.id
    return redirect(url_for("selection"))


@app.route("/selection")
def selection():
    #make sure user is signed in
    # if not g.user_id:
    #     flash("Please log in first!")
    #     return redirect(url_for('login'))
    # else:
    # grab all items in queue
    queue_list = model.session.query(model.InitStories).all()
    # pull story info by using queued story_id reference???
    story_list = []
    for i in queue_list:
        story_list.append(model.session.query(model.InitStories).filter_by(id=i.id).first())

    return render_template("selection.html", story_list=story_list)


@app.route("/initpref", methods=["POST"])
def initpref():
    story_id = request.args.get("id")
    print story_id
    pref = request.args.get("value")
    user_id = session['user_id']
    # query story table in db to get url
    story = model.session.query(model.InitStories).filter_by(id=story_id).first()
    # add the classifier job to the pyres queue
    print story
    print story['id']
    print user_id
    print pref
    r.enqueue(Classifier, story.id, user_id, pref)
    classify
    Classifier.perform(story.url, user_id, pref)

    # return user to news page
    return "Got it in that database"


@app.route("/first")
def first_news():
    # classifying all urls in db, add new best-rated stories to Queue, remove old stories from Queue
    FisherClassifier.perform(session['user_id'])
    # grab all items in queue
    queue_list = model.session.query(model.Queue).filter_by(user_id=session['user_id']).all()        
    # pull story info by using queued story_id reference???
    story_list = []
    for i in queue_list:
        story_list.append(model.session.query(model.Stories).filter_by(id=i.story_id).first())
<<<<<<< HEAD:views.py

    return render_template("news.html", story_list=story_list)

=======

    return render_template("news.html", story_list=story_list)
>>>>>>> demo_day:routes.py


@app.route("/news")
def news():
<<<<<<< HEAD:views.py
    #make sure user is signed in
    # if not g.user_id:
    #     flash("Please log in first!")
    #     return redirect(url_for('login'))
    # else:
=======
    # TODO: Check Queue: if it is empty, classify. Otherwise, just display it.
    queued = db_session.query(Queue).filter_by(user_id=session['user_id']).all()
    if len(queued) < 5:
        FisherClassifier.perform(session['user_id'])

    # grab all items in queue
>>>>>>> demo_day:routes.py
    queue_list = model.session.query(model.Queue).all()
    story_list = []
    for i in queue_list:
        story_list.append(model.session.query(model.Stories).filter_by(id=i.story_id).first())

    return render_template("news.html", story_list=story_list)


# TO DO: for preference routes, make story diappear from page view after button click action
@app.route("/like", methods=["POST"])
def like():
    story_id = request.form["story_id"]
    user_id = session['user_id']
	# query story table in db to get url
    story = model.session.query(model.Stories).filter_by(id=story_id).first()
    # Classify: Comment this out when PyRes is back
    # Classifier.perform(story.url, user_id, "yes")
	# add the classifier job to the pyres queue
<<<<<<< HEAD:views.py
	r.enqueue(Classifier, story.url, user_id, "yes")

	# return user to news page,  
	return redirect(url_for('news'))
=======
    r.enqueue(Classifier, story.url, user_id, "yes")
	# return user to news page
    return redirect(url_for('news'))
>>>>>>> demo_day:routes.py


# TO DO: for preference routes, make story diappear from page view after button click action???
@app.route("/dislike", methods=["POST"])
def dislike():
<<<<<<< HEAD:views.py
	story_id = request.form["story_id"]
	user_id = session['user_id']
	# query story table in db to get url
	story = model.session.query(model.Stories).filter_by(id=story_id).first()
	# add the classifier job to the pyres queue
	r.enqueue(Classifier, story.url, user_id, "no")
	# remove selected article from Queue and therefore view
	db_session.query(Queue).filter_by(user_id=user_id, story_id=story_id).delete()
	db_session.commit()

	# send user back to news page like nothing is taking any time
	return redirect(url_for('news'))
=======
    story_id = request.form["story_id"]
    user_id = session['user_id']
    # query story table in db to get url
    story = model.session.query(model.Stories).filter_by(id=story_id).first()
    # just classify, we'll have to wait til I get my head around pyres
    # Classifier.perform(story.url, user_id, "no")
    # add the classifier job to the pyres queue
    r.enqueue(Classifier, story.url, user_id, "no")
    # remove selected article from Queue and therefore view
    # db_session.query(Queue).filter_by(user_id=user_id, story_id=story_id).delete()
    # db_session.commit()
    # send user back to news page like nothing is taking any time
    return redirect(url_for('news'))

@app.route("/playing")
def playing():
    return render_template("selectionjs.html")
>>>>>>> demo_day:routes.py


@app.route("/logout")
def logout():
	del session['user_id']
	return redirect(url_for("index"))


if __name__ == "__main__":
	app.run(debug = True)
