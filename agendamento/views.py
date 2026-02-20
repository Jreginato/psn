from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AgendamentoForm

def agendar(request):
    if request.method == 'POST':
        form = AgendamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Agendamento realizado com sucesso! Entraremos em contato em breve.')
            return redirect('agendamento:sucesso')
    else:
        form = AgendamentoForm()
    
    return render(request, 'agendamento/agendar.html', {'form': form})

def agendamento_sucesso(request):
    return render(request, 'agendamento/sucesso.html')
