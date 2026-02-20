from django.contrib import admin
from django import forms
from django.db import models
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, ConsultoriaOnline, Exercicio, Treino, DiaTreino, ExercicioTreino

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


# ===== TREINOS =====

class ExercicioTreinoInline(admin.TabularInline):
    model = ExercicioTreino
    extra = 1
    fields = ('ordem', 'exercicio', 'series', 'repeticoes', 'carga', 'descanso', 'observacao_especifica')
    autocomplete_fields = ['exercicio']
    ordering = ('ordem',)
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 2, 'cols': 40})},
    }


class DiaTreinoInline(admin.StackedInline):
    model = DiaTreino
    extra = 1
    fields = ('nome', 'descricao', 'ordem')
    show_change_link = True


@admin.register(Treino)
class TreinoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'aluno', 'consultoria', 'status', 'criado_em')
    list_filter = ('status', 'criado_em', 'consultoria__usuario')
    search_fields = ('titulo', 'descricao', 'consultoria__usuario__username', 'consultoria__usuario__email')
    readonly_fields = ('aluno', 'criado_em', 'atualizado_em')
    inlines = [DiaTreinoInline]
    
    fieldsets = (
        ('Informações do Treino', {
            'fields': ('aluno', 'consultoria', 'titulo', 'status', 'descricao')
        }),
        ('Arquivo', {
            'fields': ('arquivo_pdf',),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Se marcar como 'atual', desativa outros treinos do mesmo aluno
        if obj.status == 'atual':
            Treino.objects.filter(
                consultoria=obj.consultoria, 
                status='atual'
            ).exclude(pk=obj.pk).update(status='inativo')
        super().save_model(request, obj, form, change)

    def aluno(self, obj):
        return obj.consultoria.usuario.get_full_name() or obj.consultoria.usuario.username
    aluno.short_description = 'Aluno'


@admin.register(DiaTreino)
class DiaTreinoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'treino', 'aluno', 'ordem')
    list_filter = ('treino', 'treino__consultoria__usuario')
    search_fields = ('nome', 'treino__titulo')
    inlines = [ExercicioTreinoInline]
    ordering = ('treino', 'ordem')

    def aluno(self, obj):
        return obj.treino.consultoria.usuario.get_full_name() or obj.treino.consultoria.usuario.username
    aluno.short_description = 'Aluno'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'treino':
            field.label_from_instance = (
                lambda obj: f"{obj.titulo} - {obj.consultoria.usuario.get_full_name() or obj.consultoria.usuario.username}"
            )
        return field
