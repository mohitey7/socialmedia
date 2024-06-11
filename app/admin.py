from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm
from django.template.response import TemplateResponse
from django.core.exceptions import PermissionDenied

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = UserCreationForm
    ordering = ['id']
    readonly_fields = ['id', 'created_at', 'last_login']
    list_display = ['id', 'firstname', 'lastname', 'email', 'is_staff', 'is_admin']
    fieldsets = (
        ('Credentials', {'fields': ('email', 'password')}),
        (('Personal info'), {'fields': ('firstname', 'lastname')}),
        ('Permissions', {'fields': ('is_staff', 'is_admin')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'firstname', 'lastname', 'password1', 'password2', 'is_staff', 'is_admin'),
        }),
    )

    filter_horizontal = ()
    list_filter = []

    def change_password(self, request, user_id, form_url=''):
        user = self.get_object(request, user_id)
        if not self.has_change_permission(request, user):
            raise PermissionDenied

        if request.method == 'POST':
            form = AdminPasswordChangeForm(user, request.POST)
            if form.is_valid():
                form.save()
                return self.response_change(request, user)
        else:
            form = AdminPasswordChangeForm(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        admin_form = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': f'Change password: {user.email}',
            'adminForm': admin_form,
            'form_url': form_url,
            'form': form,
            'is_popup': "_popup" in request.POST or "_popup" in request.GET,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
            **self.admin_site.each_context(request),
        }

        return TemplateResponse(request, 'admin/auth/user/change_password.html', context)

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<user_id>/password/',
                self.admin_site.admin_view(self.change_password),
                name='auth_user_password_change',
            ),
        ]
        return custom_urls + urls

admin.site.site_header = 'Social Media Administration'
admin.site.site_title = 'Admin Panel'
admin.site.index_title = 'Social Media Databases'

admin.site.register(User, CustomUserAdmin)
admin.site.register(FriendRequest)
admin.site.register(Friendship)