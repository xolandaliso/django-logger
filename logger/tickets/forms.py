from ast import arg
from dataclasses import fields
from django import forms
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from .models import CustomUser, Department, Ticket, Employee, Documents, Location, TicketComments, Type

class CustomUserForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):

        model = CustomUser
        
        fields = [
                    'first_name', 'last_name', 'username', 'email', 'phone', 'pbx_extension', 'is_active' ]

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Register', css_class='btn-primary'))
        self.helper.layout = Layout(
            Field('first_name', css_class='form-control'),
            Field('last_name',  css_class='form-control'),
            Field('username', css_class='form-control'),
            Field('email', css_class='form-control'),
            Field('phone', css_class='form-control'),
            Field('pbx_extension', css_class='form-control'),
        )

    def save(self, commit=True):
        user = super(CustomUserForm, self).save(commit=False)
        if commit:
            user.save()
        return user

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [ 
                    'ticket_description', 'ticket_type', 'location', 'employee' ]

    def __init__(self, *args, **kwargs):
        department = kwargs.pop('department', None)
        super(TicketForm, self).__init__(*args, **kwargs)
        if department:
            self.fields['employee'].queryset = Employee.objects.filter(department=department)
            self.fields['ticket_type'].queryset = Type.objects.filter(department=department)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create Ticket', css_class='btn-primary'))
        self.helper.layout = Layout(
            Field('ticket_description', css_class='form-control'),
            Field('ticket_type', css_class='form-control'),
            Field('location', css_class='form-control'),
            Field('employee', css_class='form-control'),
        )

class TicketFormComments(forms.ModelForm):
    class Meta:
        model = TicketComments
        fields = ['comment']

        def __init__(self, *args, **kwargs):
            super(TicketFormComments, self).__init__(*args, **kwargs)
            self.helper = FormHelper()
            self.helper.form_method = 'post'
            self.helper.layout = Layout(
                Field('comment', css_class='form-control', rows=3),
                Submit('submit', 'Add Comment', css_class='btn btn-primary mt-2')
        )