from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import User


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role')

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords don't match.")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        help_text='Passwords are hashed. Use <a href="../password/">this form</a> to change.'
    )

    class Meta:
        model = User
        fields = (
            'email', 'password', 'first_name', 'last_name', 'phone',
            'role', 'company', 'avatar', 'is_active', 'is_staff',
            'is_superuser', 'groups', 'user_permissions',
        )


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ['email', 'get_full_name', 'role', 'company', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'company']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_login']

    fieldsets = (
        (None, {'fields': ('id', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'avatar')}),
        ('Role & Company', {'fields': ('role', 'company')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions')
