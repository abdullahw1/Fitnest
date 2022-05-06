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
from xhtml2pdf import pisa
from werkzeug.utils import secure_filename


from myapp import myapp_obj, db
from myapp.forms import SignupForm, LoginForm, UploadMarkdownForm, SearchForm, NextButton, ObjectiveForm, NoteForm, NoteShareForm
from myapp.models import User, Friend, FriendStatusEnum, Todo, Note, SharedNote
from myapp.models_methods import get_friend_status, get_all_friends

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
            flash(f'Logged in as User "{form.username.data}", remember_me={form.remember_me.data}')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for("log"))
        else:
            flash("Login invalid username or password!", "error")
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


AVATAR_IMGS = {
    1: 'images/clipart722174.png',
    2: 'images/clipart722180.png',
    3: 'images/clipart1236782.png',
    4: 'images/clipart1236792.png',
    5: 'images/clipart1237041.png',
    6: 'images/clipart1237090.png',
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


#Pomodoro app
@myapp_obj.route("/pomodoro")
def tomato():
    """Show Pomodoro timer route"""
    return render_template("/pomodoro.html")
#stopwatch app
@myapp_obj.route("/stopwatch")
def stopwatch():
    """Show stopwatch route"""
    return render_template("/stopwatch.html")

# Todo app
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


@myapp_obj.route("/note", methods=['GET', 'POST'])
@login_required
def show_notes():
    """ Route to view a users notes"""
    return redirect(url_for('view_notes', note_id=0)) # note_id 0 indicate no note to view


@myapp_obj.route("/viewNote/<int:note_id>", methods=['GET', 'POST'])
@login_required
def view_notes(note_id):
    '''Route to view note, this is similar to show_notes '''
    note = None
    html_text = None
    posted_notes = []
    search_text = request.form.get('text')
    user_id = current_user.get_id()
    search_form = SearchForm()
    if search_text:
        notes = Note.query.filter_by(user_id=current_user.get_id()).filter(Note.data.contains(search_text)).all()
        if notes:
            flash(f'{len(notes)} search results found')
        else:
            flash('No search results found', "error")
    else:
        notes = Note.query.filter_by(user_id=current_user.get_id()).all()
        if note_id != 0:
            note = Note.query.filter_by(id=note_id, user_id=current_user.get_id()).one_or_none()
            html_text =  markdown.markdown(note.data)
    for x in notes:
        posted_notes = posted_notes + [{'name':f'{x.name}','id':f'{x.id}'}]
    return render_template('note.html', title='Note', posted_notes=posted_notes, note=note, html_text=html_text, user_id=user_id, search_form=SearchForm())


@myapp_obj.route("/download-note-as-pdf/<int:note_id>", methods=['GET', 'POST'])
@login_required
def download_note_as_pdf(note_id):
    '''Route will allow for html note to be downloaded as pdf in the md file in a pdf directory'''
    note = Note.query.filter_by(id=note_id, user_id=current_user.get_id()).one_or_none()
    if not note:
        abort(404, description=f"Note with id {note_id} doesn't exists")
    html_text = markdown.markdown(note.data)
    output_filename = note.name.split(".md")
    output_filename = output_filename[0] + '.pdf'
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_filename = os.path.join(temp_dir, output_filename)
        # Convert html to pdf
        with open(pdf_filename, "wb+") as fp:
            pisa_status = pisa.CreatePDF(html_text, dest=fp)
        return send_file(pdf_filename, as_attachment=True)


@myapp_obj.route("/upload-note", methods=['GET', 'POST'])
@login_required
def upload_note():
    """Import note route, for user to import markdown file into note"""
    form = UploadMarkdownForm()
    if form.validate_on_submit():
        n = form.file.data
        filename = n.filename
        content = n.stream.read().decode('ascii')
        note = Note(name=filename, data=content, user_id=current_user.get_id())
        db.session.add(note)
        db.session.commit()
        flash(f'Uploaded note {filename} ')
        return redirect(url_for("show_notes"))
    return render_template("import-note.html", form=form)


@myapp_obj.route("/share-notes/<int:note_id>", methods=['GET', 'POST'])
@login_required
def share_note(note_id):
    ''' route will allow user to share note to other users(friends)'''
    note = Note.query.filter_by(id=note_id).one_or_none()
    friends = []
    for status, oth_user in get_all_friends(current_user.get_id()):
        if status == 'friend':  # Only find friends
            friends.append(oth_user)
    form = NoteShareForm()
    form.dropdown.choices = [(u.id, u.username) for u in friends]
    if form.validate_on_submit():
        user = User.query.filter_by(id=form.dropdown.data).one()
        now = datetime.now()
        shared_note = SharedNote(note_id=note_id, datetime=now, owner_user_id=current_user.get_id(), target_user_id=user.id)
        db.session.add(shared_note)
        db.session.commit()
        flash(f'Shared note "{shared_note.note.name}" to "{user.username}" on {str(datetime.now())}')
        return redirect(url_for("show_notes"))
    return render_template("share-notes.html", note=note, form=form)


@myapp_obj.route("/notes-sharing", methods=['GET', 'POST'])
@login_required
def notes_sharing():
    """A route for viewing sharing status of notes (both shared to others and others shared to me)"""
    owner_notes = SharedNote.query.filter_by(owner_user_id=current_user.get_id()).all()
    target_notes = SharedNote.query.filter_by(target_user_id=current_user.get_id()).all()
    return render_template("notes-sharing.html", owner_notes=owner_notes, target_notes=target_notes)


@myapp_obj.route("/notes-sharing/add-to-mynotes/<int:sharing_id>", methods=['GET', 'POST'])
@login_required
def notes_sharing_add_to_mynotes(sharing_id):
    """A route for adding shared note that other user shared into My Notes"""
    sharing = SharedNote.query.get(sharing_id)
    if int(current_user.get_id()) != sharing.owner_user_id and\
        int(current_user.get_id()) != sharing.target_user_id:
        abort(404, description='Invalid permission')
    note = Note(name=sharing.note.name, data=sharing.note.data, user_id=current_user.get_id())
    db.session.add(note)
    db.session.commit()
    flash(f'Copied note(#{sharing.note.id}) to "My Notes", new note(#{note.id})')
    return redirect(url_for('notes_sharing'))


@myapp_obj.route("/notes-sharing/cancel-sharing/<int:sharing_id>", methods=['GET', 'POST'])
@login_required
def notes_sharing_cancel_sharing(sharing_id):
    """A route for cancelling a flashcard sharing"""
    sharing = SharedNote.query.get(sharing_id)
    if int(current_user.get_id()) != sharing.owner_user_id and\
        int(current_user.get_id()) != sharing.target_user_id:
        abort(404, description='Invalid permission')
    flash(f'Sharing of note(#{sharing.note.id}) cancelled')
    db.session.delete(sharing)
    db.session.commit()
    return redirect(url_for('notes_sharing'))
