from django.contrib import admin
from .models import User, Reset, OtpCode, Follow, BookMark, BookMarkUser



class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'short_skills')

class ResetAdmin(admin.ModelAdmin):
    list_display = ('email', 'token')

class OtpCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'code')

class FollowAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user')

class BookMarkAdmin(admin.ModelAdmin):
    list_display = ('title', 'user')

class BookMarkUserAdmin(admin.ModelAdmin):
    list_display = ('book_mark', 'user')


admin.site.register(User, UserAdmin)
admin.site.register(Reset, ResetAdmin)
admin.site.register(OtpCode, OtpCodeAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(BookMark, BookMarkAdmin)
admin.site.register(BookMarkUser, BookMarkUserAdmin)
