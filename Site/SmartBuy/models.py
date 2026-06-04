from django.db import models


class Product_Type(models.Model):

    AMAZON = "amazon_search"
    MERCADO_LIVRE = "mercadolivre_search"
    GOOGLE = "google_shopping_search"

    SOURCE_CHOICES = [

        (AMAZON, "Amazon"),
        (MERCADO_LIVRE, "Mercado Livre"),
        (GOOGLE, "Google"),
    ]

    produto = models.TextField(
        blank=True,
        null=True
    )

    loja = models.TextField(
        blank=True,
        null=True
    )

    source = models.CharField(
        max_length=100,
        choices=SOURCE_CHOICES,
        default=AMAZON,
        db_index=True
    )

    def __str__(self):

        return f"{self.produto} - {self.loja}"


class Produto(models.Model):

    product_type = models.ForeignKey(
        Product_Type,
        on_delete=models.CASCADE,
        related_name="tipo"
    )

    titulo = models.TextField(
        blank=True,
        null=True
    )

    preco = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    imagem = models.TextField(
        blank=True,
        null=True
    )

    url = models.TextField(
        blank=True,
        null=True
    )

    avaliacao = models.TextField(
        blank=True,
        null=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return self.titulo



class HistoricoPreco(models.Model):

    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name="historico"
    )

    preco = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    coletado_em = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ["-coletado_em"]
class CotacaoDolar(models.Model):
    valor = models.DecimalField(max_digits=10, decimal_places=4)
    data = models.DateField(auto_now_add=True)