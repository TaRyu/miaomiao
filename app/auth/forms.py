# coding: utf-8
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import Required, Email, Length, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    email = StringField('Email', validators=[
        Required(),
        Length(1, 64, message=u'请控制在64个字符以内！'),
        Email(message=u'请填写正确的邮箱地址！')])
    password = PasswordField(u'密码',
                             validators=[Required()])
    rember_me = BooleanField(u'自动登录')
    submit = SubmitField(u'登录')


class RegistrationForm(Form):
    email = StringField('Email', validators=[
        Required(),
        Length(1, 64, message=u'请控制在64个字符以内！'),
        Email(message=u'请填写正确的邮箱地址！')])
    username = StringField(u'用户名', validators=[Required(),
                           Length(1, 128, message=u'请控制在64个字符以内！')])
    password = PasswordField(u'密码', validators=[
        Required(),
        EqualTo('password2', message=u'与验证密码不同！')])
    password2 = PasswordField(u'验证密码',
                              validators=[Required()])
    submit = SubmitField(u'注册')

    def validate_email(self, field):
        if User.objects(email=field.data).first():
            raise ValidationError(u'该邮箱已被注册！')

    def validate_username(self, field):
        if User.objects(username=field.data).first():
            raise ValidationError(u'该用户名已经注册！')
