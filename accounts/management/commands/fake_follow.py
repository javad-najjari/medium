import random, os
from accounts.models import User, Follow
from django.core.management.base import BaseCommand



class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.all()
        users = [user for user in users]

        for user in users:
            rand = random.randint(1, 50)
            new_users = random.sample(users, rand)

            print(f'Following: {user.name}({user.id}) -> {rand}')
            for new_user in new_users:
                Follow.objects.create(from_user=user, to_user=new_user)
        

        # wrong follows

        follows = Follow.objects.all()
        follows = [follow for follow in follows]
        count = len(follows)
        i = 0
        x = 1

        for follow in follows:
            os.system('clear')
            print(f'removing follow(1/2): {x}/{count}')
            if follow.from_user == follow.to_user:
                follow.delete()
                i += 1
            x += 1

        # delete duplicate follows

        follows = Follow.objects.all()
        follows = [follow for follow in follows]
        x = 1

        for follow in follows:
            os.system('clear')
            print(f'removing follow(2/2): {x}/{count}')
            if len(Follow.objects.filter(from_user=follow.from_user, to_user=follow.to_user)) > 1:
                follow.delete()
                i += 1
            x += 1
        print(f'{i} item removed')

