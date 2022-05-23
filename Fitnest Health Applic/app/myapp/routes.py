"""This module holds all the flask routes of our app (all URL paths) 
and incharge of the frontend for rendering html templates.

The standarn convention of defining a route here is:

```python
@myapp_obj.route("/my-route")
def my_route():
    # Code here
    return render_template("my_route.html")
```

Or we could redirect to an existing route using:

```python
@myapp_obj.route("/my-route1")
def my_route1():
    # Code here
    return redirect(url_for("my_route"))
```

Detailed flask documentation can be found [here](https://flask.palletsprojects.com/en/2.0.x/api/).

"""

import os
import tempfile
import random
import pathlib
from datetime import datetime
import markdown
from base64 import b64encode
from flask import render_template, flash, redirect, url_for, request, jsonify, abort, send_file
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename


from myapp import myapp_obj, db
from myapp.forms import *
from myapp.models import *
from myapp.models_methods import *

basedir = os.path.abspath(os.path.dirname(__file__))

@myapp_obj.context_processor
def jinja_encode_to_b64():
    def encode_to_b64(blob):
        return b64encode(blob).decode("utf-8")
    return dict(encode_to_b64=encode_to_b64)


@myapp_obj.route("/")
def home():
    """Homepage route"""
    return render_template("homepage.html")


@myapp_obj.route("/about-us")
def about_us():
    """About Us route"""
    return render_template("about-us.html")


