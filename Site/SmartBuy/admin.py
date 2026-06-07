from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Produto, HistoricoPreco,AlertaPreco


class HistoricoPrecoInline(admin.TabularInline):

    model = HistoricoPreco

    extra = 0

    readonly_fields = (
        'preco',
        'coletado_em'
    )

    can_delete = False


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):

    list_display = (
        'titulo',
        'preco',
        'avaliacao',
        'criado_em'
    )

    search_fields = (
        'titulo',
    )

    list_filter = (
        'criado_em',
    )

    readonly_fields = (
        'criado_em',
    )

    inlines = [
        HistoricoPrecoInline
    ]


@admin.register(HistoricoPreco)
class HistoricoPrecoAdmin(admin.ModelAdmin):

    list_display = (
        'produto',
        'preco',
        'coletado_em'
    )

    search_fields = (
        'produto__titulo',
    )

    list_filter = (
        'coletado_em',
    )

    readonly_fields = (
        'coletado_em',
    )
@admin.register(AlertaPreco)
class AlertaPrecoAdmin(admin.ModelAdmin):

    list_display = (
        "produto",
        "email",
        "criado_em",
    )

    search_fields = (
        "email",
        "produto__titulo",
    )

    list_filter = (
        "criado_em",
    )

    readonly_fields = (
        "criado_em",
    )

    autocomplete_fields = (
        "produto",
    )