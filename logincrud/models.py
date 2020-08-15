from datetime import datetime
from flask_login import UserMixin, current_user
from argon2 import PasswordHasher

from logincrud.app import db

ph = PasswordHasher()

class SurrogatePK(object):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, record_id):
        """Get record by ID."""
        if any(
                (isinstance(record_id, (str, bytes)) and record_id.isdigit(),
                 isinstance(record_id, (int, float))),
        ):
            return cls.query.get(int(record_id))
        return None

    @classmethod
    def find(cls, record_id):
        """Alias for get_by_id."""
        return cls.get_by_id(record_id)


class CRUDMixin(object):

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()


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
    def data_registro(self):
        return self.register_date.strftime("%d/%m/%y às %H:%M")

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
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
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
            lst.append(f'{tag}')
        return lst

    def __repr__(self):
        return f'Post: {self.title}.'




