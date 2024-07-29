from django.contrib import admin
from django.db import models
from .models import Department, Employee, Ticket, Status, Type, Resolution

# Register your models here.

class TicketAdmin(admin.ModelAdmin):
    # ... other admin configurations ...

    formfield_overrides = {
        models.ForeignKey: {'queryset': Status.objects.all()},
    }

admin.site.register(Ticket, TicketAdmin)
admin.site.register(Status)
admin.site.register(Department)
admin.site.register(Employee)
#admin.site.register(Ticket)
admin.site.register(Type)
admin.site.register(Resolution)