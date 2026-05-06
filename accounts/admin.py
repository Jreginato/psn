from django.contrib import admin
from django import forms
from django.db import models
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone
import nested_admin
from .models import CustomUser, ConsultoriaOnline, Exercicio, Treino, DiaTreino, ExercicioTreino, SessaoTreino, SerieRealizada


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('whatsapp',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('whatsapp',)}),
    )
    list_display = ('username', 'email', 'whatsapp', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(ConsultoriaOnline)
class ConsultoriaOnlineAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'aluno', 'ativa', 'data_inicio', 'data_fim', 'data_atualizacao')
    list_filter = ('ativa', 'data_inicio', 'usuario')
    search_fields = ('usuario__username', 'usuario__email', 'usuario__first_name', 'usuario__last_name')
    readonly_fields = ('data_inicio', 'data_atualizacao')

    fieldsets = (
        ('Informações do Aluno', {
            'fields': ('usuario', 'ativa', 'data_inicio', 'data_fim', 'observacoes')
        }),
        ('Plano Alimentar', {
            'fields': ('plano_alimentar_arquivo', 'plano_alimentar_texto'),
            'classes': ('collapse',)
        }),
        ('Medicação', {
            'fields': ('medicacao_arquivo', 'medicacao_texto'),
            'classes': ('collapse',)
        }),
        ('Última Atualização', {
            'fields': ('data_atualizacao',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')

    def aluno(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username
    aluno.short_description = 'Aluno'


# ===== BANCO DE EXERCÍCIOS =====

@admin.register(Exercicio)
class ExercicioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'grupo_muscular', 'ativo', 'criado_em')
    list_filter = ('ativo', 'grupo_muscular')
    search_fields = ('nome', 'descricao', 'grupo_muscular')
    readonly_fields = ('criado_em', 'atualizado_em')

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'grupo_muscular', 'descricao', 'ativo')
        }),
        ('Mídia', {
            'fields': ('link_video', 'imagem')
        }),
        ('Orientações', {
            'fields': ('dica_execucao', 'observacoes')
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )


# ===== TREINOS — INLINE ANINHADO =====

class ExercicioTreinoNestedInline(nested_admin.NestedTabularInline):
    model = ExercicioTreino
    extra = 1
    fields = ('ordem', 'exercicio', 'series', 'repeticoes', 'carga', 'descanso', 'observacao_especifica')
    ordering = ('ordem',)
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 2, 'cols': 35})},
    }


class DiaTreinoNestedInline(nested_admin.NestedStackedInline):
    model = DiaTreino
    extra = 1
    fields = ('nome', 'ordem', 'descricao')
    ordering = ('ordem',)
    inlines = [ExercicioTreinoNestedInline]


@admin.register(Treino)
class TreinoAdmin(nested_admin.NestedModelAdmin):
    list_display = ('titulo', 'aluno_link', 'status_badge', 'total_dias', 'criado_em')
    list_filter = ('status', 'consultoria__usuario')
    search_fields = ('titulo', 'descricao', 'consultoria__usuario__username',
                     'consultoria__usuario__first_name', 'consultoria__usuario__last_name')
    readonly_fields = ('aluno_info', 'criado_em', 'atualizado_em')
    inlines = [DiaTreinoNestedInline]

    fieldsets = (
        ('Identificação', {
            'fields': ('aluno_info', 'consultoria', 'titulo', 'status', 'descricao')
        }),
        ('Arquivo PDF (opcional)', {
            'fields': ('arquivo_pdf',),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'consultoria__usuario'
        ).prefetch_related('dias')

    def save_model(self, request, obj, form, change):
        if obj.status == 'atual':
            Treino.objects.filter(
                consultoria=obj.consultoria,
                status='atual'
            ).exclude(pk=obj.pk).update(status='inativo')
        super().save_model(request, obj, form, change)

    def aluno_info(self, obj):
        if obj.pk:
            u = obj.consultoria.usuario
            return f"{u.get_full_name() or u.username} ({u.email})"
        return '—'
    aluno_info.short_description = 'Aluno'

    def aluno_link(self, obj):
        u = obj.consultoria.usuario
        nome = u.get_full_name() or u.username
        return format_html('<b>{}</b>', nome)
    aluno_link.short_description = 'Aluno'
    aluno_link.admin_order_field = 'consultoria__usuario__first_name'

    def status_badge(self, obj):
        color = '#16a34a' if obj.status == 'atual' else '#9ca3af'
        label = obj.get_status_display()
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;font-size:11px">{}</span>',
            color, label
        )
    status_badge.short_description = 'Status'

    def total_dias(self, obj):
        return obj.dias.count()
    total_dias.short_description = 'Dias'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'consultoria':
            field.label_from_instance = (
                lambda obj: f"{obj.usuario.get_full_name() or obj.usuario.username} ({obj.usuario.email})"
            )
        return field


# ===== SESSÕES DE TREINO =====

class SerieRealizadaInline(admin.TabularInline):
    model = SerieRealizada
    extra = 0
    readonly_fields = ('numero_serie', 'exercicio_nome', 'carga_usada', 'repeticoes_realizadas',
                       'tempo_descanso_segundos', 'concluida_em')
    fields = ('numero_serie', 'exercicio_nome', 'carga_usada', 'repeticoes_realizadas',
              'tempo_descanso_segundos', 'concluida_em')
    can_delete = False

    def exercicio_nome(self, obj):
        return obj.exercicio_treino.exercicio.nome
    exercicio_nome.short_description = 'Exercício'

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(SessaoTreino)
class SessaoTreinoAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'dia_treino_nome', 'treino_nome', 'status_badge',
                    'iniciado_em', 'duracao_display', 'total_series')
    list_filter = ('status', 'iniciado_em', 'usuario', 'dia_treino__treino__consultoria__usuario')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name',
                     'dia_treino__nome', 'dia_treino__treino__titulo')
    readonly_fields = ('usuario', 'dia_treino', 'status', 'iniciado_em', 'finalizado_em', 'duracao_display')
    inlines = [SerieRealizadaInline]
    ordering = ('-iniciado_em',)
    date_hierarchy = 'iniciado_em'

    fieldsets = (
        ('Sessão', {
            'fields': ('usuario', 'dia_treino', 'status', 'iniciado_em', 'finalizado_em', 'duracao_display')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'usuario', 'dia_treino__treino__consultoria__usuario'
        ).prefetch_related('series__exercicio_treino__exercicio')

    def aluno(self, obj):
        return format_html('<b>{}</b>', obj.usuario.get_full_name() or obj.usuario.username)
    aluno.short_description = 'Aluno'
    aluno.admin_order_field = 'usuario__first_name'

    def dia_treino_nome(self, obj):
        return obj.dia_treino.nome
    dia_treino_nome.short_description = 'Dia'

    def treino_nome(self, obj):
        return obj.dia_treino.treino.titulo
    treino_nome.short_description = 'Treino'

    def status_badge(self, obj):
        cores = {
            'em_andamento': '#f59e0b',
            'concluida':    '#16a34a',
            'abandonada':   '#9ca3af',
        }
        color = cores.get(obj.status, '#9ca3af')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:10px;font-size:11px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def duracao_display(self, obj):
        seg = obj.duracao_segundos
        if not seg:
            return '—'
        m = seg // 60
        s = seg % 60
        return f'{m}min {s}s'
    duracao_display.short_description = 'Duração'

    def total_series(self, obj):
        return obj.series.count()
    total_series.short_description = 'Séries'

