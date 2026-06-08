from django.core.management.base import BaseCommand, CommandError
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Create the initial Super Admin user for CoWorkHub'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True, help='Super Admin email')
        parser.add_argument('--password', required=True, help='Super Admin password')
        parser.add_argument('--first-name', required=True, dest='first_name')
        parser.add_argument('--last-name', required=True, dest='last_name')
        parser.add_argument('--phone', default='', dest='phone')
        parser.add_argument(
            '--force',
            action='store_true',
            help='Create even if a Super Admin already exists',
        )

    def handle(self, *args, **options):
        if not options['force'] and User.objects.filter(role=User.SUPER_ADMIN).exists():
            raise CommandError(
                'A Super Admin already exists. Use --force to create another one.'
            )

        user = User.objects.create_user(
            email=options['email'],
            password=options['password'],
            first_name=options['first_name'],
            last_name=options['last_name'],
            phone=options['phone'],
            role=User.SUPER_ADMIN,
            is_staff=True,
            is_superuser=True,
        )

        self.stdout.write(
            self.style.SUCCESS(f'Super Admin created: {user.get_full_name()} <{user.email}>')
        )
