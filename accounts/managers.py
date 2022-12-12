from django.contrib.auth.models import BaseUserManager



class UserManager(BaseUserManager):
    def create_user(self, username, email, password):
        if not (username and email):
            raise ValueError('username and email must set')

        user = self.model(
            username=username, email=email
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

