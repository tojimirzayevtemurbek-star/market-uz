from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Count, Q, Sum
from django.utils.html import format_html

from .admin_site import admin_site
from .models import Customer, Debt, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profil"
    fields = ('store_name', 'login_count')
    readonly_fields = ('login_count',)


@admin.register(User, site=admin_site)
class DokonchiAdmin(BaseUserAdmin):
    """Do'konchilar (tizimga ro'yxatdan o'tgan do'kon egalari) ro'yxati.

    Eslatma: parollar Django tomonidan bir tomonlama (qaytarib bo'lmaydigan)
    shifrlanadi, shuning uchun hech qanday admin ham foydalanuvchining aslida
    qanday parol kiritganini ko'ra olmaydi -- bu barcha foydalanuvchilarning
    xavfsizligi uchun. Agar kimningdir paroli esidan chiqsa, shu yerdan
    "Parolni o'zgartirish" havolasi orqali yangi parol o'rnatib berishingiz
    mumkin.
    """

    inlines = [ProfileInline]
    list_display = (
        'username', 'dokon_nomi', 'mijozlar_soni', 'jami_qarzi',
        'kirishlar_soni', 'holat_badge', 'date_joined', 'last_login',
    )
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'profile__store_name')
    ordering = ('-date_joined',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('profile').annotate(
            _mijozlar_soni=Count('customers', distinct=True),
            _jami_qarz=Sum('customers__debts__amount', filter=Q(customers__debts__is_paid=False)),
        )

    def _profile(self, obj):
        try:
            return obj.profile
        except Profile.DoesNotExist:
            return None

    @admin.display(description="Do'kon nomi")
    def dokon_nomi(self, obj):
        profile = self._profile(obj)
        return (profile.store_name if profile else '') or '\u2014'

    @admin.display(description="Mijozlar soni", ordering='_mijozlar_soni')
    def mijozlar_soni(self, obj):
        return obj._mijozlar_soni or 0

    @admin.display(description="Jami qarzi", ordering='_jami_qarz')
    def jami_qarzi(self, obj):
        return "{:,.0f} so'm".format(obj._jami_qarz or 0).replace(',', ' ')

    @admin.display(description="Necha marta kirgan")
    def kirishlar_soni(self, obj):
        profile = self._profile(obj)
        return profile.login_count if profile else 0

    @admin.display(description="Holati")
    def holat_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color:#059669;font-weight:700;">&#9679; Faol</span>')
        return format_html('<span style="color:#e11d48;font-weight:700;">&#9679; Bloklangan</span>')


class DebtInline(admin.TabularInline):
    model = Debt
    extra = 0


@admin.register(Customer, site=admin_site)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'owner', 'total_unpaid', 'created_at')
    list_filter = ('owner',)
    search_fields = ('first_name', 'last_name', 'phone')
    inlines = [DebtInline]


@admin.register(Debt, site=admin_site)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('customer', 'description', 'amount', 'is_paid', 'created_at', 'paid_at')
    list_filter = ('is_paid',)
    search_fields = ('customer__first_name', 'customer__last_name', 'description')
