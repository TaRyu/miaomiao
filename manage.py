# coding: utf-8
# !/usr/bin/env python
import os
from app import create_app, db
from app.models import Role, Permission, User, Article
from flask.ext.script import Manager, Shell

app = create_app(os.getenv('MIAO_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, Role=Role, Permission=Permission,
                User=User, Article=Article)
manager.add_command('shell', Shell(make_context=make_shell_context))


if __name__ == '__main__':
    manager.run()
