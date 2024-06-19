
from django.shortcuts import render, redirect
from .forms import TicketForm
from django.contrib.auth.decorators import login_required

def landing(request):
    return render(request, 'tickets/index.html')

def login_view(request):
    return render(request, 'tickets/login.html')

def register_view(request):
    return render(request, 'tickets/register.html')

@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_tickets')
    else:
        form = TicketForm()
    return render(request, 'tickets/create_ticket.html', {'form': form})

@login_required
def manage_tickets(request):
    return render(request, 'tickets/manage_tickets.html')
