from django.db import models
from django.contrib.auth import get_user_model



User = get_user_model()

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    body = models.TextField()
    tags = models.CharField(max_length=500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    seo_title = models.CharField(max_length=255, null=True, blank=True)
    seo_description = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.title[:30]}'
    
    def short_description(self):
        return self.description[:30]


class File(models.Model):
    file = models.FileField(upload_to='post')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='files')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)
    
    def get_post(self):
        return self.post.title

