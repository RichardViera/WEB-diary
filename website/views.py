from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from . import db
from .models import Diaries, User
from datetime import date

views = Blueprint('views', __name__)
warning = 0

@views.route('/')
def home():
    # Loads the main page
    return render_template("home.html", user=current_user)

@views.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    datenow = date.today()
    if request.method == 'POST':
        # Get the title and the entry that the user has provided
        title = request.form.get('title')
        entry = request.form.get('entry')

        if len(title) < 1 or len(entry) < 1:
            return redirect(url_for('views.write'))
        
        # Log the entry into the database
        new_entry = Diaries(user_id = current_user.id, title=title, entry=entry, date=datenow)
        db.session.add(new_entry)
        db.session.commit()
        
        # Return to main page
        return redirect(url_for('views.home'))
    else:
        # If there has been an entry already today reroute to home page
        logname = Diaries.query.filter_by(date = datenow).first()
        if logname:
            return redirect(url_for('views.home'))

        # Load up the page
        d1 = datenow.strftime("%B %d, %Y")
        return render_template("write.html", user = current_user, date = d1)

@views.route('/read/<id>')
@login_required
def read(id):
    # Pull up the specific diary entry
    entry = Diaries.query.filter_by(id = id).first()

    # If it doesn't exist go back to homepage
    if not entry:
        return redirect(url_for('views.home'))

    # Render the page
    return render_template("read.html", user = current_user, entry = entry)

@views.route('/explore', methods=['GET', 'POST'])
@login_required
def explore():
    if request.method == 'POST':
        # Get data from user
        search = request.form.get('search')

        # Get users who have names similiar to the one searched
        rows = User.query.filter(User.username.like(search)).all()

        # Delete the current user or users who have a private account if they are in the rows
        for author in rows:
            if author.id == current_user.id:
                del author
            elif author.status == 1:
                del author

        # Render the page with the results
        return render_template("explore.html", user = current_user, result = rows, search =search)
    else:
        # Render the search page
        return render_template("explore.html", user = current_user)

@views.route('/user/<id>')
@login_required
def user(id):
    # Get all the diary entries of this user from the database
    author = User.query.filter_by(id = id).first()
    return render_template("user.html", user = current_user, author = author)

@views.route('/read_others/<id>')
@login_required
def read_others(id):
    # Pull up the specific diary entry
    entry = Diaries.query.filter_by(id = id).first()

    # If it doesn't exist go back to homepage
    if not entry:
        return redirect(url_for('views.home'))

    # Pull up the author
    author = User.query.filter_by(id = entry.user_id).first()

    # Render the page
    return render_template("read_author.html", user = current_user, entry = entry, author = author)
