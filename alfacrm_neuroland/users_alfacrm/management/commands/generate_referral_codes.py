import random
import string

from django.core.management.base import BaseCommand

from users_alfacrm.models import AlfaCRMUser


class Command(BaseCommand):
    help = "Generate referral codes for existing users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--length", type=int, default=10, help="Length of referral code"
        )

    def handle(self, *args, **options):
        length = options["length"]
        users = AlfaCRMUser.objects.all()

        for user in users:
            if not user.referral_code:
                user.referral_code = "".join(
                    random.choices(
                        string.ascii_uppercase + string.digits, k=length
                    )
                )
                user.save()

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully generated referral codes for existing users."
            )
        )
