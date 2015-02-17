# coding: utf-8
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import hashlib
from flask.ext.login import UserMixin, AnonymousUserMixin
from datetime import datetime
from . import db, login_manager


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Document):
    id = db.SequenceField(primary_key=True)
    name = db.StringField(max_length=64, unique=True)
    default = db.BooleanField(default=True)
    permissions = db.IntField()

    meta = {
        'indexes': ['default'],
        'collection': 'roles'
    }

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.objects(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            role.save()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Document):
    id = db.SequenceField(primary_key=True)
    email = db.EmailField(max_length=64, unique=True)
    username = db.StringField(max_length=64, unique=True)
    role = db.ReferenceField('Role')
    password_hash = db.StringField(max_length=128)
    confirmed = db.BooleanField(default=False)
    name = db.StringField(max_length=64)
    gender = db.StringField(max_length=1, default=u'0',
                            choices=(u'0', u'1', u'2'))
    birthday = db.DateTimeField()
    location = db.StringField(max_length=64)
    about_me = db.StringField()
    avatar_hash = db.StringField(max_length=32)
    member_since = db.DateTimeField(default=datetime.now())
    last_seen = db.DateTimeField(default=datetime.now())
    # followed = db.ListField(db.ReferenceField('User',
    #                         reverse_delete_rule=db.PULL))
    # followed_by = db.ListField(db.ReferenceField('User',
    #                            reverse_delete_rule=db.PULL))

    meta = {
        'indexes': ['email', 'username'],
        'collection': 'users'
    }

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['MIAO_ADMIN']:
                self.role = Role.objects(permissions=0xff).first()
            else:
                self.role = Role.objects(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        self.follow(self)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.update(set__confirmed=True)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.update(set__last_seen=datetime.now())

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def follow(self, user):
        if not self.is_following(user):
            Follow(follower=self, followed=user).save()

    def unfollow(self, user):
        if self.is_following:
            Follow.objects(follower=self, followed=user).first().delete()

    def is_following(self, user):
        return Follow.objects(follower=self, followed=user).first() is not None

    @property
    def articles(self):
        return Article.objects(author=self)

    @property
    def followed_articles(self):
        return Article.objects(author__in=[followed.followed
                               for followed in
                               Follow.objects(follower=self).all()]).all()

    @property
    def followers(self):
        return Follow.objects(follower__ne=self, followed=self).all()

    @property
    def followed(self):
        return Follow.objects(follower=self, followed__ne=self).all()

    def __repr__(self):
        return '<User %r>' % self.username


class Follow(db.Document):
    id = db.SequenceField(primary_key=True)
    follower = db.ReferenceField('User', reverse_delete_rule=db.NULLIFY)
    followed = db.ReferenceField('User', reverse_delete_rule=db.NULLIFY)
    timestamp = db.DateTimeField(default=datetime.now)

    meta = {
        'indexes': ['-timestamp', 'follower', 'followed'],
        'ordering': ['-timestamp'],
        'collection': 'follows'
    }


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.objects.get(id=int(user_id))


class Article(db.Document):
    id = db.SequenceField(primary_key=True)
    title = db.StringField(max_length=64)
    author = db.ReferenceField('User')
    about = db.StringField(max_length=256)
    tag = db.ListField(db.StringField(max_length=16))
    level = db.IntField(default=0)
    belong = db.StringField(max_length=16)
    body = db.StringField(max_length=20000)
    # comments_id = db.ListField(db.ReferenceField('Comment'))
    timestamp = db.DateTimeField(default=datetime.now())
    required_login = db.BooleanField(default=False)

    meta = {
        'indexes': ['-timestamp', 'title'],
        'ordering': ['-timestamp'],
        'collection': 'articles'
    }

    @property
    def comments(self):
        return Comment.objects(article_id=self.id).all()

    def __repr__(self):
        return '<Article %r>' % self.title


class Comment(db.Document):
    id = db.SequenceField(primary_key=True)
    article_id = db.IntField()
    body = db.StringField(max_length=2048)
    author = db.ReferenceField('User')
    timestamp = db.DateTimeField(default=datetime.now())

    meta = {
        'indexes': ['-timestamp', 'article_id'],
        'ordering': ['-timestamp'],
        'collection': 'comments'
    }
