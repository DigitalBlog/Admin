import os
from flask import Flask, redirect
from flask_babel import Babel
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib import sqla
from flask_admin.menu import MenuLink
from flask_login import UserMixin, current_user, LoginManager
from datetime import datetime
from time import time

def get_locale():
        return 'ru'

app=Flask(__name__)
babel = Babel(app, locale_selector=get_locale,)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ADMIN_SWATCH'] = "lumen"

db = SQLAlchemy(app)
admin = Admin(app, name='DigitalBlog', template_mode='bootstrap4')
login = LoginManager(app)

@app.route('/')
def index():
    return 'DigitalBlog Admin'

class Followers(db.Model):
    __tablename__ = 'followers'
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

class PostView(db.Model):
    __tablename__ = 'post_views'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)

class PostFavourites(db.Model):
    __tablename__ = 'post_favourites'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)

class Stuff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    content = db.Column(db.String)

class CommentLikes(db.Model):
    __tablename__ = 'comment_likes'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), primary_key=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True, unique=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, index=True, unique=True)
    password = db.Column(db.String)
    avatar_url=db.Column(db.String, default="static/default.png")
    stroage_used=db.Column(db.Integer, default=0)
    stroage_granted=db.Column(db.Integer)
    sub_id=db.Column(db.SmallInteger, default=0)
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade = "all,delete")
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade = "all,delete")
    about_me = db.Column(db.String)
    message_setting = db.Column(db.SmallInteger, default=0)
    role = db.Column(db.SmallInteger)
    confirmed = db.Column(db.Boolean, default=False)
    banned = db.Column(db.Boolean, default=False)
    banned_reason = db.Column(db.String, default="")
    blogger = db.Column(db.Boolean, default=False)
    member_since = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    email_notify = db.Column(db.Boolean, default=True)
    show_profile_id = db.Column(db.SmallInteger, default=0)
    anonymous_show = db.Column(db.Boolean, default=True)
    viewed_posts = db.relationship(
        'PostView',
        foreign_keys='PostView.user_id',
        backref='user', lazy='dynamic',cascade = "all,delete")
    liked_comments = db.relationship(
        'CommentLikes',
        foreign_keys='CommentLikes.user_id',
        backref='user', lazy='dynamic', cascade = "all,delete")
    favourited_posts = db.relationship(
        'PostFavourites',
        foreign_keys='PostFavourites.user_id',
        backref='user', lazy='dynamic', cascade = "all,delete")
    notifies = db.relationship(
        'Notify',
        foreign_keys='Notify.recipient_id',
        backref='user', lazy='dynamic', cascade = "all,delete")
    followed = db.relationship('Followers',
                                    foreign_keys='Followers.follower_id',
                                    backref='follower', lazy='dynamic', cascade = "all,delete")
    followers = db.relationship('Followers',
                                    foreign_keys='Followers.followed_id',
                                    backref='followed', lazy='dynamic', cascade = "all,delete")
    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic', cascade = "all,delete")
    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient', lazy='dynamic', cascade = "all,delete")
    last_message_read_time = db.Column(db.DateTime, default=datetime.utcnow)
    last_notify_read_time = db.Column(db.DateTime, default=datetime.utcnow)
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade = "all,delete")

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login.user_loader
def load_user(email):
    return User.query.filter_by(email=email).first()

