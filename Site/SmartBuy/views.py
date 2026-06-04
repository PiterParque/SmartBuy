from django.shortcuts import render,get_list_or_404,get_object_or_404
from SmartBuy.models import Produto,HistoricoPreco,Product_Type,CotacaoDolar
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone

def index(request):

    produtos = Produto.objects.all().order_by("-criado_em")[:10]
    produtos_melhores_avaliacoes=Produto.objects.all().order_by("avaliacao")[:5]
    produtos_amazon = (
        Produto.objects
        .filter(product_type__source='amazon_search')
        .order_by('-id')[:20]
    )

    produtos_mercadolivre = (
        Produto.objects
        .filter(product_type__source='mercadolivre_search')
        .order_by('-id')[:20]
    )

    context = {
        "produtos_destaque": produtos,
        "produtos_carrosel":produtos_melhores_avaliacoes,
        'produtos_amazon': produtos_amazon,
        'produtos_mercadolivre': produtos_mercadolivre,
        "AMAZON": 'amazon_search',
        "MERCADO_LIVRE": 'mercadolivre_search',

    }

    return render(request, "_base.html", context)


def produto(request, id):

    produto = get_object_or_404(Produto, id=id)
    # =========================================
    # PRODUTO
    # =========================================

    produto = get_object_or_404(
        Produto,
        id=id
    )

    # =========================================
    # HISTÓRICO
    # =========================================

    historico = HistoricoPreco.objects.filter(
        produto=produto
    ).order_by("coletado_em")

    periodo = request.GET.get(
        "periodo",
        "30"
    )

    historico = HistoricoPreco.objects.filter(
        produto=produto
    )

    if periodo != "all":

        dias = int(periodo)

        historico = historico.filter(
            coletado_em__gte=
            timezone.now() - timedelta(days=dias)
        )

    historico = historico.order_by(
        "coletado_em"
    )

    # =========================================
    # DATAFRAME
    # =========================================

    df = pd.DataFrame(
        list(
            historico.values(
                "preco",
                "coletado_em"
            )
        )
    )
    cotacoes = CotacaoDolar.objects.all().values(
        "valor",
        "data"
    )

    df_dolar = pd.DataFrame(list(cotacoes))
    df["data"] = pd.to_datetime(
        df["coletado_em"]
    ).dt.date

    df_dolar["data"] = pd.to_datetime(
        df_dolar["data"]
    ).dt.date
    df = df.merge(
        df_dolar,
        on="data",
        how="left"
    )
    previsoes = []

    # =========================================
    # MACHINE LEARNING
    # =========================================

    if not df.empty and len(df) > 1:

        # converter data
        df["coletado_em"] = pd.to_datetime(
            df["coletado_em"]
        )

        # transformar cotação em número
        df["valor"] = pd.to_numeric(
            df["valor"],
            errors="coerce"
        )

        # preencher valores faltantes
        df["valor"] = (
            df["valor"]
            .ffill()
            .bfill()
        )

        # criar coluna de dias
        df["dias"] = (
            df["coletado_em"] -
            df["coletado_em"].min()
        ).dt.days

        # variáveis de entrada
        X = df[
            [
                "dias",
                "valor"
            ]
        ]

        # variável alvo
        y = df["preco"].astype(float)

        # modelo
        modelo = LinearRegression()

        modelo.fit(X, y)

        # último dólar conhecido
        ultimo_dolar = df["valor"].iloc[-1]

        # próximos 7 dias
        futuros_dias = pd.DataFrame({
            "dias": np.arange(
                df["dias"].max() + 1,
                df["dias"].max() + 8
            ),
            "valor": ultimo_dolar
        })

        # previsões
        resultado = modelo.predict(
            futuros_dias
        )

        previsoes = [
            round(float(preco), 2)
            for preco in resultado
        ]

    # =========================================
    # CONTEXT
    # =========================================

    context = {
        "produto": produto,
        "historico": historico,
        "previsoes": previsoes,
        "AMAZON": 'amazon_search',
        "MERCADO_LIVRE": 'mercadolivre_search',
        "periodo": periodo,
    }

    return render(request, "product.html", context)


def pesquisar(request):

    termo = request.GET.get("q", "").strip()
    produtos = Produto.objects.all()
    if termo:
        print(termo)
        produtos = produtos.filter(
            Q(titulo__icontains=termo)
        )
    context = {
        "termo": termo,
        "produtos": produtos,
        "AMAZON":'amazon_search',
        "MERCADO_LIVRE":'mercadolivre_search',
    }

    return render(
        request,
        "pesquisa.html",
         context,
    )
def categoria(request, categoria):


    tipos = get_list_or_404(
        Product_Type,
        produto__iexact=categoria
    )

    produtos = Produto.objects.filter(
        product_type__in=tipos
    )

    return render(
        request,
        "produtos.html",
        {
            "produtos": produtos,
            "filtro": categoria,
            "AMAZON": 'amazon_search',
            "MERCADO_LIVRE": 'mercadolivre_search',
        }
    )

def loja(request,loja):
    produtos_loja = get_list_or_404(
        Product_Type,
        loja__iexact=loja
    )

    produtos = Produto.objects.filter(
        product_type__in=produtos_loja
    )
    if loja == 'mercadolivre_search':
        loja="Mercado livre"
    elif loja == "amazon_search":
        loja="Amazon"
    else:
        pass
    return render(
        request,
        "produtos.html",
        {
            "produtos": produtos,
            "filtro": loja,
            "AMAZON": 'amazon_search',
            "MERCADO_LIVRE": 'mercadolivre_search',
        }
    )
def queda_preco(request):

    produtos_queda = []

    for produto in Produto.objects.all():

        historico = produto.historico.all()[:2]

        if len(historico) >= 2:

            preco_atual = historico[0].preco
            preco_anterior = historico[1].preco

            if preco_atual < preco_anterior:
                produtos_queda.append(produto)

    return render(
        request,
        "produtos.html",
        {
            "produtos": produtos_queda,
            "filtro": "Preços em Queda",
            "AMAZON": "amazon_search",
            "MERCADO_LIVRE": "mercadolivre_search",
        }
    )                                                                                        