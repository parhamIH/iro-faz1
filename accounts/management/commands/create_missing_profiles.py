from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile

class Command(BaseCommand):
    help = 'Creates missing profiles for users who do not have one'

    def handle(self, *args, **kwargs):
        users_without_profile = User.objects.filter(profile__isnull=True)
        count = 0
        
        for user in users_without_profile:
            Profile.objects.create(user=user)
            count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {count} missing profile(s)'
            )
        ) 