class Notify(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String)
    body = db.Column(db.String)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Notify {}>'.format(self.title)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    body = db.Column(db.String)
    timestamp = db.Column(db.DateTime, index=True)
    last_update_time = db.Column(db.DateTime, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    filename=db.Column(db.String)
    anonymous_show=db.Column(db.Boolean, default=False)
    file_size=db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade = "all,delete")
    views_count = db.Column(db.Integer, default=0)
    views = db.relationship('PostView', backref='post', lazy='dynamic', cascade = "all,delete")
    rate_count = db.Column(db.Integer, default=0)
    show=db.Column(db.Boolean, default=False)
    allow_comments=db.Column(db.Boolean, default=True)
    favourites_count = db.Column(db.Integer, default=0)
    description = db.Column(db.String)
    favourites = db.relationship('PostFavourites', backref='post', lazy='dynamic', cascade = "all,delete")

    def __repr__(self):
        return '<Post {}>'.format(self.title)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String)
    read = db.Column(db.Boolean, default=False)
    read_time = db.Column(db.DateTime)
    body = db.Column(db.String)
    filename = db.Column(db.String)
    file_size=db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, index=True)
    last_update_time = db.Column(db.DateTime, index=True)

    def __repr__(self):
        return '<Message {}>'.format(self.title)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.String)

    def get_data(self):
        return json.loads(str(self.payload_json))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)
    commented_on = db.Column(db.Integer, db.ForeignKey('post.id'))
    commented_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True)
    last_update_time = db.Column(db.DateTime, index=True)
    likes_count = db.Column(db.Integer, default=0)
    likes = db.relationship('CommentLikes', backref='comment', lazy='dynamic', cascade = "all,delete")

class UserView(sqla.ModelView):
    def __init__(self, model, session, name, category=None, column_filters=[], column_searchable_list=[], create_modal = True, edit_modal = True, can_export = True, can_view_details = True, page_size = 10):
        self.column_filters = column_filters
        self.column_searchable_list = column_searchable_list
        self.column_editable_list= column_filters
        self.create_modal = create_modal
        self.edit_modal = edit_modal
        self.can_export = can_export
        self.can_view_details = can_view_details
        self.page_size = page_size
        super(UserView, self).__init__(model, session, name=name, category=category)

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.role==4
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect('https://digitalblog.repl.co/auth/login')

admin.add_view(UserView(User, db.session, name="Пользователи", column_filters=['username', 'first_name', 'last_name', 'email', 'role', 'banned', 'password', 'avatar_url', 'stroage_used', 'stroage_granted', 'sub_id', 'about_me', 'message_setting', 'role', 'confirmed', 'banned', 'banned_reason', 'blogger', 'member_since', 'last_seen', 'last_message_read_time', 'email_notify', 'show_profile_id', 'anonymous_show', "last_notify_read_time"], column_searchable_list=['id', 'username', 'email']))
admin.add_view(UserView(Post, db.session, name="Публикации", column_filters=['title', 'body', 'timestamp', 'last_update_time', 'filename', 'file_size', 'views_count', 'rate_count', 'show', 'allow_comments', 'favourites_count', 'author', 'anonymous_show'], column_searchable_list=['id', 'title', 'body']))
admin.add_view(UserView(Message, db.session, name="Личные сообщения", column_filters=['title', 'body', 'timestamp', 'last_update_time', 'filename', 'file_size', 'read', 'author', 'recipient', 'read_time'], column_searchable_list=['id', 'title', 'body']))
admin.add_view(UserView(Notify, db.session, name="Уведомления", column_filters=['title', 'body', 'timestamp', 'user'], column_searchable_list=['id', 'title', 'body']))
admin.add_view(UserView(Comment, db.session, name="Комментарии", column_filters=['comment', 'timestamp', 'last_update_time', 'likes_count', 'author', 'post'], column_searchable_list=['id', 'comment']))
admin.add_view(UserView(Stuff, db.session, name="Дополнительно", column_filters=["name", "content"]))
admin.add_view(UserView(Notification, db.session, name="Счётчик уведомлений", category="Служебные"))
admin.add_view(UserView(PostFavourites, db.session, name="Избранные", category="Служебные"))
admin.add_view(UserView(PostView, db.session, name="Просмотры публикаций", category="Служебные"))
admin.add_view(UserView(Followers, db.session, name="Подписки", category="Служебные"))
admin.add_view(UserView(CommentLikes, db.session, name="Лайки комментариев", category="Служебные"))
admin.add_link(MenuLink(name='Сайт', category='', url='https://digitalblog.repl.co/'))

app.run(host='0.0.0.0')