from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class CadastroForm(forms.Form):
    nome_completo = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Digite seu nome completo'
        }),
        label='Nome Completo'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'seu@email.com'
        }),
        label='E-mail'
    )
    
    celular = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+55 (00) 00000-0000 ou formato internacional',
            'id': 'id_celular'
        }),
        label='Celular / WhatsApp',
        help_text='Formato brasileiro ou internacional'
    )
    
    senha = forms.CharField(
        min_length=6,
        max_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '6 dígitos'
        }),
        label='Senha (6 dígitos)'
    )
    
    confirmacao_senha = forms.CharField(
        min_length=6,
        max_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '6 dígitos'
        }),
        label='Confirme a Senha'
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Verifica se email já está cadastrado
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este e-mail já está cadastrado.')
        
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get('senha')
        confirmacao_senha = cleaned_data.get('confirmacao_senha')
        
        if senha and confirmacao_senha:
            if senha != confirmacao_senha:
                raise ValidationError('As senhas não conferem.')
        
        return cleaned_data