@myapp_obj.route("/signup", methods=['GET', 'POST'])
def signup():
    """Signup page route"""
    if current_user.is_authenticated:
        return redirect(url_for("log"))
    form = SignupForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(email=form.email.data, username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created. You can now login")
        return redirect('/dashboard')

    return render_template("signup.html", form=form)


@myapp_obj.route("/login", methods=['GET', 'POST'])
def login():
    """Login page route"""
    if current_user.is_authenticated:
        return redirect(url_for("log"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f'Logged in as User "{form.username.data}", remember_me={form.remember_me.data}')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for("log"))
        else:
            flash("Login invalid username or password!", "error")
            return redirect('/login')
    return render_template("login.html", form=form)


"""Creating a route for the dashboard"""
@myapp_obj.route("/dashboard")
@login_required
def log():
    """User logged in route, this redirects to dashboard"""
    return render_template("/dashboard.html")


"""Creating a route for the My Workouts page"""
@myapp_obj.route("/my-workouts")
@login_required
def my_workouts():
    workouts = Workout.query.filter_by(owner_user_id=current_user.get_id()).order_by(Workout.id.desc()).all()
    return render_template("/my-workouts.html", workouts=workouts)


"""Creating a route for the Add a Workout page"""
@myapp_obj.route("/add-workout", methods=['GET', 'POST'])
@login_required
def add_workout():
    form = AddWorkoutForm()
    if form.validate_on_submit():
        workout = Workout(name=form.name.data, muscle_group=form.muscle_group.data,
                          duration_hour=form.duration_hour.data, duration_minute=form.duration_minute.data,
                          sets=form.sets.data, reps=form.reps.data, description=form.description.data,
                          owner_user_id=current_user.get_id())
        db.session.add(workout)
        db.session.commit()
        flash("Your workout has been created.")
        return redirect(url_for("my_workouts"))
    """User logged in route and selects add workout button, this redirects to Add a Workout page"""
    return render_template("/add-workout.html", form=form)


@myapp_obj.route("/delete-workout")
@login_required
def delete_workout():
    workout_id = request.args.get('id')
    if workout_id:
        Workout.query.filter_by(id=workout_id).delete()
        db.session.commit()
        flash("Your workout has been deleted.")
    return redirect(url_for("my_workouts"))


"""Creating a route for the Edit a Workout page"""
@myapp_obj.route("/leg-day")
@login_required
def leg_workout():
    """User logged in route and wants to view suggested workouts for legs, this redirects to Leg Day page"""
    return render_template("/leg-day.html")


"""Creating a route for the Edit a Workout page"""
@myapp_obj.route("/upperbody-day")
@login_required
def upperbody_workout():
    """User logged in route and wants to view suggested workouts for upper body, this redirects to Upper Body Day page"""
    return render_template("/upperbody-day.html")


"""Creating a route for the Edit a Workout page"""
@myapp_obj.route("/core-day")
@login_required
def core_workout():
    """User logged in route and wants to view suggested workouts for their core, this redirects to Core Day page"""
    return render_template("/core-day.html")


"""Creating a route for the Gymtionary page"""
@myapp_obj.route("/gymtionary")
@login_required
def gymtionary():
    """User logged in route and wants to view machine tutorials, this redirects to Gymtionary page"""
    return render_template("/gymtionary.html")


@myapp_obj.route("/logout")
@login_required
def logout():
    """User logged out route, this logout the user and redirects to homepage"""
    logout_user()
    return redirect(url_for("home"))


AVATAR_IMGS = {
    1: 'images/John_Avatar.png',
    2: 'images/avatar2.png',
    3: 'images/Spencer_Avatar.png',
    4: 'images/Ali_Avatar.png',
    5: 'images/avatar5.png',
    6: 'images/Hannah_Avatar.png',
}

@myapp_obj.route("/account")
@login_required
def account():
    """User's account page, redirect if need to change avatar"""

    return render_template("/account.html", avatars=AVATAR_IMGS)


@myapp_obj.route("/change_avatar/<int:avatar_id>")
@login_required
def change_avatar(avatar_id):
    """To switch avatar pictures and more, then redirect back to account"""
    if avatar_id in AVATAR_IMGS:
        avatar_path = os.path.join(basedir, f'./static/{AVATAR_IMGS[avatar_id]}')
        if os.path.exists(avatar_path):
            user = current_user._get_current_object()
            with open(avatar_path, 'rb') as fp:
                user.avatar = fp.read() # Modify avatar blob
                db.session.commit()
        else:
            raise Exception(f"Avatar {avatar_path} doesn't exists")
    return redirect(url_for("account"))




# Friends
@myapp_obj.route("/my-friends", methods=['GET', 'POST'])
@login_required
def show_friends():
    """My Friends route for viewing all friends and accepting/rejecting pending friend requests"""
    # Handle show all friends
    friends = []
    for status, oth_user in get_all_friends(current_user.get_id()):
        if status == 'friend':
            buttons = [(f'/remove-friend/{oth_user.id}', 'Remove Friend', 'btn-outline-danger')] #Tuple in the format (link, text, button_type)
            print_status = 'Friend'
        elif status == 'pending-sent-request':
            buttons = [(f'/remove-friend/{oth_user.id}', 'Unsend', 'btn-outline-warning')]
            print_status = 'Sent'
        elif status == 'pending-to-approve':
            buttons = [(f'/add-friend/{oth_user.id}', 'Approve', 'btn-outline-success'),
                        (f'/remove-friend/{oth_user.id}', 'Reject', 'btn-outline-danger')
                    ]
            print_status = 'Pending'
        else:
            abort(404, f'Unknown status {status}')
        friends.append((oth_user, print_status, buttons))
    # Handle Add user
    found_users = []
    search_form = SearchForm()
    if search_form.validate_on_submit():
        search_str = search_form.text.data
        result = User.query.filter(User.username.contains(search_str) & (User.id != (current_user.get_id()))).all()
        for user in result:
            status, _ = get_friend_status(current_user.get_id(), user.id)
            if status == 'friend':
                buttons = [(f'/remove-friend/{user.id}', 'Remove Friend', 'btn-outline-danger')]
            elif status == 'pending-sent-request':
                buttons = [(f'/remove-friend/{user.id}', 'Unsend', 'btn-outline-warning')]
            elif status == 'pending-to-approve':
                buttons = [(f'/add-friend/{user.id}', 'Approve', 'btn-outline-success'),
                            (f'/remove-friend/{user.id}', 'Reject', 'btn-outline-danger')
                        ]
            elif status == 'neutral':
                buttons = [(f'/add-friend/{user.id}', 'Add Friend', 'btn-outline-info')]
            else:
                abort(404, description=f'Unknown status {status}')
            found_users.append((user.username, buttons))
    return render_template("my-friends.html", friends=friends, search_form=search_form, found_users=found_users)


@myapp_obj.route("/add-friend/<int:user_id>", methods=['GET', 'POST'])
@login_required
def add_friend_userid_provided(user_id):
    """A route for handling an add friend request, this will redirect back to MyFriends page"""
    # Abort if adding self as friend
    if int(current_user.get_id()) == user_id:
        return abort(404, description="Cannot add yourself as friend")
    status, friend_record = get_friend_status(current_user.get_id(), user_id)
    if status == 'friend':
        # Already a friend, do nothing
        pass
    elif status == 'pending-sent-request':
        # Current user sent a request, do nothing
        flash(f'Friend request already sent to "{friend_record.user2.username}"', "warning")
    elif status == 'pending-to-approve':
        # Other user sent the request, approve (Change status from pending to approved)
        friend_record.status = FriendStatusEnum.FRIEND
        db.session.add(friend_record)
        db.session.commit()
        flash(f'Approved friend request from "{friend_record.user1.username}"')
    elif status == 'neutral':
        # No friendship record found, send friend request
        user = User.query.filter_by(id=user_id).one()
        friend = Friend(user1_id=current_user.get_id(), user2_id=user.id, status=FriendStatusEnum.PENDING)
        db.session.add(friend)
        db.session.commit()
        flash(f'Sent friend request to "{user.username}"')
    else:
        abort(404, description=f"Unknown status {status}")
    return redirect(url_for("show_friends"))


@myapp_obj.route("/remove-friend/<int:user_id>", methods=['GET', 'POST'])
@login_required
def remove_friend_userid_provided(user_id):
    """A route for handling cancel sent friend request and reject freind request,
    this will then redirect back to MyFriends page
    """
    # Abort if removing self as friend
    if int(current_user.get_id()) == user_id:
        return abort(404, description="Cannot remove yourself from friend")
    status, friend_record = get_friend_status(current_user.get_id(), user_id)
    if friend_record:
        other_user = friend_record.user1.username if friend_record.user1.id != int(current_user.get_id()) else friend_record.user2.username
        if status == 'friend':
            flash(f'Removed "{other_user}" from friend')
        elif status == 'pending-sent-request':
            flash(f'Unsent friend request to "{other_user}"')
        elif status == 'pending-to-approve':
            flash(f'Rejected friend request from "{other_user}"')
        elif status == 'neutral':
            pass # Do nothing
        else:
            abort(404, description=f'Unknown status {status}')
        db.session.delete(friend_record)
        db.session.commit()
    return redirect(url_for("show_friends"))
#stopwatch route
@myapp_obj.route("/stopwatch")
def stopwatch():
    """Show stopwatch route"""
    return render_template("/stopwatch.html")

#activity page route
@myapp_obj.route("/activity")
def activity():
    return render_template("activity.html")

#Todo feature
@myapp_obj.route("/todo")
@login_required
def myTodo():
    """Show ToDo list route"""
    todo_list = Todo.query.filter_by(user_id=current_user.get_id()).all()
    return render_template("todo.html", todo_list=todo_list)


@myapp_obj.route("/addTodo", methods=["POST"])
@login_required
def addTodo():
    """Add ToDo item into ToDo list, then redirect back to show ToDo list"""
    title = request.form.get("title")
    new_todo = Todo(title=title, user_id=current_user.get_id(), complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("myTodo"))


@myapp_obj.route("/updateTodo/<int:todo_id>")
@login_required
def updateTodo(todo_id):
    """Mark ToDo item to complete/not complete, then redirect back to show ToDo list"""
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.get_id()).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("myTodo"))


