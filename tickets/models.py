from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        
class CustomUser(AbstractUser, TimeStampedModel):
    phone = models.CharField(max_length=15, blank=True, null=True)
    pbx_extension = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username 
        
               
class Department(TimeStampedModel):
    department_name = models.CharField(max_length=255)
    employees = models.ManyToManyField('CustomUser', through='Employee', related_name='departments')

    def __str__(self):
        return self.department_name
        
   
class Employee(TimeStampedModel):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('intern', 'Intern'),
        # Add other roles as needed
    ]

    employee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='employee_roles')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='department_employees')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.employee.username} - {self.department.department_name}"
        
 
class Type(models.Model):
    type_description = models.CharField(max_length=255)

    def __str__(self):
        return self.type_description

class Resolution(models.Model):
    resolution_description = models.CharField(max_length=255)

    def __str__(self):
        return self.resolution_description

class Status(models.Model):
    status_description = models.CharField(max_length=255)

    def __str__(self):
        return self.status_description

class Location(models.Model):
    location_name = models.CharField(max_length=255)
    location_description = models.TextField(blank=True, null=True)
    location_parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sublocations')

    def __str__(self):
        return self.location_name       
 
class Ticket(TimeStampedModel):
    request_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='requested_tickets')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assigned_tickets')
    ticket_description = models.TextField()
    ticket_type = models.ForeignKey(Type, on_delete=models.CASCADE, related_name='tickets')
    ticket_resolution = models.ForeignKey(Resolution, on_delete=models.CASCADE, related_name='tickets')
    ticket_status = models.ForeignKey(Status, on_delete=models.CASCADE, related_name='tickets')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='tickets')

    def __str__(self):
        return f"Ticket {self.id} by {self.request_user.username}"
        #https://django-simple-history.readthedocs.io/en/latest/
        
class TicketComments(TimeStampedModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()

    def __str__(self):
        return f"Comment by {self.user.username} on Ticket {self.ticket.id}"       
           
class Documents(TimeStampedModel):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to='documents/')

    def __str__(self):
        return f"Document for Ticket {self.ticket.id}"
        
 
class RecurringTicket(TimeStampedModel):
    FREQUENCY_CHOICES = [
        ('minutely', 'Minutely'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('custom', 'Custom'),
    ]

    UNIT_CHOICES = [
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ]

    recurring_description = models.TextField()
    frequency = models.CharField(max_length=50, choices=FREQUENCY_CHOICES)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='recurring_tickets')
    custom_interval = models.PositiveIntegerField(null=True, blank=True)
    custom_unit = models.CharField(max_length=50, choices=UNIT_CHOICES, null=True, blank=True)
    next_run = models.DateField()

    def __str__(self):
        return f"Recurring Ticket by {self.employee.employee.username} - {self.frequency}"