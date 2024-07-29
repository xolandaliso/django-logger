from django import forms
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Field, Div
from .models import CustomUser, Resolution, Ticket, Employee, Documents, Status, TicketComments, Type


class CustomUserForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Register', css_class='btn-primary'))
        self.helper.layout = Layout(
            Div(
                Div('first_name', css_class='col-md-6 mb-0', style="margin-right: 10px;"),
                Div('last_name', css_class='col-md-6 mb-0', style="margin-left: 50px;"),
                css_class='form-row'
            ),
            Div(
                Div('username', css_class='col-md-6 mb-0', style="margin-right: 10px;"),
                Div('email', css_class='col-md-6 mb-0'),
                css_class='form-row'
            ),
            Div(
                Div('phone', css_class='col-md-6 mb-0', style="margin-right: 10px;"),
                Div('pbx_extension', css_class='col-md-6 mb-0'),
                css_class='form-row'
            ),
            Div(
                Div('password1', css_class='col-md-6 mb-0', style="margin-right: 10px;"),
                Div('password2', css_class='col-md-6 mb-0'),
                css_class='form-row'
            )
        )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'pbx_extension']

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)  # Ensure to call super with UserCreationForm
        user.is_active = True  # Always set is_active to True
        if commit:
            user.save()
        return user

'''
class TicketForm(forms.ModelForm):
    document = forms.FileField(label='Attach Document', required=False)  # Add a file upload field

    class Meta:
        model = Ticket
        fields = ['ticket_description', 'ticket_type', 'location', 'employee']  # Include necessary fields

    def __init__(self, *args, **kwargs):
        department = kwargs.pop('department', None)
        user_role = kwargs.pop('user_role', None)  # Add user_role parameter

        super(TicketForm, self).__init__(*args, **kwargs)

        if department:
            self.fields['employee'].queryset = Employee.objects.filter(department=department)
            self.fields['ticket_type'].queryset = Type.objects.filter(department=department)

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        if user_role == 'employee':
            self.fields['ticket_status'] = forms.ModelChoiceField(queryset=Status.objects.all(), required=False)
            self.helper.layout = Layout(
                Field('ticket_description', css_class='form-control'),
                Field('ticket_type', css_class='form-control'),
                Field('location', css_class='form-control'),
                Field('employee', css_class='form-control'),
                'ticket_status',  # Include ticket_status field
                'document',
                Submit('submit', 'Create Ticket', css_class='btn btn-primary')
            )
        else:
            self.helper.layout = Layout(
                Field('ticket_description', css_class='form-control'),
                Field('ticket_type', css_class='form-control'),
                Field('location', css_class='form-control'),
                Field('employee', css_class='form-control'),
                'document',
                Submit('submit', 'Create Ticket', css_class='btn btn-primary')
            )

    def save(self, commit=True):
        ticket = super(TicketForm, self).save(commit=False)
        if commit:
            ticket.save()

        # Save the uploaded document if present
        if self.cleaned_data.get('document'):
            Documents.objects.create(ticket=ticket, document=self.cleaned_data['document'])

        return ticket
'''
class TicketForm(forms.ModelForm):
    document = forms.FileField(label='Attach Document', required=False)  # add a file upload field

    class Meta:
        model = Ticket
        fields = ['ticket_description', 'ticket_type', 'location', 'employee']  #general fields

    def __init__(self, *args, **kwargs):
        department = kwargs.pop('department', None)
        user_role = kwargs.pop('user_role', None)      # add user_role parameter
        form_type = kwargs.pop('form_type', 'create')  # add form_type parameter
        user = kwargs.pop('user', None)  # add user parameter

        super(TicketForm, self).__init__(*args, **kwargs)

        if department:
            print(f'\nuser:{user}')
            self.fields['employee'].queryset = Employee.objects.filter(department=department).exclude(employee=user)
            self.fields['ticket_type'].queryset = Type.objects.filter(department=department)

            if form_type == 'create':
                self.fields['employee'].queryset = self.fields['employee'].queryset.exclude(role='super_manager')

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        if form_type == 'update' and user_role in ['staff', 'manager', 'super_manager']:
            # add ticket_status and ticket_resolution fields for updating
            self.fields['ticket_status'] = forms.ModelChoiceField(
                queryset=Status.objects.filter(department=department),
                required=False,
                empty_label="Select status",
                label="Ticket Status"
            )

            self.fields['ticket_resolution'] = forms.ModelChoiceField(
                queryset=Resolution.objects.filter(department=department),
                required=False,
                empty_label="Select resolution",
                label="Ticket Resolution"
            )

            # use the human-readable labels from STATUS_CHOICES
            self.fields['ticket_status'].label_from_instance = lambda obj: dict(Status.STATUS_CHOICES).get(obj.status_description, obj.get_status_description_display())

            self.helper.layout = Layout(
                Field('ticket_description', css_class='form-control'),
                Field('ticket_type', css_class='form-control'),
                Field('location', css_class='form-control'),
                Field('employee', css_class='form-control'),
                'ticket_status',
                Field('ticket_resolution', css_class='form-control', id='id_ticket_resolution', style='display:none;'),
                Submit('submit', 'Update Ticket', css_class='btn btn-primary')
            )
        else:
            self.helper.layout = Layout(
                Field('ticket_description', css_class='form-control'),
                Field('ticket_type', css_class='form-control'),
                Field('location', css_class='form-control'),
                Field('employee', css_class='form-control'),
                'document',
                Submit('submit', 'Create Ticket', css_class='btn btn-primary')
            )

        if user_role not in ['staff', 'manager', 'super_manager']:

            self.fields.pop('ticket_status', None)
            self.fields.pop('ticket_resolution', None)
            
    def save(self, commit=True):
        ticket = super(TicketForm, self).save(commit=False)
        
        # set ticket status to 'Open' during creation
        if self.instance.pk is None:
            open_status = Status.objects.filter(status_description='Open').first()
            ticket.ticket_status = open_status

        if commit:
            ticket.save()

        # save the uploaded document if present
        if self.cleaned_data.get('document'):
            Documents.objects.create(ticket=ticket, document=self.cleaned_data['document'])

        return ticket


'''
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
'''
class TicketCommentsForm(forms.ModelForm):
    class Meta:
        model = TicketComments
        fields = ['comment']

        def __init__(self, *args, **kwargs):
            super(TicketCommentsForm, self).__init__(*args, **kwargs)
            self.helper = FormHelper()
            self.helper.form_method = 'post'
            self.helper.add_input(Submit('submit', 'Add Comment', css_class='btn btn-secondary mt-2'))
            self.helper.layout = Layout(
                Field('comment', css_class='form-control', rows=3)
        )