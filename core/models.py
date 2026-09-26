from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class Profile(models.Model):
    """Do'kon egasi haqida qo'shimcha ma'lumot (do'kon nomi)."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    store_name = models.CharField('Do\'kon nomi', max_length=150, blank=True)
    login_count = models.PositiveIntegerField("Necha marta kirgan", default=0)

    def __str__(self):
        return self.store_name or self.user.username


class Customer(models.Model):
    """Qarzdor mijoz."""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers')
    first_name = models.CharField('Ismi', max_length=100)
    last_name = models.CharField('Familiyasi', max_length=100, blank=True)
    phone = models.CharField('Telefon raqami', max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def total_unpaid(self):
        return self.debts.filter(is_paid=False).aggregate(t=Sum('amount'))['t'] or 0

    @property
    def total_paid(self):
        return self.debts.filter(is_paid=True).aggregate(t=Sum('amount'))['t'] or 0

    @property
    def has_debt(self):
        return self.total_unpaid > 0


class Debt(models.Model):
    """Bitta qarz yozuvi (mijoz nima oldi va qanchaga)."""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='debts')
    description = models.CharField('Nima uchun / nima oldi', max_length=255, blank=True)
    amount = models.DecimalField('Summasi', max_digits=14, decimal_places=0)
    created_at = models.DateTimeField('Qarz sanasi', auto_now_add=True)
    is_paid = models.BooleanField('To\'landi', default=False)
    paid_at = models.DateTimeField('To\'langan sana', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer} - {self.amount}"

    def mark_paid(self):
        self.is_paid = True
        self.paid_at = timezone.now()
        self.save(update_fields=['is_paid', 'paid_at'])
