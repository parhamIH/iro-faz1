from django.core.management.base import BaseCommand
from accounts.services import cleanup_expired_tokens


class Command(BaseCommand):
    help = 'Clean up expired device tokens'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned up without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        try:
            if dry_run:
                # In dry run mode, just count expired tokens
                from django.utils import timezone
                from accounts.models import DeviceToken
                
                expired_count = DeviceToken.objects.filter(
                    expires_at__lt=timezone.now(),
                    is_active=True
                ).count()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Found {expired_count} expired tokens that would be cleaned up'
                    )
                )
            else:
                # Actually clean up expired tokens
                cleaned_count = cleanup_expired_tokens()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully cleaned up {cleaned_count} expired tokens'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error cleaning up expired tokens: {str(e)}')
            ) 