# coding: utf-8
import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SSL_DISABLE = True
    MAIL_SERVER = 'smtp-mail.outlook.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MIAO_MAIL_SUBJECT_PREFIX = u'喵说[Admin]'
    MIAO_MAIL_SENDER = 'miaosay Admin <miaosay@outlook.com>'
    MIAO_PER_PAGE = 20

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MIAO_ADMIN = 'admin@mail.com'
    MONGODB_DB = 'dev-miao'


class TestingConfig(Config):
    TESTING = True
    MONGODB_DB = 'test-miao'


class ProductionConfig(Config):
    MIAO_ADMIN = os.environ.get('MIAO_ADMIN')
    MONGODB_DB = 'miaosay'
    MONGODB_HOST = 'ds045011.mongolab.com'
    MONGODB_PORT = 45011
    MONGODB_USERNAME = 'miaomiao'
    MONGODB_PASSWORD = os.environ.get('DB_PASSWORD')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.MIAO_MAIL_SENDER,
            toaddrs=[cls.MIAO_ADMIN],
            subject=cls.MIAO_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


class HerokuConfig(ProductionConfig):
    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # handle proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,

    'default': DevelopmentConfig
}
