from django.contrib import admin
from .models import Department, Employee, Ticket, Status, Type, Resolution

# Register your models here.
admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(Ticket)
admin.site.register(Status)
admin.site.register(Type)
admin.site.register(Resolution)