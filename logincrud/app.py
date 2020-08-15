from flask import Flask, render_template, request, redirect, flash
from flask_login import login_user, LoginManager, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy

from logincrud.forms import LoginForm, RegisterForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + 'database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'th1s_k4y_sh0uld_be_53cr3t'
login_manager = LoginManager(app)

db = SQLAlchemy(app)


@login_manager.user_loader
def user_loader(user_id):
    from logincrud.models import User
    return User.query.get(user_id)


@app.route('/Registrar', methods=['POST', 'GET'])
def registrar():
    form = RegisterForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            if form.password.data != form.confirm.data:
                flash('Senhas precisam ser Iguais!')
            form.to_database()
            return redirect('/Login')

        else:
            flash('Há algo errado com as informações...')
            return redirect('/Registrar')

    else:
        bg_color = '#1b262c'
        return render_template('/registrar.html',
                               form=form,
                               bg_color=bg_color)


@app.route('/', methods=['POST', 'GET'])
@app.route('/Login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/Blog')

    from logincrud.models import User, ph
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            try:
                if user and ph.verify(user.password, form.password.data) == True:
                    login_user(user)
                    return redirect(f'/Blog/{current_user.username}')
                else:
                    flash("Usuário não cadastrado!")
                    return redirect('/Registrar')
            except:
                flash('A senha não coincide com a senha cadastrada.')

        else:
            flash('Verificar Informações!')
            return redirect('/Login')

    return render_template('login.html',
                           form=form,
                           bg_color='#1b262c')


@app.route('/Logout')
def logout():
    try:
        if current_user.is_authenticated:
            logout_user()
            return redirect('/Login')
        else:
            return redirect('/Login')
    except:
        return redirect('/')


@app.route('/Admin')  # Acesso de administrador a todos os posts e todos os usuários
def admin():
    from logincrud.utils import BlogPosts, Users
    _posts = BlogPosts
    _users = Users
    return render_template('admin.html',
                           users=_users,
                           posts=_posts)


@app.route('/Blog/<username>/', methods=['GET', 'POST'])
def profile(username):
    from logincrud.models import User
    user = User.query.filter_by(username=username).first()
    return render_template('profile.html',
                           user=user,
                           user_posts=user.posts[::-1])


@app.route('/Blog', methods=['GET', 'POST'])
def posts():
    from logincrud.utils import BlogPosts, Users
    all_posts = BlogPosts[::-1]

    return render_template('posts.html',
                           posts=all_posts,
                           users=Users)


@app.route('/Blog/Posts/ByTag/<tag>', methods=['GET'])
def search_by_tag(tag):
    from logincrud.models import BlogPost
    all_posts = [post for post in BlogPost.query.all() if tag in post.tags]
    return render_template('searchbytag.html', posts=all_posts, tag=tag)


@app.route('/Blog/Post/New', methods=['GET', 'POST'])
def new_post():
    from logincrud.forms import PostForm
    form = PostForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            form.to_database()
            flash(f'Post ({form.title.data}) Criado!')
            return redirect(f'/Blog/{current_user.username}')
        return redirect('/posts')

    return render_template('new-post.html', form=form)


@app.route('/Blog/Post/<int:id>')
def post(id):
    from logincrud.models import BlogPost
    _post = BlogPost.query.filter_by(id=id).first()
    return render_template('post.html',
                           post=_post)


@app.route('/Blog/Post/Delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    from logincrud.models import BlogPost
    _post = BlogPost.query.get_or_404(id)
    flash(f'Post ({_post.content}) Deletado.')
    _post.delete()
    return redirect(f'/Blog/{current_user.username}')


@app.route('/Blog/Post/Edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    from logincrud.models import BlogPost
    post = BlogPost.query.get_or_404(id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.tags_string = request.form['tags']
        post.save()
        return redirect(f'/Blog/{current_user.username}')

    elif request.method == 'GET':
        return render_template('edit-post.html',
                               post=post)

    return redirect('/posts')


if __name__ == '__main__':
    app.run(debug=True, port=5003)
