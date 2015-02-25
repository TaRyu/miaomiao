# coding: utf-8
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, SelectField,\
    ValidationError, BooleanField, SelectMultipleField, FieldList, IntegerField
from wtforms.validators import Required, Length, Email
from  wtforms.widgets import ListWidget
from ..models import Role, User


class EditProfileForm(Form):
    name = StringField(u'姓名', validators=[Length(0, 64,
                       message=u'请控制在64个字符以内！')])
    gender = SelectField(u'性别',
                         choices=[(u'0', u'保密'), (u'1', u'男'), (u'2', u'女')])
    # birthday = DateField(u'出生日期')
    location = StringField(u'地区', validators=[Length(0, 64,
                           message=u'请控制在64个字符以内！')])
    about_me = TextAreaField(u'我的简介')
    submit = SubmitField(u'保存')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[
        Required(), Length(1, 64, message=u'请控制在64个字符以内！'), Email()])
    username = StringField(u'用户名', validators=[Required(), Length(1, 128,
                           message=u'请控制在128个字符以内！')])
    confirmed = BooleanField(u'激活')
    role = SelectField(u'角色', coerce=int)
    name = StringField(u'姓名', validators=[Length(0, 64,
                       message=u'请控制在64个字符以内！')])
    gender = SelectField(u'性别',
                         choices=[(u'0', u'保密'), (u'1', u'男'), (u'2', u'女')])
    # birthday = DateField(u'出生日期')
    location = StringField(u'地区', validators=[Length(0, 64,
                           message=u'请控制在64个字符以内！')])
    about_me = TextAreaField(u'我的简介')
    submit = SubmitField(u'修改')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.objects().all()]
        self.user = user

    def validate_email(self, field):
        if User.objects(email=field.data).first():
            raise ValidationError(u'该邮箱已被注册！')

    def validate_username(self, field):
        if User.objects(username=field.data).first():
            raise ValidationError(u'该用户名已经注册！')


class WriteArticleForm(Form):
    title = StringField(u'标题', validators=[Required(),
                        Length(1, 64, message=u'请控制在64个字符以内！')])
    about = StringField(u'简介', validators=[Length(0, 256,
                        message=u'请控制在256个字符以内！')])
    body = TextAreaField(u'来喵一下吧', validators=[Required()],
                         id='article-body')
    submit = SubmitField(u'提交')


class CommentForm(Form):
    body = StringField('', validators=[Required()])
    submit = SubmitField(u'提交')


class CreateCollectionForm(Form):
    name = StringField(u'合集名', validators=[Required(),
                       Length(1, 64, message=u'请控制在64个字符以内！')])
    about = StringField(u'简介', validators=[Length(0, 256,
                        message=u'请控制在256个字符以内！')])
    articles = SelectMultipleField(u'合集文章')
    hidden = SelectMultipleField(u'hidden', choices=[(0, 0)])
    submit = SubmitField(u'提交')

    def __init__(self, user, *args, **kwargs):
        super(CreateCollectionForm, self).__init__(*args, **kwargs)
        self.user = user
        self.articles.choices = [(str(article.id), article.title)
                                 for article in self.user.articles]
        self.hidden.choices = self.articles.choices
