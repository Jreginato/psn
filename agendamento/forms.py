from django import forms
from .models import Agendamento
from datetime import date, time, datetime

class AgendamentoForm(forms.ModelForm):
    horario_desejado = forms.ChoiceField(
        label='Horário desejado',
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    
    class Meta:
        model = Agendamento
        fields = ['nome', 'email', 'telefone', 'data_desejada', 'horario_desejado', 'objetivo', 'mensagem']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Digite seu nome completo', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'seuemail@exemplo.com', 'class': 'form-input'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(11) 99999-9999 ou +5511999999999', 'class': 'form-input', 'maxlength': '20'}),
            'data_desejada': forms.DateInput(attrs={'type': 'date', 'class': 'form-input', 'min': date.today().isoformat()}),
            'objetivo': forms.Select(attrs={'class': 'form-input'}),
            'mensagem': forms.Textarea(attrs={'placeholder': 'Conte mais sobre seu objetivo (opcional)', 'rows': 4, 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Gerar horários disponíveis das 08:00 às 18:00 de 30 em 30 minutos
        horarios = [('', 'Selecione um horário')]
        for hora in range(8, 18):
            horarios.append((f'{hora:02d}:00:00', f'{hora:02d}:00'))
            horarios.append((f'{hora:02d}:30:00', f'{hora:02d}:30'))
        # Adicionar 18:00 como último horário
        horarios.append(('18:00:00', '18:00'))
        
        self.fields['horario_desejado'].choices = horarios

    def clean_data_desejada(self):
        data = self.cleaned_data.get('data_desejada')
        if data and data < date.today():
            raise forms.ValidationError('A data não pode ser anterior a hoje.')
        # Validar se é domingo (weekday 6)
        if data and data.weekday() == 6:
            raise forms.ValidationError('Não atendemos aos domingos. Escolha outro dia.')
        return data

    def clean_horario_desejado(self):
        horario_str = self.cleaned_data.get('horario_desejado')
        if horario_str:
            # Converter string para time
            horario = datetime.strptime(horario_str, '%H:%M:%S').time()
            if horario < time(8, 0) or horario > time(18, 0):
                raise forms.ValidationError('Horário deve estar entre 08:00 e 18:00.')
            return horario
        return None
