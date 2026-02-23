from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.mail import send_mail


@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created:
        token = default_token_generator.make_token(instance)
        activation_url = f"{settings.FRONTEND_URL}user/activate/{instance.id}/{token}/"

        subject = "Activate your account"
        message = (
            f"Hi {instance.username},\n\n"
            f"Please activate your account by clicking the link below:\n"
            f"{activation_url}\n\n"
            f"Thank you!"
        )

        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [instance.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send activation email to {instance.email}: {e}")


@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    if created:
        user_group, _ = Group.objects.get_or_create(name='User')
        instance.groups.add(user_group)