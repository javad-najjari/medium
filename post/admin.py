from django.contrib import admin
from .models import Post



class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'short_description', 'created')


admin.site.register(Post, PostAdmin)
