import itertools
from slugify import slugify as external_slugify

from django.db import models
from django.conf import settings
from taggit.managers import TaggableManager
from django.utils import timezone
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation


from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = external_slugify(self.name)
        super().save(*args, **kwargs)


class Post(models.Model):
    '''Модель поста'''

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField()
    image = models.ImageField(
        upload_to='posts/%Y/%m/%d/', blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='posts'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='posts'
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='draft'
    )
    tags = TaggableManager(blank=True)
    likes = GenericRelation('likes.Like', related_query_name='post')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'posts'
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-published_at', '-created_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['author', 'status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Генерація slug
        if not self.slug:
            self.slug = self._generate_unique_slug()

        # Автоматична дата публікації
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        elif self.status == 'draft':
            self.published_at = None  # Скидаємо дату при зміні на чернетку

        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        """Генерація унікального slug з урахуванням race conditions"""
        base_slug = external_slugify(self.title)
        if not base_slug:
            base_slug = f"post-{self.pk}"
        slug = base_slug

        for i in itertools.count(1):
            qs = self.__class__.objects.filter(slug=slug)
            if self.pk:
                qs = qs.exclude(pk=self.pk)

            if not qs.exists():
                return slug
            slug = f"{base_slug}-{i}"

    def increment_views(self):
        """Збільшення лічильника переглядів без тригера save()"""
        Post.objects.filter(pk=self.pk).update(
            views_count=models.F('views_count') + 1
        )
        self.views_count += 1  # Оновлюємо локальний екземпляр

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'slug': self.slug})

    @property
    def is_published(self):
        """Чи опублікований пост"""
        return self.status == 'published' and self.published_at is not None

    @property
    def likes_count(self):
        """Кількість лайків"""
        return self.likes.count()

    def is_liked_by(self, user):
        """Чи лайкнув користувач цей пост"""
        if not user.is_authenticated:
            return False
        return self.likes.filter(user=user).exists()


class PostImages(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='images')
    image = models.ImageField(upload_to='posts/%Y/%m/%d/extra/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'post_images'
        verbose_name = 'Post_ Image'
        verbose_name_plural = 'Post Images'
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['post', 'order']),
        ]

    def __str__(self):
        return f"Image for {self.post.title}"


class PostVideo(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='posts/%Y/%m/%d/videos/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'post_videos'
        verbose_name = 'Post Video'
        verbose_name_plural = 'Post Videos'
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['post', 'order']),
        ]

    def __str__(self):
        return f"Video for {self.post.title}"
