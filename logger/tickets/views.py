from multiprocessing import context
import re
from .forms import TicketForm, CustomUserForm, TicketCommentsForm
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Department, Employee, Type, Ticket
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils import timezone



'''
landing
'''

def landing(request):
    return render(request, 'tickets/index.html')

'''
below view is not 
needed anymore---
delete it later
'''

def create_manage(request):
    return render(request, 'tickets/user_home.html')

'''
views for
registration, login and logout
home might be deleted later
'''

def check_employee_status(user):
    return Employee.objects.filter(employee=user).exists()

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['is_employee'] = check_employee_status(user)
            return redirect('department_selection')  # redirect to the home view

        else:
            # handle invalid login attempt
            context = {'error': 'Invalid username or password'}
            return render(request, 'tickets/login.html', context)
    else:
        return render(request, 'tickets/login.html')

@login_required
def home(request):
    user = request.user
    if hasattr(user, 'employee') and user.employee.role == 'manager':
        return render(request, 'tickets/manager_home.html')
    else:
        return render(request, 'tickets/staff_home.html')

def register_view(request):
    if request.method == 'POST':                           # http request method - pulls data from server
        form = CustomUserForm(request.POST)                # starts the form using the request - with POST data
        if form.is_valid():
            user =  form.save()                            # saves form (in db) upon validation
            login(request, user)
            return redirect('department_selection')
    else:
        form = CustomUserForm()                           # for request method GET 
    context = { 
        'form':form
    }
    return render(request, 'tickets/register.html', context)   # returns registr. page to user

def logout_view(request):
    logout(request)
    return render(request, 'tickets/logout.html')

'''
department specific views
- department selection during ticket creation
- create ticket for specific department
'''


@login_required
def department_selection(request):
    departments = Department.objects.all()
    return render(request, 'tickets/department_selection.html', {'departments': departments})

def department_ticket_creation(request):
    department_id = request.GET.get('department')
    department = get_object_or_404(Department, id=department_id)

    if request.method == 'POST':
        form = TicketForm(request.POST, department=department)
        if form.is_valid():
            try:
                ticket = form.save(commit=False)
                ticket.request_user = request.user
                ticket.save()
            
                messages.success(request, \
                        f'Your ticket has been \
                            successfully created and sent to {department.department_name}.' )
                            
                return redirect('ticket_created')                  # redirect to a success page or the ticket list
            except Exception as e:
                messages.error(request, f'Failed to create ticket: {str(e)}')
        else:
            messages.error(request, 'Form submission failed. Please check the form details.')
    else:
        form = TicketForm(department=department)

    context = {
        'form': form,
        'department': department,
    }
    return render(request, 'tickets/department_ticket_creation.html', context)


'''
ticket management views
- create ticket
- update ticket (update message later !?)
- delete ticket
- created tickets message

'''

@login_required
def manage_tickets(request):
    tickets = Ticket.objects.filter(request_user=request.user)
    ticket_comments = TicketCommentsForm()
    if request.method == 'POST':
        form = TicketCommentsForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.ticket_id = request.POST.get('ticket_id')
            comment.save()
            return redirect('manage_tickets')

    context = {
        'tickets': tickets,
        'comment_form':ticket_comments
    }
    return render(request, 'tickets/manage_tickets.html', context)

@login_required
def get_manage_tickets(request):
    tickets = Ticket.objects.filter(request_user=request.user)
    ticket_comments = TicketCommentsForm()
    context = {
        'tickets': tickets,
        'comment_form':ticket_comments
    }
    return render(request, 'tickets/partials/get_manage_tickets.html', context)

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # save the ticket form data to session
                request.session['ticket_data'] = form.cleaned_data
                return redirect('department_selection')         # redirect to department selection
            except Exception as e:
                messages.error(request, f'Failed to create ticket: {str(e)}')
    else:
        form = TicketForm()

    context = {
        'form': form,
    }
    return render(request, 'tickets/create_ticket.html', context)

@login_required
def ticket_created(request):

    context = {
        'success_message': "Your ticket has been successfully created and sent to the department.",
    }
    return render(request, 'tickets/ticket_created.html', context)

'''
@login_required
def ticket_update(request, pk):
    ticket = get_object_or_404(
            Ticket, 
            pk = pk, 
            request_user = request.user
    )
    department = ticket.employee.department

    if request.method == 'POST':
        form = TicketForm(
            request.POST, 
            instance = ticket,
            department = department
    )
        if form.is_valid():
            form.save()
            return('manage_tickets')
    else:
        form = TicketForm(
            instance = ticket, 
            department = department
    )
    context = {
        'form':form
    }
    return render( request, 'tickets/ticket_update.html', context)
'''

@login_required
def ticket_update(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, request_user=request.user)
    department = ticket.employee.department
    
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket, department=department)
        if form.is_valid():
            ticket = form.save(commit=False)
            #ticket.updated_at = timezone.now()  # Set the updated_at timestamp
            ticket.save()
            return redirect('manage_tickets')  # Redirect to the manage_tickets view upon successful update
    else:
        form = TicketForm(instance=ticket, department=department)
    
    context = {
        'form': form,
    }
    return render(request, 'tickets/ticket_update.html', context)

@login_required
def ticket_delete(request, pk):
    ticket = get_object_or_404(
                Ticket,
                pk = pk,
                request_user = request.user
    )
    if request.method == 'POST':
        ticket.delete()       
        return('manage_tickets')

    context = {
            'ticket': ticket
    }
    return render(request, 'tickets/ticket_delete.html', context)


'''
ticket comments
'''

@login_required
def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    comments = ticket.comments.all()
    comment_form = TicketCommentsForm()

    if request.method == 'POST':
        form = TicketCommentsForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.ticket = ticket
            comment.save()
            return HttpResponseRedirect(reverse('ticket_detail', args=[pk]))

    context = {
        'ticket': ticket,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'tickets/ticket_detail.html', context)

@login_required
def add_comment(request, ticket_id):
    print(f'\n the request {request.method} \n')  # This should now print "POST" if form submission is successful
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        form = TicketCommentsForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.ticket = ticket
            comment.save()
            messages.success(request, 'Comment added successfully.')

            comments = ticket.comments.all()  # Get updated comments
            context = {'comments': comments, 'ticket': ticket}

            return render_to_string('tickets/partials/comment.html', context, request=request)

        else:
            messages.error(request, 'Failed to add comment. Please check the form.')

    return JsonResponse({'error': 'Invalid request method or comment form error'})

@login_required
def employee_dashboard(request):
    user = request.user
    try:
        employee = Employee.objects.get(employee=user)
        if employee.role == 'manager':
            # managers see all tickets in their department
            assigned_tickets = Ticket.objects.filter(employee__department=employee.department)
        else:
            # staff and interns see only their assigned tickets
            assigned_tickets = Ticket.objects.filter(employee=employee)
    except Employee.DoesNotExist:
        assigned_tickets = []

    context = {
        'assigned_tickets': assigned_tickets
    }
    return render(request, 'tickets/employee_dashboard.html', context)

def myticket_counts(request):
    user = request.user
    tickets = Ticket.objects.filter(request_user=user)
    if tickets.count() > 0:

        return HttpResponse(
        f'''<span hx-get="/myticket_counts" hx-swap="outerHTML" hx-trigger="every 60s" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">{tickets.count()}</span>'''
 )

    else:
        return HttpResponse(
        f'''<span hx-get="/myticket_counts" hx-swap="outerHTML" hx-trigger="every 60s"></span>'''
 )

