import random
from decimal import Decimal
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from SmartBuy.models import Produto, HistoricoPreco


class Command(BaseCommand):

    help = "Gerar históricos"

    def handle(self, *args, **kwargs):

        produtos = Produto.objects.all()

        for produto in produtos:

            preco_base = random.uniform(100, 5000)

            for dia in range(180):

                variacao = random.uniform(-0.10, 0.10)

                preco = preco_base * (1 + variacao)

                historico = HistoricoPreco.objects.create(
                    produto=produto,
                    preco=Decimal(round(preco, 2))
                )

                historico.coletado_em = (
                    timezone.now() - timedelta(days=dia)
                )

                historico.save()

        print("Históricos criados!")