@myapp_obj.route("/deleteTodo/<int:todo_id>")
@login_required
def deleteTodo(todo_id):
    """Remove ToDo item from ToDo list, then redirect back to show ToDo list"""
    todo = Todo.query.filter_by(id=todo_id, user_id=current_user.get_id()).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("myTodo"))


@myapp_obj.errorhandler(404)
def page_not_found(e):
    """Handler error404 and print out description of error"""
    return jsonify(error=str(e)), 404


myapp_obj.register_error_handler(404, page_not_found)


@myapp_obj.route("/journal", methods=['GET', 'POST'])
@login_required
def show_journals():
    """ Route to view a users journals"""
    return redirect(url_for('view_journal', journal_id=0)) # journal_id 0 indicate no journal to view



@myapp_obj.route("/viewJournal/<int:journal_id>", methods=['GET', 'POST'])
@login_required
def view_journal(journal_id):
    '''Route to view journal, this is similar to show_journal '''
    journal = None
    html_text = None
    posted_journals = []
    search_text = request.form.get('text')
    user_id = current_user.get_id()
    search_form = SearchForm()
    if search_text:
        journals = Journal.query.filter_by(user_id=current_user.get_id()).filter(Journal.data.contains(search_text)).all()
        if journals:
            flash(f'{len(journals)} search results found')
        else:
            flash('No search results found', "error")
    else:
        journals = Journal.query.filter_by(user_id=current_user.get_id()).all()
        if journal_id != 0:
            journal = Journal.query.filter_by(id=journal_id, user_id=current_user.get_id()).one_or_none()
            html_text =  markdown.markdown(journal.data)
    for x in journals:
        posted_journals = posted_journals + [{'name':f'{x.name}','id':f'{x.id}'}]
    return render_template('journal.html', title='Journal', posted_journals=posted_journals, journal=journal, html_text=html_text, user_id=user_id, search_form=SearchForm())





