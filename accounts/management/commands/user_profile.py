from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from accounts.models import User
import random, os



class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.all()
        users = [user for user in users]
        images = os.listdir('/home/javad/Desktop/image/')
        rand = random.sample(list(range(0, 733)), 130)
        count = len(users)
        i = 1

        for user in users:
            print(f'profile photo: {i} / {count}')
            if user.id % 10 != 0:
                directory = f'/home/javad/Desktop/image/{images[rand[i-1]]}'

                with open(directory,'rb') as f:
                        data = f.read()

                user.profile.save(images[rand[i-1]], ContentFile(data))
            i += 1

