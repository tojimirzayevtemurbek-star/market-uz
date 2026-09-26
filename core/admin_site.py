from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.db.models import Q, Sum


class QarzDaftarAdminSite(AdminSite):
    site_header = "Qarz Daftar — Boshqaruv paneli"
    site_title = "Qarz Daftar admin"
    index_title = "Umumiy holat"

    def index(self, request, extra_context=None):
        from .models import Customer, Debt  # local import - sirkulyar importdan qochish uchun

        extra_context = extra_context or {}

        dokonchilar = User.objects.filter(is_superuser=False)
        extra_context.update({
            'dokonchilar_soni': dokonchilar.count(),
            'faol_dokonchilar_soni': dokonchilar.filter(is_active=True).count(),
            'jami_mijozlar_soni': Customer.objects.count(),
            'jami_qarz_summasi': Debt.objects.filter(is_paid=False).aggregate(t=Sum('amount'))['t'] or 0,
            'songgi_royxatdan_otganlar': dokonchilar.select_related('profile').order_by('-date_joined')[:5],
        })
        return super().index(request, extra_context)


admin_site = QarzDaftarAdminSite(name='qarzdaftar_admin')