@myapp_obj.route("/upload-journal", methods=['GET', 'POST'])
@login_required
def upload_journal():
    """Import journal route, for user to import markdown file into journal"""
    form = UploadMarkdownForm()
    if form.validate_on_submit():
        n = form.file.data
        filename = n.filename
        content = n.stream.read().decode('ascii')
        journal = Journal(name=filename, data=content, user_id=current_user.get_id())
        db.session.add(journal)
        db.session.commit()
        flash(f'Uploaded Journal {filename} ')
        return redirect(url_for("show_journals"))
    return render_template("import-journal.html", form=form)



@myapp_obj.route("/share-journals/<int:journal_id>", methods=['GET', 'POST'])
@login_required
def share_journal(journal_id):
    ''' route will allow user to share journals to other users(friends)'''
    journal = Journal.query.filter_by(id=journal_id).one_or_none()
    friends = []
    for status, oth_user in get_all_friends(current_user.get_id()):
        if status == 'friend':  # Only find friends
            friends.append(oth_user)
    form = JournalShareForm()
    form.dropdown.choices = [(u.id, u.username) for u in friends]
    if form.validate_on_submit():
        user = User.query.filter_by(id=form.dropdown.data).one()
        now = datetime.now()
        shared_journal = SharedJournal(journal_id=journal_id, datetime=now, owner_user_id=current_user.get_id(), target_user_id=user.id)
        db.session.add(shared_journal)
        db.session.commit()
        flash(f'Shared Journal "{shared_journal.journal.name}" to "{user.username}" on {str(datetime.now())}')
        return redirect(url_for("show_journals"))
    return render_template("share-journals.html", journal=journal, form=form)


@myapp_obj.route("/journals-sharing", methods=['GET', 'POST'])
@login_required
def journals_sharing():
    """A route for viewing sharing status of journals (both shared to others and others shared to me)"""
    owner_journals = SharedJournal.query.filter_by(owner_user_id=current_user.get_id()).all()
    target_journals = SharedJournal.query.filter_by(target_user_id=current_user.get_id()).all()
    return render_template("journals-sharing.html", owner_journals=owner_journals, target_journals=target_journals)



@myapp_obj.route("/journals-sharing/add-to-myjournals/<int:sharing_id>", methods=['GET', 'POST'])
@login_required
def journals_sharing_add_to_myjournals(sharing_id):
    """A route for adding shared journals that other user shared into My journals"""
    sharing = SharedJournal.query.get(sharing_id)
    if int(current_user.get_id()) != sharing.owner_user_id and\
        int(current_user.get_id()) != sharing.target_user_id:
        abort(404, description='Invalid permission')
    journal = Journal(name=sharing.journal.name, data=sharing.journal.data, user_id=current_user.get_id())
    db.session.add(journal)
    db.session.commit()
    flash(f'Copied journal(#{sharing.journal.id}) to "My Journals", new journal(#{journal.id})')
    return redirect(url_for('journals_sharing'))


@myapp_obj.route("/journals-sharing/cancel-sharing/<int:sharing_id>", methods=['GET', 'POST'])
@login_required
def journals_sharing_cancel_sharing(sharing_id):
    """A route for cancelling a journals sharing"""
    sharing = SharedJournal.query.get(sharing_id)
    if int(current_user.get_id()) != sharing.owner_user_id and\
        int(current_user.get_id()) != sharing.target_user_id:
        abort(404, description='Invalid permission')
    flash(f'Sharing of journal(#{sharing.journal.id}) cancelled')
    db.session.delete(sharing)
    db.session.commit()
    return redirect(url_for('journals_sharing'))

@myapp_obj.route("/delete-journal/<int:todo_id>")
@login_required
def delete_journal(journal_id):
    """Remove journal item from ToDo list, then redirect back to show ToDo list"""
    journal = Journal.query.filter_by(id=journal_id).one_or_none()
    db.session.delete(journal)
    db.session.commit()
    return redirect(url_for("myTodo"))
