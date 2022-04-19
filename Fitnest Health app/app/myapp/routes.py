

from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify, abort
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_user, logout_user, login_required

from myapp import myapp_obj, db
from myapp.forms import SignupForm, LoginForm, SearchForm, NoteForm
from myapp.models import User, Friend, FriendStatusEnum, Todo, Notes, SharedNotes
from myapp.models_methods import get_friend_status, get_all_friends
from io import BytesIO


@myapp_obj.route("/")
def home():
    """Homepage route"""
    return render_template("homepage.html")

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
        return redirect(url_for("home"))

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
            flash(f'Login requested for user {form.username.data},remember_me={form.remember_me.data}')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for("log"))
        else:
            flash("Login invalid username or password!")
            return redirect('/login')
    return render_template("login.html", form=form)

@myapp_obj.route("/loggedin")
@login_required
def log():
    """User logged in route, this redirects to homepage"""
    return render_template("/homepage.html")

@myapp_obj.route("/logout")
@login_required
def logout():
    """User logged out route, this logout the user and redirects to homepage"""
    logout_user()
    return redirect(url_for("home"))

# Flashcards

# Friends
@myapp_obj.route("/my-friends", methods=['GET', 'POST'])
@login_required
def show_friends():
    """My Friends route for viewing all friends and accepting/rejecting pending friend requests"""
    # Handle show all friends
    friends = []
    for status, oth_user in get_all_friends(current_user.get_id()):
        if status == 'friend':
            buttons = [(f'/remove-friend/{oth_user.id}', 'Remove Friend')]
            print_status = 'Friend'
        elif status == 'pending-sent-request':
            buttons = [(f'/remove-friend/{oth_user.id}', 'Unsend')]
            print_status = 'Sent'
        elif status == 'pending-to-approve':
            buttons = [(f'/add-friend/{oth_user.id}', 'Approve'), (f'/remove-friend/{oth_user.id}', 'Reject')]
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
                buttons = [(f'/remove-friend/{user.id}', 'Remove Friend')]
            elif status == 'pending-sent-request':
                buttons = [(f'/remove-friend/{user.id}', 'Unsend')]
            elif status == 'pending-to-approve':
                buttons = [(f'/add-friend/{user.id}', 'Approve'), (f'/remove-friend/{user.id}', 'Reject')]
            elif status == 'neutral':
                buttons = [(f'/add-friend/{user.id}', 'Add Friend')]
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
        flash(f'Friend request already sent to "{friend_record.user2.username}"')
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


#Pomodoro app
@myapp_obj.route("/pomodoro")
def tomato():
    """Show Pomodoro timer route"""
    return render_template("/pomodoro.html")

# Todo app
@myapp_obj.route("/todo")
def myTodo():
    """Show ToDo list route"""
    todo_list = Todo.query.all()
    return render_template("todo.html", todo_list=todo_list)

@myapp_obj.route("/addTodo", methods=["POST"])
def addTodo():
    """Add ToDo item into ToDo list, then redirect back to show ToDo list"""
    title = request.form.get("title")
    new_todo = Todo(title=title, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("myTodo"))

@myapp_obj.route("/updateTodo/<int:todo_id>")
def updateTodo(todo_id):
    """Mark ToDo item to complete/not complete, then redirect back to show ToDo list"""
    todo = Todo.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("myTodo"))

@myapp_obj.route("/deleteTodo/<int:todo_id>")
def deleteTodo(todo_id):
    """Remove ToDo item from ToDo list, then redirect back to show ToDo list"""
    todo = Todo.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("myTodo"))

@myapp_obj.errorhandler(404)
def page_not_found(e):
    """Handler error404 and print out description of error"""
    return jsonify(error=str(e)), 404

myapp_obj.register_error_handler(404, page_not_found)

@myapp_obj.route("/note/<int:user_id>", methods = ['GET', 'POST'])
@login_required
def note(user_id):
    """ Route to view a users notes"""
    postedNotes = []
    noteIndex = Notes.query.filter_by(User = user_id).all()

    if noteIndex is not None:
        for note in noteIndex:
            postedNotes = postedNotes + [{'Name':f'{note.name}','id':f'{note.id}'}]
        else:
            return redirect(url_for("myTodo"))
    return render_template('note.html', title = 'Notes', noteIndex = postedNotes, user_id = user_id)

@myapp_obj.route("/upload_notes/<int:user_id>", methods = ['GET', 'POST'])
@login_required
def addNotes(user_id):
    '''This route allows user to upload md file and save to database'''
    form = NoteForm()
    if form.validate_on_submit():
        notes = Notes(name = form.name.data, data = form.note.data.read(), user=current_user._get_current_object())
        db.session.add(notes)
        db.session.commit()
        flash("Note has been created")
        return redirect(url_for("home"))
    return render_template('/upload-note.html', title='upload', form=form, user_id=user_id)

@myapp_obj.route("/viewNote/<int:user_id>/<int:id>", methods = ['GET', 'POST'])
@login_required
def viewNotes(user_id, id):
    '''(not functional) route will allow for file to be opened and viewed in html '''
    note = Notes.query.filter_by(id=id).first()
    data = BytesIO(note.data).read()
    return render_template('view_note.html', title='Note', user_id=user_id, id=id, data=data)


