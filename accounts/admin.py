from django.contrib import admin
from .models import User, Reset, OtpCode



class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'short_skills')

class ResetAdmin(admin.ModelAdmin):
    list_display = ('email', 'token')

class OtpCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'code')


admin.site.register(User, UserAdmin)
admin.site.register(Reset, ResetAdmin)
admin.site.register(OtpCode, OtpCodeAdmin)
