from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

User = get_user_model()


class Category(models.Model):
    title = models.CharField('Заголовок', max_length=256)
    description = models.TextField('Описание')
    slug = models.SlugField('Идентификатор', unique=True)
    is_published = models.BooleanField('Опубликовано', default=True)
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(models.Model):
    name = models.CharField('Название', max_length=256)
    is_published = models.BooleanField('Опубликовано', default=True)
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField('Заголовок', max_length=256)
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата и время публикации', default=timezone.now
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор', related_name='posts'
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
        verbose_name='Категория'
    )
    image = models.ImageField(
        'Изображение', upload_to='posts_images/', blank=True, null=True
    )
    is_published = models.BooleanField('Опубликовано', default=True)
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.id])

    @property
    def comment_count(self):
        return self.comments.count()

    @classmethod
    def get_published_posts(cls):
        return cls.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )


class Comment(models.Model):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Публикация'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор', related_name='comments'
    )
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self):
        return f'Комментарий {self.author.username} к {self.post.title}'

    @property
    def post_id(self):
        return self.post.id
