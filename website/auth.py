from flask import Blueprint, redirect, render_template, request, url_for
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from validate_email_address import validate_email
from flask_login import login_user, login_required, logout_user, current_user
import re

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get information from the page that the user has submitted
        username = request.form.get('username')
        password = request.form.get('password')

        # Check for the username
        logname = User.query.filter_by(username = username).first()

        if logname:
            # Check if the password is correct
            if check_password_hash(logname.password, password):
                # Login the user
                login_user(logname, remember=True)
                return redirect(url_for('views.home'))
            else:
                return render_template("login.html", warning = "Incorrect password or username")
        
        # Check for the E-mail if username is not found
        logmail = User.query.filter_by(email = username).first()

        if logmail:
            # Check if the password is correct
            if check_password_hash(logmail.password, password):
                # Login the user
                login_user(logmail, remember=True)
                return redirect(url_for('views.home'))
            else:
                return render_template("login.html", warning = "Incorrect password or E-mail")
        
        # Warn that no username or E-mail with that name is registered
        return render_template("login.html", warning = "Username or E-mail not registered yet")
    else:
        # Load up the login page
        return render_template("login.html")

@auth.route('/sign_up', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get information from the page that the user has submitted
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        email = request.form.get('email')

        # Check if the username already exists or not
        row = User.query.filter_by(username = username).first()
        if row:
            return render_template("signup.html", warning = "Username already taken")

        # Make sure the password is long enough
        if len(password) < 9:
           return render_template("signup.html", warning = "Password needs to be more than 8 characters long")
        elif password != confirm:
            return render_template("signup.html", warning = "Password must match confirmation")

        # Make sure that the E-mail given is valid
        regex = '[a-z 0-9]+[\._]?[a-z 0-9]+[@]\w+[.]\w{2,3}$'
        
        if (re.search(regex, email)):
            # Make sure that if the E-mail given actually exists
            if validate_email(email, verify=True) == False:
                return render_template("signup.html", warning = "E-mail address does not exist")
            
            # Make sure that email address has not yet been registered
            check = User.query.filter_by(email = email).first()
            if check:
                return render_template("signup.html", warning = "E-mail address already registered")
            else:
                # Create the new user account
                new_user = User(email=email, username=username, password=generate_password_hash(password, method='sha256'), status=0)
                db.session.add(new_user)
                db.session.commit()

                # Redirect to login page
                return redirect(url_for('auth.login'))

        # Warn that the E-mail is invalid
        return render_template("signup.html", warning = "Invalid E-mail")   
    else:
        # Load up the sign up page
        return render_template("signup.html")

@auth.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    # Check if the user is a private or public user
    if current_user.status == 0:
        status = "PUBLIC"
    else:
        status ="PRIVATE"

    if request.method == 'POST':
        # Get information from the page that the user has submitted
        new = request.form.get('new')
        old = request.form.get('old')

        # Check if the previous password is correct
        if not check_password_hash(current_user.password, old):
            return render_template("settings.html", user = current_user, status = status, warning = "Incorrect Old Password", text = "warning_set")
        
        # Check if the password is long enough
        if len(new) < 9:
           return render_template("settings.html", user = current_user, status = status, warning = "Password needs to be more than 8 characters long", text = "warning_set")

        # Change the password in the database
        row = User.query.filter_by(id = current_user.id).first()
        row.password = generate_password_hash(new, method='sha256')
        db.session.commit()

        # load the page back up
        return render_template("settings.html", user = current_user, status = status, text = "announcement_set")
    else:
        # Load up the settings page
        return render_template("settings.html", user = current_user, status = status, text = "announcement_set")

@auth.route('/change_status')
@login_required
def change_status():
    # Change the privacy status of the account
    row = User.query.filter_by(id = current_user.id).first()
    if current_user.status == 1:
        row.status = 0
    else:
        row.status = 1
    db.session.commit()

    # Return to the settings page
    return redirect(url_for('auth.settings'))

@auth.route('/logout')
@login_required
def logout():
    # Logout user
    logout_user()
    return redirect(url_for('views.home'))