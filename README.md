# Sistema em Flask com Login e CRUD
O sistema tem as seguintes funcionalidades:
- Registro, Login, Logout;
- Criação, Visualização, Edição e Remoção de Postagens (CRUD);
- Pesquisa de Post por #tag

A aplicação foi feita de maneira <b>simplificada</b>, em apenas um arquivo, sem <a href="https://flask.palletsprojects.com/en/1.1.x/blueprints/">blueprints</a> pois se trata de um projeto demonstrativo.

A encriptação das senhas é feita por meio da biblioteca de hash `Argon2`.<br>
Publiquei um tutorial sobre esse sistema de criptografia aqui: <a href="https://github.com/ngeorgj/Argon2-ex">ngeorgj/Argon2-ex</a>.

Modelos do Banco de Dados (SQLite3) constando no arquivo `models.py`:

```python
class User(db.Model, CRUDMixin, SurrogatePK, UserMixin):
    nome = db.Column(db.String)
    sobrenome = db.Column(db.String)

    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)

    mobile = db.Column(db.String)
    email = db.Column(db.String, unique=True)

    register_date = db.Column(db.DateTime)

    def __init__(self, nome, sobrenome, username, password, mobile, email):
        # Construtor da classe, realiza o hash da senha no momento do
        # cadastro com criptografia Argon2.

        self.nome = nome
        self.sobrenome = sobrenome
        self.username = username
        self.password = ph.hash(password)  # << Argon2
        self.mobile = mobile
        self.email = email
        self.register_date = datetime.now()  # .strftime("%d/%m/%y às %H:%M")

        self.save()

    @property
    def nome_completo(self):
        return f'{self.nome} {self.sobrenome}'

    @property
    def greetings(self):
        return f'Olá, {self.nome}!'

    @property
    def post_count(self):
        return len(self.posts)

    @property
    def posts(self):
        return BlogPost.query.filter_by(author_id=self.id).all()


class BlogPost(db.Model, CRUDMixin, SurrogatePK):
    __tablename__ = "blogpost"
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime)
    tags_string = db.Column(db.String)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, author_id, tags_string):
        self.title = title
        self.content = content
        self.author_id = author_id
        self.tags_string = tags_string
        self.date_posted = datetime.now()
        self.save()

    @property
    def author(self):
        return User.query.filter_by(id=self.author_id).first().nome_completo

    @property
    def author_username(self):
        return User.query.filter_by(id=self.author_id).first().username

    @property
    def timestamp(self):
        return self.date_posted.strftime("%d/%m/%y às %H:%M")

    @property
    def tags(self):
        tags = self.tags_string.replace(' ', "")
        tags = tags.split(',')

        lst = []
        for tag in tags:
            lst.append(f'#{tag}')
        return lst

    def __repr__(self):
        return f'Post: {self.title}.'

```

# Tecnologias Empregadas

O projeto utilizou as seguintes técnologias/libraries.

<ul>
	<li>Python 3.8</li>
  	<li>SQLite3</li>
	<li>Jinja Templates</li>
	<li>Flask</li>
	<li>Flask-Login</li>
	<li>Flask-SQLAlchemy</li>	
	<li>WTForms</li>
	<li>Argon2</li>
	<li>Bootstrap 4.4 [HTML5 + CSS3]</li>
</ul>

# Forms

Formulários feitos usando Flask-WTF com funções `to_database()` que registram os dados assim que o formulário é validado.
```python
# PS: Importações sendo feitas localmente em algumas views.
class PostForm(FlaskForm):
    title = StringField('Titulo', render_kw={'placeholder': 'Dê um titulo legal ao seu post!'})
    content = TextAreaField('Conteúdo', render_kw={'placeholder': 'Conteúdo da Postagem'})
    tags = StringField('Tags', render_kw={'placeholder': 'Separadas por virgulas.'})
    submit = SubmitField('Postar')

    def to_database(self):
        from logincrud.models import BlogPost

        BlogPost(self.title.data,
                 self.content.data,
                 current_user.id,
                 self.tags.data)
```

# As Views 
- /
- /Registrar
- /Login
- /Blog
- /Blog/User
- /Blog/Post/Edit/post_id
- /Blog/Post/Delete/post_id
 
# Busca por Tags
Adicionado uma função de busca de posts por meio de `#tags`:
```python
@app.route('/Blog/Posts/ByTag/<tag>', methods=['GET'])
def search_by_tag(tag):
    all_posts = [post for post in BlogPost.query.all() if tag in post.tags ]  # List Comprehension
    return render_template('searchbytag.html', posts=all_posts, tag=tag)
```


por <b>@ngeorgj</b> em 15/08/2020
