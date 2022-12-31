from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager



class User(AbstractBaseUser):
    name = models.CharField(max_length=150, null=True, blank=True)
    family = models.CharField(max_length=150, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)
    skills = models.CharField(max_length=150, null=True)
    email = models.CharField(max_length=150, unique=True)
    profile = models.ImageField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    followers = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    objects = UserManager()

    def short_skills(self):
        if self.skills:
            return self.skills[:50]
        return None

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class Reset(models.Model):
    email = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class OtpCode(models.Model):
    email = models.CharField(max_length=255)
    code = models.CharField(max_length=10)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Follow(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_followings')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_followers')

    def __str__(self):
        return f'{self.from_user} - {self.to_user}'


class BookMark(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')

    def __str__(self):
        return f'{self.title} - {self.user}'


class BookMarkUser(models.Model):
    book_mark = models.ForeignKey(BookMark, on_delete=models.CASCADE)
    post = models.ForeignKey('post.Post', on_delete=models.CASCADE)


