from .forms import TicketForm, CustomUserForm
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Department, Employee, Type, Ticket
from django.contrib import messages


def landing(request):
    return render(request, 'tickets/index.html')

def create_manage(request):
    return render(request, 'tickets/user_home.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('create_manage')  # Redirect to the home view
        else:
            # Handle invalid login attempt
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

# registration view
def register_view(request):
    if request.method == 'POST':                           # http request method - pulls data from server
        form = CustomUserForm(request.POST)                # starts the form using the request - with POST data
        if form.is_valid():
            user =  form.save()                            # saves form (in db) upon validation
            login(request, user)
            return redirect('create_manage')
    else:
        form = CustomUserForm()                           # for request method GET 
    return render( request, 'tickets/register.html', { 'form' : form } )   # returns registr. page to user

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            try:
                # save the ticket form data to session
                request.session['ticket_data'] = form.cleaned_data
                return redirect('department_selection')              # redirect to department selection
            except Exception as e:
                messages.error(request, f'Failed to create ticket: {str(e)}')
    else:
        form = TicketForm()

    context = {
        'form': form,
    }
    return render(request, 'tickets/create_ticket.html', context)

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


@login_required
def ticket_created(request):

    context = {
        'success_message': "Your ticket has been successfully created and sent to the department.",
    }
    return render(request, 'tickets/ticket_created.html', context)


def manage_tickets(request):
    tickets = Ticket.objects.filter(request_user=request.user)

    context = {
        'tickets': tickets,
    }
    return render(request, 'tickets/manage_tickets.html', context)


def logout_view(request):
    logout(request)
    return render(request, 'tickets/logout.html')
