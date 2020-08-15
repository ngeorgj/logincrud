from logincrud.models import BlogPost, User

BlogPosts = BlogPost.query.all()
Users = User.query.all()