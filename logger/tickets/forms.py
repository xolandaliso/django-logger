
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import (
    CustomUser, Department, Employee, Type, Resolution, Status, Location, 
    Ticket, TicketComments, Documents, RecurringTicket
)

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [ 
                    'username', 'password', 'email', 'phone', 'pbx_extension', 'is_active' ]

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['department_name', 'employees']

    def __init__(self, *args, **kwargs):
        super(DepartmentForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))
    
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['employee', 'department', 'role']

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
                    'request_user', 'employee', 'ticket_description', 'ticket_type',\
                         'ticket_resolution', 'ticket_status', 'location' ]

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))


class TicketCommentsForm(forms.ModelForm):
    class Meta:
        model = TicketComments
        fields = ['ticket', 'user', 'comment']

    def __init__(self, *args, **kwargs):
        super(TicketCommentsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))


class DocumentsForm(forms.ModelForm):
    class Meta:
        model = Documents
        fields = ['ticket', 'document']

    def __init__(self, *args, **kwargs):
        super(DocumentsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input( Submit('submit', 'Submit') )


class RecurringTicketForm(forms.ModelForm):
    class Meta:
        model = RecurringTicket
        fields = [
                    'recurring_description', 'frequency', 'employee',\
                        'custom_interval', 'custom_unit', 'next_run' ]

    def __init__(self, *args, **kwargs):
        super(RecurringTicketForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input( Submit('submit', 'Submit') )

