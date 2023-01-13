from django.contrib import admin
from .models import User, Reset, OtpCode, Follow, BookMark, BookMarkUser



class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'short_about', 'has_profile', 'short_skills', 'activated', 'user_is_admin', 'followers_count')
    ordering = ('-is_admin', 'id')

class ResetAdmin(admin.ModelAdmin):
    list_display = ('email', 'short_token', 'is_valid')
    ordering = ('id',)

class OtpCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'is_valid')
    ordering = ('id',)

class FollowAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user')

class BookMarkAdmin(admin.ModelAdmin):
    list_display = ('title', 'user')

class BookMarkUserAdmin(admin.ModelAdmin):
    list_display = ('get_bookmark', 'get_user', 'post')


admin.site.register(User, UserAdmin)
admin.site.register(Reset, ResetAdmin)
admin.site.register(OtpCode, OtpCodeAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(BookMark, BookMarkAdmin)
admin.site.register(BookMarkUser, BookMarkUserAdmin)
