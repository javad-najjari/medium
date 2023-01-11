from django.contrib import admin
from .models import Post, File



class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'short_description', 'created')
    ordering = ('id',)

class FileAdmin(admin.ModelAdmin):
    list_display = ('get_post', 'created')


admin.site.register(Post, PostAdmin)
admin.site.register(File, FileAdmin)
