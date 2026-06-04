import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from django.core.management.base import BaseCommand

from sklearn.linear_model import LinearRegression

from SmartBuy.models import HistoricoPreco


class Command(BaseCommand):

    help = "Gerar previsões de preço"

    def handle(self, *args, **kwargs):

        # =========================================
        # ESCOLHER PRODUTO
        # =========================================

        produto_id = 1

        # =========================================
        # PEGAR DADOS DO DJANGO
        # =========================================

        historicos = (
            HistoricoPreco.objects
            .filter(produto_id=produto_id)
            .order_by('coletado_em')
            .values(
                'preco',
                'coletado_em'
            )
        )

        # =========================================
        # VERIFICA SE EXISTEM DADOS
        # =========================================

        if not historicos.exists():

            self.stdout.write(
                self.style.ERROR(
                    'Nenhum histórico encontrado'
                )
            )

            return

        # =========================================
        # CONVERTE PARA DATAFRAME
        # =========================================

        df = pd.DataFrame(list(historicos))

        # =========================================
        # CONVERTER DATA
        # =========================================

        df["coletado_em"] = pd.to_datetime(
            df["coletado_em"]
        )

        # =========================================
        # ORDENA DADOS
        # =========================================

        df = df.sort_values(
            "coletado_em"
        )

        # =========================================
        # CRIA COLUNA DE TEMPO
        # =========================================

        df["dias"] = (
            df["coletado_em"] -
            df["coletado_em"].min()
        ).dt.days

        # =========================================
        # MACHINE LEARNING
        # =========================================

        X = df[["dias"]]

        y = df["preco"].astype(float)

        # =========================================
        # TREINA MODELO
        # =========================================

        modelo = LinearRegression()

        modelo.fit(X, y)

        # =========================================
        # PREVER PRÓXIMOS 30 DIAS
        # =========================================

        futuros_dias = np.arange(
            df["dias"].max() + 1,
            df["dias"].max() + 31
        ).reshape(-1, 1)

        previsoes = modelo.predict(
            futuros_dias
        )

        # =========================================
        # MOSTRAR PREVISÕES
        # =========================================

        self.stdout.write(
            self.style.SUCCESS(
                "\nPREVISÕES FUTURAS:\n"
            )
        )

        for dia, preco in zip(
            futuros_dias,
            previsoes
        ):

            print(
                f"Dia {dia[0]} -> R$ {preco:.2f}"
            )

        # =========================================
        # GRÁFICO
        # =========================================

        plt.figure(figsize=(14, 6))

        # Histórico real
        plt.plot(
            df["dias"],
            y,
            label="Histórico"
        )

        # Previsão futura
        plt.plot(
            futuros_dias,
            previsoes,
            label="Previsão"
        )

        plt.xlabel("Dias")

        plt.ylabel("Preço")

        plt.title(
            "Previsão de Preço do Produto"
        )

        plt.legend()

        plt.grid(True)

        plt.show()