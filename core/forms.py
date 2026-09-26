from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User

from .models import Customer, Debt, Profile

INPUT_CLASSES = (
    "w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-slate-800 "
    "placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 "
    "outline-none transition"
)


class RegisterForm(UserCreationForm):
    store_name = forms.CharField(
        label="Do'kon nomi",
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "Masalan: Aziz Market"}),
    )

    class Meta:
        model = User
        fields = ["username", "store_name", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": INPUT_CLASSES, "placeholder": "Login"})
        self.fields["password1"].widget.attrs.update({"class": INPUT_CLASSES, "placeholder": "Parol"})
        self.fields["password2"].widget.attrs.update({"class": INPUT_CLASSES, "placeholder": "Parolni takrorlang"})
        for f in self.fields.values():
            f.help_text = None


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Login",
        widget=forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "Login", "autofocus": True}),
    )
    password = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(attrs={"class": INPUT_CLASSES, "placeholder": "Parol"}),
    )


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "phone"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "Ismi"}),
            "last_name": forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "Familiyasi (ixtiyoriy)"}),
            "phone": forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "+998 90 123 45 67"}),
        }


class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = ["description", "amount"]
        widgets = {
            "description": forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "Nima oldi? (ixtiyoriy)"}),
            "amount": forms.NumberInput(attrs={"class": INPUT_CLASSES, "placeholder": "Summasi (so'm)"}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["store_name"]
        widgets = {
            "store_name": forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "Masalan: Aziz Market"}),
        }


class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget.attrs.update({"class": INPUT_CLASSES, "placeholder": "Joriy parol"})
        self.fields["new_password1"].widget.attrs.update({"class": INPUT_CLASSES, "placeholder": "Yangi parol"})
        self.fields["new_password2"].widget.attrs.update({"class": INPUT_CLASSES, "placeholder": "Yangi parolni takrorlang"})
        for f in self.fields.values():
            f.help_text = None
