from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    whatsapp = models.CharField('WhatsApp', max_length=20, blank=True)
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return self.username
    
    def tem_consultoria_online(self):
        """Verifica se o usuário tem consultoria online ativa"""
        return hasattr(self, 'consultoria') and self.consultoria.ativa


class ConsultoriaOnline(models.Model):
    usuario = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='consultoria',
        verbose_name='Usuário'
    )
    ativa = models.BooleanField('Consultoria Ativa', default=True)
    data_inicio = models.DateField('Data de Início', auto_now_add=True)
    data_fim = models.DateField('Data de Término', null=True, blank=True)
    observacoes = models.TextField('Observações', blank=True)
    
    # Plano Alimentar e Medicação
    plano_alimentar_arquivo = models.FileField(
        'Arquivo de Plano Alimentar',
        upload_to='consultoria/planos_alimentares/',
        blank=True,
        null=True
    )
    medicacao_arquivo = models.FileField(
        'Arquivo de Medicação',
        upload_to='consultoria/medicacoes/',
        blank=True,
        null=True
    )
    
    plano_alimentar_texto = models.TextField('Descrição do Plano Alimentar', blank=True)
    medicacao_texto = models.TextField('Descrição da Medicação', blank=True)
    
    data_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)
    
    class Meta:
        verbose_name = 'Consultoria Online'
        verbose_name_plural = 'Consultorias Online'
    
    def __str__(self):
        return f"Consultoria de {self.usuario.get_full_name() or self.usuario.username}"
    
    def get_treino_atual(self):
        """Retorna o treino atual (ativo)"""
        return self.treinos.filter(status='atual').first()
    
    def get_treinos_inativos(self):
        """Retorna treinos inativos"""
        return self.treinos.filter(status='inativo').order_by('-criado_em')


# ===== BANCO DE EXERCÍCIOS =====

class Exercicio(models.Model):
    """Banco geral de exercícios - cadastro único reutilizável"""
    nome = models.CharField('Nome do Exercício', max_length=200)
    descricao = models.TextField('Descrição', blank=True, help_text='Como executar o exercício')
    grupo_muscular = models.CharField('Grupo Muscular', max_length=100, blank=True, help_text='Ex: Peito, Costas, Pernas')
    
    link_video = models.URLField('Link do Vídeo', blank=True, help_text='YouTube, Instagram, etc')
    imagem = models.ImageField('Imagem', upload_to='exercicios/', blank=True, null=True)
    
    dica_execucao = models.TextField('Dica de Execução', blank=True)
    observacoes = models.TextField('Observações', blank=True)
    
    ativo = models.BooleanField('Ativo', default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Exercício (Banco)'
        verbose_name_plural = 'Exercícios (Banco)'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


# ===== TREINOS =====

class Treino(models.Model):
    STATUS_CHOICES = [
        ('atual', 'Atual'),
        ('inativo', 'Inativo'),
    ]
    
    consultoria = models.ForeignKey(
        ConsultoriaOnline,
        on_delete=models.CASCADE,
        related_name='treinos',
        verbose_name='Consultoria'
    )
    titulo = models.CharField('Título do Treino', max_length=200)
    descricao = models.TextField('Descrição Geral', blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='atual')
    
    arquivo_pdf = models.FileField('PDF do Treino (opcional)', upload_to='treinos/', blank=True, null=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Treino'
        verbose_name_plural = 'Treinos'
        ordering = ['-status', '-criado_em']
    
    def __str__(self):
        return f"{self.titulo} ({self.get_status_display()})"


class DiaTreino(models.Model):
    """Subdivisao do treino (A, B, C, D...)"""
    treino = models.ForeignKey(
        Treino,
        on_delete=models.CASCADE,
        related_name='dias',
        verbose_name='Treino'
    )
    nome = models.CharField('Nome do Dia', max_length=100, help_text='Ex: Treino A, Superior, Pernas')
    descricao = models.TextField('Descricao', blank=True)
    ordem = models.IntegerField('Ordem', default=1)

    class Meta:
        verbose_name = 'Dia de Treino'
        verbose_name_plural = 'Dias de Treino'
        ordering = ['treino', 'ordem']

    def __str__(self):
        return f"{self.treino.titulo} - {self.nome}"


class ExercicioTreino(models.Model):
    """Vincula exercícios do banco ao treino com configurações específicas"""
    dia_treino = models.ForeignKey(
        DiaTreino,
        on_delete=models.CASCADE,
        related_name='exercicios',
        verbose_name='Dia de Treino'
    )
    exercicio = models.ForeignKey(
        Exercicio,
        on_delete=models.CASCADE,
        related_name='treinos',
        verbose_name='Exercício'
    )
    
    ordem = models.IntegerField('Ordem', default=1)
    series = models.IntegerField('Séries', default=3)
    repeticoes = models.CharField('Repetições', max_length=50, help_text='Ex: 12, 10-12, até falha')
    carga = models.CharField('Carga', max_length=50, blank=True, help_text='Ex: 20kg, Peso corporal')
    descanso = models.CharField('Descanso', max_length=50, blank=True, help_text='Ex: 60s, 1-2min')
    
    observacao_especifica = models.TextField('Observação Específica', blank=True, help_text='Observação apenas para este aluno/treino')
    
    class Meta:
        verbose_name = 'Exercício do Treino'
        verbose_name_plural = 'Exercícios do Treino'
        ordering = ['dia_treino', 'ordem']
        unique_together = ['dia_treino', 'exercicio', 'ordem']
    
    def __str__(self):
        return f"{self.exercicio.nome} - {self.series}x{self.repeticoes}"
