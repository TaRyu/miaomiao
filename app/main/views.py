# coding: utf-8
from flask import render_template, flash, redirect, url_for, request,\
        current_app, abort, make_response
from flask.ext.login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, WriteArticleForm,\
        CommentForm
# from .. import db
from ..models import User, Role, Article, Permission, Comment
from ..decorators import admin_required, permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated():
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        objects = current_user.followed_articles
    else:
        objects = Article.objects().all()
    pagination = objects.paginate(
        page, per_page=current_app.config['MIAO_PER_PAGE'],
        error_out=False)
    articles = pagination.items
    return render_template('index.html', articles=articles,
                           count=objects.count(),
                           show_followed=show_followed, pagination=pagination)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/user/<username>')
def user(username):
    user = User.objects(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    objects = user.articles
    pagination = objects.paginate(
        page, per_page=current_app.config['MIAO_PER_PAGE'],
        error_out=False)
    articles = pagination.items
    return render_template('user.html', user=user, articles=articles,
                           pagination=pagination)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.objects(username=username).first_or_404()
    if current_user.is_following(user):
        flash(u'你正在关注该用户')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash(u'已成功关注')
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.objects(username=username).first_or_404()
    if not current_user.is_following(user):
        flash(u'你未关注该用户')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash(u'已取消关注')
    return redirect(url_for('.user', username=username))


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.gender = form.gender.data[0]
        # current_user.birthday = form.birthday.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        current_user.save()
        flash(u'信息已经被更新')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.gender.data = current_user.gender
    # form.birthday.data = current_user.birthday
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.objects.get_or_404(id=id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.bojects.get(form.role.data)
        user.name = form.name.data
        user.gender = form.gender.data
        # user.birthday = form.birthday.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        user.save()
        flash(u'信息已被修改')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role.id
    form.name.data = user.name
    form.gender.data = current_user.gender
    # form.birthday.data = current_user.birthday
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/write-article', methods=['GET', 'POST'])
@login_required
def write_article():
    form = WriteArticleForm()
    if form.validate_on_submit():
        article = Article(title=form.title.data,
                          author=current_user.id,
                          about=form.about.data,
                          body=form.body.data)
        article.save()
        flash(u'完成喵！')
        return redirect(url_for('.index'))
    return render_template('write_article.html', form=form)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def article(id):
    article = Article.objects.get_or_404(id=id)
    article.read_count += 1
    article.save()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(article_id=article.id,
                          body=form.body.data,
                          author=current_user.id)
        comment.save()
        flash(u'评论成功')
        return redirect(url_for('.article', id=article.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (article.comments.count() - 1) / \
            current_app.config['MIAO_PER_PAGE'] + 1
    pagination = article.comments.paginate(
        page, per_page=current_app.config['MIAO_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('article.html', article=article, form=form,
                           comments=comments, pagination=pagination)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    article = Article.objects.get_or_404(id=id)
    if current_user != article.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = WriteArticleForm()
    if form.validate_on_submit():
        article.title = form.title.data
        article.about = form.about.data
        article.body = form.body.data
        article.save()
        flash(u'内容以已更新')
        return redirect(url_for('.article', id=article.id))
    form.title.data = article.title
    form.about.data = article.about
    form.body.data = article.body
    return render_template('edit_article.html', form=form)


@main.route('/delete_article/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def delete_article(id):
    article = Article.objects.get_or_404(id=id)
    article.delete()
    Comment.objects(article_id=id).all().delete()
    flash(u'文章已删除')
    return redirect(url_for('.index'))


@main.route('/delete_comment/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def delete_comment(id):
    comment = Comment.objects.get_or_404(id=id)
    comment.delete()
    flash(u'评论已删除')
    return redirect(url_for('.article', id=comment.article_id))


@main.route('/followers/<username>')
def followers(username):
    user = User.objects(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page,
        per_page=current_app.config['MIAO_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower,
                'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title=u"粉丝",
                           endpoint='.followers',
                           pagination=pagination,
                           follows=follows)


@main.route('/followed/<username>')
def followed(username):
    user = User.objects(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page,
        per_page=current_app.config['MIAO_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed,
                'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title=u"关注者",
                           endpoint='.followed',
                           pagination=pagination,
                           follows=follows)
