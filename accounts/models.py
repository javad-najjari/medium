from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager
from django.utils import timezone
import utils



class User(AbstractBaseUser):
    name = models.CharField(max_length=150, null=True, blank=True)
    family = models.CharField(max_length=150, null=True, blank=True)
    username = models.CharField(max_length=150, unique=True)
    skills = models.CharField(max_length=150, null=True)
    email = models.CharField(max_length=150, unique=True)
    profile = models.ImageField(upload_to='profile', null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    objects = UserManager()

    def short_skills(self):
        if self.skills:
            if len(self.skills) > 30:
                return self.skills[:30] + ' ...'
            return self.skills
        return None
    short_skills.short_description = 'skills'

    def has_profile(self):
        if self.profile:
            return True
        return False
    has_profile.boolean = True
    has_profile.short_description = 'profile'

    def short_about(self):
        if self.about:
            if len(self.about) > 30:
                return self.about[:30] + ' ...'
            return self.about
        return None
    short_about.short_description = 'about'

    def user_is_admin(self):
        if self.is_admin:
            return True
        return False
    user_is_admin.boolean = True
    user_is_admin.short_description = 'admin'

    def activated(self):
        if self.is_active:
            return True
        return False
    activated.boolean = True
    activated.short_description = 'active'

    def followers_count(self):
        return self.user_followers.count()
    followers_count.short_description = 'followers'

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class OtpCode(models.Model):
    email = models.CharField(max_length=255)
    code = models.CharField(max_length=10)
    created = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        elapsed_time = timezone.now() - self.created
        if elapsed_time.seconds > utils.OTP_CODE_VALID_SECONDS:
            return False
        return True
    is_valid.boolean = True
    is_valid.short_description = 'valid'

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
        return f'{self.title} -> {self.user}'


class BookMarkUser(models.Model):
    book_mark = models.ForeignKey(BookMark, on_delete=models.CASCADE)
    post = models.ForeignKey('post.Post', on_delete=models.CASCADE)

    def get_bookmark(self):
        return self.book_mark.title
    get_bookmark.short_description = 'bookmark'

    def get_user(self):
        return self.book_mark.user
    get_user.short_description = 'user'


