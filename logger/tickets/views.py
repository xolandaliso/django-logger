from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from multiprocessing import context
from collections import defaultdict
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from .utils import send_email_notification
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.contrib.auth.forms import UserCreationForm
from .models import Department, Employee, Status, Ticket
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import TicketForm, CustomUserForm, TicketCommentsForm


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

        user = authenticate(
            request, 
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            request.session['is_employee'] = check_employee_status(user)
            request.session['employee_role'] = get_employee_role(user)
            return redirect('department_selection')  # redirect to the home view

        else:
            # handle invalid login attempt
            context = {'error': 'Invalid username or password'}
            return render(request, 'tickets/login.html', context)
    else:
        return render(request, 'tickets/login.html')

def get_employee_role(user):
    try:
        employee = Employee.objects.get(employee=user)
        if employee.role == 'manager' and employee.department is None:
            return 'super_manager'
        return employee.role
    except Employee.DoesNotExist:
        return None

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
    return render(
        request, 
        'tickets/register.html', 
        context
    )           # renders registr. template

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

    context=  {
        'departments': departments
    }
    return render(
        request, 
        'tickets/department_selection.html',
        context
    )

def department_ticket_creation(request):
    department_id = request.GET.get('department')
    department = get_object_or_404(Department, id=department_id)

    if request.method == 'POST':
        form = TicketForm(
            request.POST, 
            department=department,
            form_type='create'
        )
        if form.is_valid():
            try:
                ticket = form.save(commit=False)
                ticket.request_user = request.user
                selected_employee = form.cleaned_data.get('employee')

                if selected_employee.employee == request.user:
                    messages.error(request, 'You cannot assign a ticket to yourself.')
                else:
                    open_status = Status.objects.get(
                        status_description='open',
                        department=department
                    )
                    ticket.ticket_status = open_status
                    ticket.save()

                    # prepare ticket details for the email
                    ticket_details = f'Ticket ID: {ticket.id}\n' \
                                     f'Description: {ticket.ticket_description}\n' \
                                     f'Department: {department.department_name}\n' \
                                     f'Created by: {ticket.request_user.get_full_name()}'

                    # fetch employee email from the database
                    employee_email = selected_employee.employee.email
                    user_email = request.user.email

                    # send email notification to the employee
                    employee_subject = f'New {ticket.ticket_type} Ticket Assigned to You'
                    employee_message = f'A new ticket has been assigned to you. \
                            \n \n Details: \n {ticket_details}'
                    send_email_notification(employee_email, employee_subject, employee_message)

                    # send email notification to the user

                    user_subject = 'Ticket Created Successfully'
                    user_message = f'Hi, {ticket.request_user.get_full_name()} \n \
                        Your ticket has been \
                        successfully created and sent to {department.department_name} department.\
                        \n thanks, \n TAD'
                    send_email_notification(user_email, user_subject, user_message)

                    messages.success(request, f'Your ticket has been successfully created and sent to {department.department_name}.')
                    return redirect('department_selection')
            except Status.DoesNotExist:
                messages.error(request, 'Open status for this department does not exist.')
            except Exception as e:
                messages.error(request, f'Failed to create ticket: {str(e)}')
        else:
            messages.error(request, 'Form submission failed. Please check the form details.')
    else:
        form = TicketForm(
            department=department, 
            form_type='create'
        )

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

    return render(request, 'tickets/manage_tickets.html')

@login_required
def get_manage_tickets(request):
    user = request.user
    search_query = request.GET.get('search', '')  # get the search query from the request
    tickets = Ticket.objects.filter(
        request_user=user
    )
    
    if search_query:
        tickets = tickets.filter(
            ticket_description__icontains=search_query
        )
    
    open_tickets = tickets.exclude(
        ticket_status__status_description='closed')[:3]  # slice open tickets to first 3

    closed_tickets = tickets.filter(
        ticket_status__status_description='closed')[:3]    # closed tickets to first 3
    ticket_comments = TicketCommentsForm()

    one_week_ago = timezone.now() - timedelta(weeks=1)
    
    context = {
        'open_tickets': open_tickets,
        'closed_tickets': closed_tickets,
        'search_query': search_query,
        'ticket_comments' : ticket_comments,
        'one_week_ago': one_week_ago
    }

    return render(
        request, 
        'tickets/partials/ticket_list_user.html',
         context
    )  # return only the ticket list fragment for HTMX request

'''
tickets open longer 
than 5 days, supermanager's view
'''

def open_tickets_over_5_days(request):
    user = request.user
    employee = Employee.objects.get(
        employee=user
    )

    if user.is_authenticated and employee.role == 'super_manager':
        five_days_ago = timezone.now() - timedelta(days=5)
        data = Ticket.objects.filter(
            created_at__lte=five_days_ago,
            ticket_status__status_description='open'
        ).values('employee__department__department_name').annotate(open_tickets_count=Count('id')).order_by('employee__department__department_name')

        print(f'\n the data: {data}\n')

        return JsonResponse(
            list( data ), 
            safe=False
        )
    return JsonResponse(
        {'error': 'Unauthorized access'},
         status=401
    )

'''
tickets open longer 
than 5 days, manager's view
'''

def manager_open_tickets_over_5_days(request):
    user = request.user
    employee = Employee.objects.get(
        employee=user
    )
    if user.is_authenticated and employee.role == 'manager':
        five_days_ago = timezone.now() - timedelta(days=5)
        data = Ticket.objects.filter(
            created_at__lte=five_days_ago,
            ticket_status__status_description='open',
            department=request.user.employee.department
        ).values('employee.department').annotate(open_tickets_count=Count('id')).order_by('employee.department')

        print(f'\n the data: {data}\n')
        return JsonResponse(list(data), safe=False)
    
    return JsonResponse({'error': 'Unauthorized access'}, status=401)

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                request.session['ticket_data'] = form.cleaned_data # save the ticket form data to session
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
    
@login_required
def ticket_update(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    user = request.user

    try:
        employee = Employee.objects.get(
            employee=user
        )
        user_role = employee.role

    except Employee.DoesNotExist:
        user_role = 'user'

    if request.method == 'POST':
        form = TicketForm(
            request.POST,
            instance=ticket,
            department=ticket.employee.department,
            user_role=user_role,
            form_type='update'
        )

        if form.is_valid():
            updated_ticket = form.save(commit=False)
            updated_ticket.ticket_status = form.cleaned_data['ticket_status']
            
            # check for resolution if the ticket is being closed
            if updated_ticket.ticket_status.status_description == 'closed' and not form.cleaned_data['ticket_resolution']:
                messages.error(request, 'Please provide a resolution before closing the ticket.')
                form.add_error('ticket_resolution', 'Please provide a resolution before closing the ticket.')

                context = {
                    'form': form,
                    'ticket': updated_ticket,
                }
                return render(request, 'tickets/ticket_update.html', context)

            updated_ticket.save()
            messages.success(request, 'Ticket updated successfully.')
            return redirect('ticket_detail', pk=ticket.pk)

        else:
            messages.error(request, 'Form submission failed. Please check the form details.')

    else:
        form = TicketForm(
            instance=ticket,
            department=ticket.employee.department,
            user_role=user_role,
            form_type='update'
        )

    context = {
        'form': form,
        'ticket': ticket,
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
            return HttpResponseRedirect( reverse('ticket_detail', args=[pk]) )

    context = {
        'ticket': ticket,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(
        request, 
        'tickets/ticket_detail.html',
        context
    )


def ticket_reopen(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)

    if request.user != ticket.request_user:
        messages.error(request, 'You do not have permission to reopen this ticket.')
        return redirect('manage_tickets')

    if ticket.ticket_status.status_description == 'closed':
        if ticket.updated_at and timezone.now() <= ticket.updated_at + timedelta(weeks=1):
            open_status = Status.objects.filter(status_description='open', department=ticket.employee.department).first()
            if open_status:
                ticket.ticket_status = open_status
                ticket.save()
                messages.success(request, 'Ticket reopened successfully.')
            else:
                messages.error(request, 'Open status not found.')
        else:
            messages.warning(request, 'This ticket cannot be reopened as it was closed more than a week ago.')
    else:
        messages.warning(request, 'This ticket is not closed.')

    return redirect('manage_tickets')

@login_required
def add_comment(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        form = TicketCommentsForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.ticket = ticket
            comment.save()
            messages.success(request, 'Comment added successfully.')

            comments = ticket.comments.all()  # get updated comments
            context = {'comments': comments, 'ticket': ticket}

            return render_to_string(
                'tickets/partials/comment.html', 
                context, 
                request=request
            )

        else:
            messages.error(request, 'Failed to add comment. Please check the form.')

    return JsonResponse(
        {   'error': 'Invalid request method or comment form error' }
    )

def employee_dashboard(request):
    user = request.user
    view = request.GET.get('view', 'assigned')  # default to 'assigned' view
    search_query = request.GET.get('search', '')

    try:
        employee = Employee.objects.get(employee=user)
        
        if view == 'all_departments' and employee.role == 'super_manager':
            tickets = Ticket.objects.select_related('employee__department').all()
        elif view == 'department' and employee.role == 'manager':
            tickets = Ticket.objects.filter(employee__department=employee.department)
        elif view == 'created' and employee.role == 'super_manager':
            tickets = Ticket.objects.filter(request_user=user)
        else:
            tickets = Ticket.objects.filter(employee=employee)

        if search_query:
            tickets = tickets.filter(
                Q(ticket_description__icontains=search_query) |
                Q(employee__employee__first_name__icontains=search_query) |
                Q(employee__employee__last_name__icontains=search_query)
            )

        paginator = Paginator(tickets, 3)  # show 3 tickets per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        if view == 'all_departments' and employee.role == 'super_manager':
            department_tickets = defaultdict(list)
            for ticket in page_obj:
                department_tickets[ticket.employee.department.department_name].append(ticket)
            context = {
                'employee': employee,
                'department_tickets': dict(department_tickets),
                'view': view,
                'search_query': search_query,
                'page_obj': page_obj,
            }
        else:
            context = {
                'employee': employee,
                'assigned_tickets': page_obj,
                'view': view,
                'search_query': search_query,
                'page_obj': page_obj,
            }
    except Employee.DoesNotExist:
        context = {
            'assigned_tickets': [],
            'view': view,
        }

    if request.htmx:
        return render(request, 'tickets/partials/ticket_list.html', context)
    
    return render(request, 'tickets/employee_dashboard.html', context)
    
def get_assigned_tickets(employee):
    if employee.role == 'manager':
        assigned_tickets = Ticket.objects.filter(
            employee__department=employee.department
        )
    else:
        assigned_tickets = Ticket.objects.filter(
            employee=employee
        )
    return assigned_tickets

def assign_ticketcounts(request):
    user = request.user
    try:
        employee = Employee.objects.get(employee=user)
        if employee.role == 'manager':
            # managers see all tickets in their department
            assigned_tickets = Ticket.objects.filter(
                employee__department=employee.department
            )
        else:
            # staff and interns see only their assigned tickets
            assigned_tickets = Ticket.objects.filter(
                employee=employee
            )
    
    except Employee.DoesNotExist:
        assigned_tickets = []

    if assigned_tickets.count() > 0:

            return HttpResponse(
            f'''<span 
                    hx-get="/assign_ticketcounts" 
                    hx-swap="outerHTML" 
                    hx-trigger="every 60s" 
                    class="position-absolute \
                    top-0 start-100 translate-middle\
                    badge rounded-pill bg-secondary text-white" 
                    style=" margin-left: 1px;
                    margin-right: 10px;
                    margin-top:-5px;"> { assigned_tickets.count() }
                </span>'''
            )
    else:
        return HttpResponse(
        f'''<span 
                hx-get="/myticket_counts" 
                hx-swap="outerHTML" 
                hx-trigger="every 60s">
            </span>'''
        )

def myticket_counts(request):
    user = request.user
    tickets = Ticket.objects.filter(request_user=user)
    if tickets.count() > 0:

        return HttpResponse(
        f'''<span 
                hx-get="/myticket_counts" 
                hx-swap="outerHTML" 
                hx-trigger="every 60s" 
                class="position-absolute \
                top-0 start-100 translate-middle\
                badge rounded-pill bg-secondary text-white" 
                style=" margin-left: 1px;
                margin-right: 10px;
                margin-top:-5px;"> { tickets.count() }
            </span>'''
        )

    else:
        return HttpResponse(
        f'''<span 
                hx-get="/myticket_counts" 
                hx-swap="outerHTML" 
                hx-trigger="every 60s">
            </span>'''
        )
        
def department_ticket_stats(request):
    status_counts = Ticket.objects.values(
        'ticket_status__status_description').annotate(count=Count('id'))

    return JsonResponse(list(status_counts), safe=False)

def tickets_by_status(request):
    status = request.GET.get('status')

    if status:
        tickets = Ticket.objects.filter(ticket_status__status_description=status)
        ticket_data = [
            {
                'id': ticket.id,
                'ticket_description': ticket.ticket_description,
                'employee_name': ticket.employee.employee.get_full_name(),  # adjust as per your model structure
                'created_at': ticket.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for ticket in tickets
        ]
        return JsonResponse(ticket_data, safe=False)

    return JsonResponse([], safe=False)