from django.contrib import admin
from django.contrib import messages
from .models import User, Company, Office, Vehicle
from .constants import OFFICE_EXISTS_ERROR


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    ordering = ['date_joined']
    list_display = ('id', 'email', 'first_name', 'last_name', 'role', 'company_id', 'office_id', 'is_active', 'is_staff', 'password', 'date_joined',)
    list_filter = ('email', 'first_name', 'last_name',)
    fields = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'date_joined', 'password', 'company', 'office')


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ('id', 'name', 'address')
    fields = ('name', 'address')


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ('id', 'name', 'address', 'city', 'region', 'country', 'company_id', 'vehicle_count')
    fields = ('name', 'address', 'city', 'region', 'country', 'company', 'vehicle_count')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    ordering = ['id']
    list_display = ('id', 'name', 'licence_plate', 'model', 'year_of_manufacture', 'user_id', 'company_id', 'office_id')
    fields = ('name', 'licence_plate', 'model', 'year_of_manufacture', 'user', 'company', 'office')
    list_filter = ('office', 'user',)

    def save_model(self, request, obj, form, change):
        office = form.cleaned_data.get('office')
        user = form.cleaned_data.get('user')

        if user and office:
            if not user.is_office_exists():
                return self.message_user(request,
                                         OFFICE_EXISTS_ERROR,
                                         messages.ERROR)

            if user.office.id != office.id:
                return self.message_user(request,
                                         'The worker must be from the same office as the vehicle',
                                         messages.ERROR)

        return super().save_model(request, obj, form, change)
