from flask import flash
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, PasswordField, SubmitField, BooleanField, validators
from wtforms.fields.html5 import EmailField
from wtforms.validators import EqualTo

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

        flash(f'Post {self.title.data} Criado!')

class LoginForm(FlaskForm):
    username = StringField('Nome de Usuário')
    password = PasswordField('Senha')
    remember = BooleanField('Lembre-se')
    submit = SubmitField('Entrar')


class RegisterForm(FlaskForm):
    nome = StringField('Nome', render_kw={'placeholder': 'Digite aqui seu nome'})
    sobrenome = StringField('Sobrenome', render_kw={'placeholder': 'Digite aqui seu sobrenome'})
    mobile = StringField('Telefone', render_kw={'placeholder': 'Insira aqui seu número'})
    email = StringField('Email', render_kw={'placeholder': 'seu@email.aqui'})
    username = StringField('Nome de Usuário', render_kw={'placeholder': 'Usuário para Login'})
    password = PasswordField('Senha', render_kw={'placeholder': 'Sua Senha'})
    confirm = PasswordField("Confirmar Senha", render_kw={'placeholder': 'Confirme a Senha'})
    submit = SubmitField('Registrar')

    def to_database(self):
        from logincrud.models import User

        User(self.nome.data,
             self.sobrenome.data,
             self.username.data,
             self.password.data,
             self.mobile.data,
             self.email.data)

        flash('Cadastro Efetuado com Sucesso!')
