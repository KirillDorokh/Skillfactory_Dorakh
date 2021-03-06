
from django.db import models
from django.contrib.auth.models import User

from django.core.cache import cache

#для перевода
from django.utils.translation import gettext as _
from django.utils.translation import pgettext_lazy


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    rating_of_author = models.IntegerField(default=0)


    def update_rating(self):
        posts = Post.objects.filter(author=self.id)
        post_raiting = sum([r.rating_of_post * 3 for r in posts])
        comments = Comment.objects.filter(user=self.id)
        comment_raiting = sum([c.rating_of_comment for c in comments])
        all_to_post_comment_raiting = sum([r.rating_of_comment for r in Comment.objects.filter(post__in=posts)])
        self.rating_of_author = post_raiting + comment_raiting + all_to_post_comment_raiting
        self.save()

    def __str__(self):
        author_id = str(self.user.username)
        return author_id


class Category(models.Model):

    subscribers = models.ManyToManyField(User, through='CategoryUser')
    name = models.CharField(max_length=255, unique=True, help_text=_('category name'))

    def __str__(self):
        return self.name


class Post(models.Model):
    news = "NW"
    article = "AR"
    CAT = [(news, "Новость"), (article, 'Статья')]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    art_or_nw = models.CharField(max_length=2,
                            choices=CAT,
                            default=news)
    post_time = models.DateTimeField(auto_now_add=True)
    headline = models.CharField(max_length=255)
    content = models.TextField()
    rating_of_post = models.IntegerField(default=0)

    categories = models.ManyToManyField(Category)

    @property
    def on_top(self):
        return self.rating_of_post > 0

    def __str__(self):
        return self.headline

    def like(self):
        self.rating_of_post = self.rating_of_post + 1
        self.save()

    def dislike(self):
        self.rating_of_post = self.rating_of_post - 1
        self.save()

    def preview(self):
        return self.content[:123] + "..."

    def get_absolute_url(self):  # добавим абсолютный путь, чтобы после создания нас перебрасывало на страницу с товаром
        return f'/news/{self.id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'post-{self.pk}')  # затем удаляем его из кэша, чтобы сбросить его


class CategoryUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    comment_text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    rating_of_comment = models.IntegerField(default = 0)

    def like(self):
        self.rating_of_comment = self.rating_of_comment + 1
        self.save()

    def dislike(self):
        self.rating_of_comment = self.rating_of_comment - 1
        self.save()

    def __str__(self):
        return self.comment_text


class MyModel(models.Model):
    name = models.CharField(max_length=100)
    kind = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='kinds',
        verbose_name=pgettext_lazy('help text for MyModel model', 'This is the help text'),
    )