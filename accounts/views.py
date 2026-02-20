from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib import messages
from .forms import CadastroForm

User = get_user_model()


def cadastro(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            # Cria o usuário
            user = User.objects.create_user(
                username=form.cleaned_data['email'],  # Username = Email
                email=form.cleaned_data['email'],
                password=form.cleaned_data['senha'],
                first_name=form.cleaned_data['nome_completo'].split()[0],
                last_name=' '.join(form.cleaned_data['nome_completo'].split()[1:]) if len(form.cleaned_data['nome_completo'].split()) > 1 else '',
                whatsapp=form.cleaned_data['celular']
            )
            
            messages.success(request, 'Cadastro realizado com sucesso! Faça login para continuar.')
            return redirect('accounts:login')
    else:
        form = CadastroForm()
    
    return render(request, 'accounts/cadastro.html', {'form': form})


def logout_view(request):
    """View de logout"""
    logout(request)
    messages.success(request, 'Você saiu da sua conta com sucesso.')
    return redirect('sales')
