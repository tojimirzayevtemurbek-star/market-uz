from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse



from .forms import (
    RegisterForm, LoginForm, CustomerForm, DebtForm,
    ProfileForm, StyledPasswordChangeForm,
)
from .models import Customer, Debt, Profile
from .search_utils import fuzzy_contains

def manifest_view(request):
    data = {
        "name": "Qarz Daftar",
        "short_name": "QarzDaftar",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#000000"
    }
    return JsonResponse(data)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, store_name=form.cleaned_data.get('store_name', ''))
            login(request, user)
            messages.success(request, "Xush kelibsiz! Ro'yxatdan muvaffaqiyatli o'tdingiz.")
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            form.add_error(None, "Login yoki parol noto'g'ri.")
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    customers = Customer.objects.filter(owner=request.user)
    total_unpaid = Debt.objects.filter(customer__owner=request.user, is_paid=False).aggregate(
        t=Sum('amount'))['t'] or 0
    total_paid = Debt.objects.filter(customer__owner=request.user, is_paid=True).aggregate(
        t=Sum('amount'))['t'] or 0
    debtor_count = customers.filter(debts__is_paid=False).distinct().count()

    # Har bir mijoz uchun faqat bitta (eng so'nggi) qarz yozuvini olamiz,
    # shu bilan bitta mijozga bir nechta qarz qo'shilsa ham ro'yxatda
    # takrorlanib chiqmaydi.
    recent_debts = []
    seen_customers = set()
    for debt in Debt.objects.filter(customer__owner=request.user).select_related('customer').order_by('-created_at'):
        if debt.customer_id in seen_customers:
            continue
        seen_customers.add(debt.customer_id)
        recent_debts.append(debt)
        if len(recent_debts) >= 8:
            break

    context = {
        'total_unpaid': total_unpaid,
        'total_paid': total_paid,
        'debtor_count': debtor_count,
        'customer_count': customers.count(),
        'recent_debts': recent_debts,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def customer_list_view(request):
    query = request.GET.get('q', '').strip()
    customers_qs = Customer.objects.filter(owner=request.user).annotate(
        unpaid=Sum('debts__amount', filter=Q(debts__is_paid=False))
    )
    if query:
        # Avval oddiy (aniq) qidiruv - tez ishlaydi.
        exact = customers_qs.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(phone__icontains=query)
        )
        exact_ids = set(exact.values_list('id', flat=True))

        # Keyin "fuzzy" qidiruv - 1-2 ta harf xato yozilgan bo'lsa ham topadi.
        fuzzy_matches = [
            c for c in customers_qs
            if c.id not in exact_ids and (
                fuzzy_contains(query, c.full_name) or fuzzy_contains(query, c.phone)
            )
        ]

        customers = list(exact.order_by('-unpaid')) + sorted(
            fuzzy_matches, key=lambda c: -(c.unpaid or 0)
        )
    else:
        customers = customers_qs.order_by('-unpaid')
    return render(request, 'core/customer_list.html', {'customers': customers, 'query': query})


@login_required
def customer_add_view(request):
    if request.method == 'POST':
        c_form = CustomerForm(request.POST)
        d_form = DebtForm(request.POST)
        if c_form.is_valid():
            customer = c_form.save(commit=False)
            customer.owner = request.user
            customer.save()
            if d_form.data.get('amount'):
                if d_form.is_valid():
                    debt = d_form.save(commit=False)
                    debt.customer = customer
                    debt.save()
            messages.success(request, f"{customer.full_name} ro'yxatga qo'shildi.")
            return redirect('customer_detail', pk=customer.pk)
    else:
        c_form = CustomerForm()
        d_form = DebtForm()
    return render(request, 'core/customer_add.html', {'c_form': c_form, 'd_form': d_form})


@login_required
def customer_detail_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk, owner=request.user)
    if request.method == 'POST':
        d_form = DebtForm(request.POST)
        if d_form.is_valid():
            debt = d_form.save(commit=False)
            debt.customer = customer
            debt.save()
            messages.success(request, "Yangi qarz qo'shildi.")
            return redirect('customer_detail', pk=customer.pk)
    else:
        d_form = DebtForm()

    debts = customer.debts.all()
    return render(request, 'core/customer_detail.html', {
        'customer': customer,
        'debts': debts,
        'd_form': d_form,
    })


@login_required
def debt_pay_view(request, pk):
    debt = get_object_or_404(Debt, pk=pk, customer__owner=request.user)
    if request.method == 'POST':
        debt.mark_paid()
        messages.success(request, "Qarz to'landi deb belgilandi.")
    return redirect('customer_detail', pk=debt.customer.pk)


@login_required
def debt_delete_view(request, pk):
    debt = get_object_or_404(Debt, pk=pk, customer__owner=request.user)
    customer_pk = debt.customer.pk
    if request.method == 'POST':
        debt.delete()
        messages.success(request, "Qarz yozuvi o'chirildi.")
    return redirect('customer_detail', pk=customer_pk)


@login_required
def settings_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil ma'lumotlari yangilandi.")
            return redirect('settings')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'core/settings.html', {'form': form})


@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = StyledPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Parolingiz muvaffaqiyatli o'zgartirildi.")
            return redirect('settings')
    else:
        form = StyledPasswordChangeForm(request.user)
    return render(request, 'core/password_change.html', {'form': form})
