from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import Profile


@receiver(user_logged_in)
def count_login(sender, request, user, **kwargs):
    """Har safar tizimga kirganda shu foydalanuvchining kirishlar sonini +1 qiladi.
    Bu ma'lumot admin panelda "Necha marta kirgan" ustunida ko'rinadi."""
    profile, _ = Profile.objects.get_or_create(user=user)
    Profile.objects.filter(pk=profile.pk).update(login_count=profile.login_count + 1)
