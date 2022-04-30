"""This modules holds a list of `Class` that each representing the database table/model.

The standard convention of defining a table here is:

```python
class MyTable(db.Model):
    # Table Columns/Relationships here
```

More detailed flask-sqlalchemy documentations can be found [here](https://flask-sqlalchemy.palletsprojects.com/en/2.x/).
More detailed sqlalchemy documentations can be found [here](https://www.sqlalchemy.org).

"""
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for
from flask_login import UserMixin

from myapp import login, db

from myapp.models_enum import FriendStatusEnum

basedir = os.path.abspath(os.path.dirname(__file__))

class Friend(db.Model):
    """Database table representing friend status
    This table only save relationship between two user, and whether
    their friend status is pending/friend. If they are neither,
    their user_id won't show up in pair in this database.

    When a user adds one person as friend, it will be marked as pending,
    user1 below is always the one that sent the friend request, and user2
    would be the one accepting/rejecting it. Once accepted, their friend
    status becomes 'FRIEND'

    Attributes:
        id: Primary key
        user1_id: Integer column, the sender of friend request
        user2_id: Integer column, the receiver of friend request
        status: Indicate whether friend request is still "PENDING" or already a "FRIEND"
    """
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Enum(FriendStatusEnum))


def _get_default_avatar():
    default_cat_img = os.path.join(basedir, './static/images/clipart722180.png')
    assert os.path.exists(default_cat_img), f'"{default_cat_img}" does not exists'
    with open(default_cat_img, 'rb') as fp:
        return fp.read()

class User(UserMixin, db.Model):
    """Database table holding main user data, and hold relationships to other tables

    Attributes:
        id: Primary key
        email: String column, hold email of user, this has to be unique
        username: String column, hold username of user, this has to be unique
        password: Hashed password of user
        avatar: Avatar image blob of user, default will be chosen if not defined
        flashcards: Relationship that points to all flashcards of this user
        friends1: Relationship that points to Friend table's user1
        friends2: Relationship that points to Friend table's user2
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))
    avatar = db.Column(db.LargeBinary, default=_get_default_avatar())
    flashcards = db.relationship('FlashCard', backref='user', lazy='dynamic')
    notes = db.relationship('Note', backref='user', lazy='dynamic')
    friends1 = db.relationship('Friend', backref='user1' , lazy='dynamic', foreign_keys=[Friend.user1_id])
    friends2 = db.relationship('Friend', backref='user2' , lazy='dynamic', foreign_keys=[Friend.user2_id])

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.id}: {self.username}, {self.password}>'


class Todo(db.Model):
    """Saves ToDo lists of users

    Attributes:
        id: Primary key
        title: String column, save the title of things to do
        complete: Boolean column, mark whether that item is completed
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class FlashCard(db.Model):
    """Saves FlashCards of users

    Attributes:
        id: Primary key
        front: String column, Front page text
        back: String column, Back page text
        learned: Integer column, track how many times user learned this card
        user_id: id of owner user of this flashcard
        sharings: relationship to a all sharing information of this flashcard
    """
    id = db.Column(db.Integer, primary_key=True)
    front = db.Column(db.Text)
    back = db.Column(db.Text)
    view = db.Column(db.Integer)
    learned = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sharings = db.relationship('SharedFlashCard', backref='flashcard', cascade='all, delete')

    def __repr__(self):
        return f'<FlashCard {self.id}: {self.front}, {self.back}>'


class SharedFlashCard(db.Model):
    """Saves sharing information of flashcards

    Attributes:
        id: Primary key
        datetime: Datetime column, time of sharing
        flashcard_id: Integer column, id of flashcard that is shared
        owner_user_id: Integer column, id of person sharing the card
        target_user_id: Integer column, id of person that was shared with the card
    """
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime)
    flashcard_id = db.Column(db.Integer, db.ForeignKey('flash_card.id'))
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    target_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner_user = db.relationship('User', foreign_keys=[owner_user_id])
    target_user = db.relationship('User', foreign_keys=[target_user_id])


class Note(db.Model):
    """Database table for notes

     Attributes:
         id: Primary key
         name: String column, title of note
         data: text column, containing files data
         User: id if user who added notes
     """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    data = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sharings = db.relationship('SharedNote', backref='note', cascade='all, delete')
    def __repr__(self):
        return f'<{self.name}   {self.data}>'


class SharedNote(db.Model):
    """Saves sharing information of notes

    Attributes:
        id: Primary key
        datetime: Datetime column, time of sharing
        note_id: Integer column, id of note that is shared
        owner_user_id: Integer column, id of person sharing the note
        target_user_id: Integer column, id of person that was shared with the note
    """
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'))
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    target_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner_user = db.relationship('User', foreign_keys=[owner_user_id])
    target_user = db.relationship('User', foreign_keys=[target_user_id])