from django.core.management.base import BaseCommand

from SmartBuy.models import (
    Produto,
    HistoricoPreco,
    Product_Type,
    CotacaoDolar
)
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from decimal import Decimal

import requests
import time
import os
import re


USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


class Command(BaseCommand):
     
    help = 'Coleta produtos da Amazon usando Oxylabs'

    BASE_URL = 'https://data.oxylabs.io/v1/queries'

    def handle(self, *args, **kwargs):
        self.coletar_dolar()
        lojas=['mercadolivre_search','amazon_search']
        produtos=["monitor","teclado","mouse","laptop"]
        for loja in  lojas:
                for produto in produtos:
                    # =====================================
                    # CRIA OU BUSCA O TIPO
                    # =====================================

                    product_type, _ = Product_Type.objects.get_or_create(
                        produto=produto,
                        loja=loja,
                        source=loja
                    )

                    produtos_ = self.pegar_produtos(
                        produto=produto,
                        source=loja
                    )

                    if not produtos_:

                        self.stdout.write(
                            self.style.ERROR('Nenhum produto encontrado')
                        )

                        

                    for produto in produtos_:

                        try:

                            preco_texto = produto['preco']

                            if not preco_texto:
                                continue

                            # =====================================
                            # LIMPA PREÇO
                            # =====================================

                            preco_limpo = (
                                preco_texto
                                .replace('.', '')
                                .replace(',', '.')
                            )

                            preco_limpo = re.sub(
                                r'[^\d.]',
                                '',
                                preco_limpo
                            )

                            if not preco_limpo:
                                continue

                            preco_decimal = Decimal(preco_limpo)

                            # =====================================
                            # BUSCA OU CRIA PRODUTO
                            # =====================================

                            produto_obj, criado = Produto.objects.get_or_create(

                                url=produto['url'],

                                defaults={

                                    'product_type': product_type,

                                    'titulo': produto['titulo'],

                                    # Produto.preco é CharField
                                    'preco': str(preco_decimal),

                                    'imagem': produto['imagem'],

                                    'avaliacao': produto['avaliacao']
                                }
                            )

                            # =====================================
                            # NOVO PRODUTO
                            # =====================================

                            if criado:

                                HistoricoPreco.objects.create(
                                    produto=produto_obj,
                                    preco=preco_decimal
                                )

                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'NOVO PRODUTO: {produto_obj.titulo}'
                                    )
                                )

                                continue

                            # =====================================
                            # ATUALIZA DADOS
                            # =====================================

                            produto_obj.product_type = product_type

                            produto_obj.titulo = produto['titulo']

                            produto_obj.imagem = produto['imagem']

                            produto_obj.avaliacao = produto['avaliacao']

                            # salva como string
                            produto_obj.preco = str(preco_decimal)

                            # =====================================
                            # ÚLTIMO HISTÓRICO
                            # =====================================

                            ultimo_historico = (
                                HistoricoPreco.objects
                                .filter(produto=produto_obj)
                                .order_by('-coletado_em')
                                .first()
                            )

                            # =====================================
                            # VERIFICA ALTERAÇÃO
                            # =====================================

                            if (
                                not ultimo_historico
                                or ultimo_historico.preco != preco_decimal
                            ):

                                HistoricoPreco.objects.create(
                                    produto=produto_obj,
                                    preco=preco_decimal
                                )

                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'NOVO HISTÓRICO: '
                                        f'{produto_obj.titulo} '
                                        f'-> R$ {preco_decimal}'
                                    )
                                )

                            else:

                                self.stdout.write(
                                    self.style.WARNING(
                                        f'PREÇO IGUAL: {produto_obj.titulo}'
                                    )
                                )

                            produto_obj.save()

                        except Exception as erro_produto:

                            self.stdout.write(
                                self.style.ERROR(
                                    f'Erro ao salvar produto: {erro_produto}'
                                )
                            )
    
    def coletar_dolar(self):

        try:

            hoje = datetime.now()
            ontem = hoje - timedelta(days=1)

            url = (
                "https://olinda.bcb.gov.br/olinda/servico/PTAX/"
                "versao/v1/odata/"
                "CotacaoMoedaPeriodo(moeda=@moeda,"
                "dataInicial=@dataInicial,"
                "dataFinalCotacao=@dataFinal)?"
                f"@moeda='USD'&"
                f"@dataInicial='{ontem.strftime('%m-%d-%Y')}'&"
                f"@dataFinal='{hoje.strftime('%m-%d-%Y')}'&"
                "$top=1&"
                "$orderby=dataHoraCotacao desc&"
                "$format=json"
            )

            response = requests.get(url, timeout=10)

            response.raise_for_status()

            dados = response.json()

            if not dados["value"]:
                raise Exception("Nenhuma cotação retornada")

            cotacao = Decimal(
                str(
                    dados["value"][0]["cotacaoVenda"]
                )
            )

            CotacaoDolar.objects.create(
                valor=cotacao
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Dólar salvo: R$ {cotacao}"
                )
            )

        except Exception as erro:

            self.stdout.write(
                self.style.ERROR(
                    f"Erro ao coletar dólar: {erro}"
                )
            )

            return None
            
    # =====================================================
    # BUSCAR PRODUTOS
    # =====================================================

    def pegar_produtos(self, produto, source):

        query = produto

        self.stdout.write(
            self.style.WARNING(f'BUSCANDO: {query} | SOURCE: {source}')
        )

        try:

            # =====================================
            # PAYLOAD
            # =====================================

            payload = {
                'source': source,
                'query': query,
                'render': 'html',
                'browser_instructions': [
                    {
                        'type': 'wait',
                        'wait_time_s': 5
                    }
                ]
            }

            response = requests.post(
                self.BASE_URL,
                auth=(USERNAME, PASSWORD),
                json=payload,
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

            query_id = data.get('id')

            # =====================================
            # VALIDA QUERY ID
            # =====================================

            if not query_id:

                self.stdout.write(
                    self.style.ERROR(
                        'Não foi possível obter o ID da query'
                    )
                )

                return []

            self.stdout.write(
                self.style.SUCCESS(
                    f'QUERY ID: {query_id}'
                )
            )

            # =====================================
            # AGUARDA PROCESSAMENTO
            # =====================================

            status = 'pending'

            tentativas = 0

            while status in ['pending', 'processing'] and tentativas < 30:

                time.sleep(5)

                status_response = requests.get(
                    f'{self.BASE_URL}/{query_id}',
                    auth=(USERNAME, PASSWORD),
                    timeout=30
                )

                status_response.raise_for_status()

                status_data = status_response.json()

                status = status_data.get('status')

                tentativas += 1

                self.stdout.write(
                    self.style.WARNING(
                        f'STATUS: {status}'
                    )
                )

            # =====================================
            # STATUS FINAL
            # =====================================

            if status != 'done':

                self.stdout.write(
                    self.style.ERROR(
                        'Consulta não finalizou'
                    )
                )

                return []

            # =====================================
            # RESULTADOS
            # =====================================

            result_response = requests.get(
                f'{self.BASE_URL}/{query_id}/results',
                auth=(USERNAME, PASSWORD),
                timeout=30
            )

            result_response.raise_for_status()

            result_data = result_response.json()

            # =====================================
            # VALIDA RESULTADOS
            # =====================================

            if not result_data.get('results'):

                self.stdout.write(
                    self.style.ERROR(
                        'Nenhum resultado retornado'
                    )
                )

                return []

            html = result_data['results'][0]['content']
            with open(f'{source}.html', 'w', encoding='utf-8') as f:
                      f.write(html)

            soup = BeautifulSoup(
                html,
                'html.parser'
            )

            # =====================================
            # ESCOLHE CARDS POR LOJA
            # =====================================

            cards = []

            if source == 'amazon_search':

                cards = soup.find_all(
                    'div',
                    {'data-component-type': 's-search-result'}
                )

            elif source == 'mercadolivre_search':

                cards = soup.select(
                    'li.ui-search-layout__item'
                )
                

            elif source == 'google_shopping_search':

                cards = soup.find_all(
                    'div',
                    class_='sh-dgr__grid-result'
                )

            else:

                self.stdout.write(
                    self.style.ERROR(
                        f'Source não suportada: {source}'
                    )
                )

                return []

            produtos = []

            # =====================================
            # LOOP DOS CARDS
            # =====================================

            for card in cards:

                try:

                    titulo = None
                    preco = None
                    imagem = None
                    link = None
                    avaliacao = None

                    # =====================================
                    # AMAZON
                    # =====================================

                    if source == 'amazon_search':

                        titulo = card.find('h2')

                        preco = card.find(
                            'span',
                            class_='a-price-whole'
                        )

                        imagem = card.find(
                            'img',
                            class_='s-image'
                        )

                        link = card.find(
                            'a',
                            class_='a-link-normal'
                        )

                        avaliacao = card.find(
                            'span',
                            class_='a-icon-alt'
                        )

                        produto_dict = {

                            'titulo': (
                                titulo.get_text(strip=True)
                                if titulo else None
                            ),

                            'preco': (
                                preco.text.strip()
                                if preco else None
                            ),

                            'imagem': (
                                imagem.get('src')
                                if imagem else None
                            ),

                            'url': (
                                'https://amazon.com' + link.get('href')
                                if link and link.get('href')
                                else None
                            ),

                            'avaliacao': (
                                avaliacao.text.strip()
                                if avaliacao else None
                            )
                        }

                    # =====================================
                    # MERCADO LIVRE
                    # =====================================

                    elif source == 'mercadolivre_search':

                        titulo = card.select_one(
                            'a.poly-component__title'
                        )

                        preco = card.select_one(
                            'span.andes-money-amount__fraction'
                        )

                        imagem = card.select_one('img')

                        link = card.select_one('a')

                        produto_dict = {

                            'titulo': (
                                titulo.get_text(strip=True)
                                if titulo else None
                            ),

                            'preco': (
                                preco.text.strip()
                                if preco else None
                            ),

                            'imagem': (
                                imagem.get('src')
                                if imagem else None
                            ),

                            'url': (
                                link.get('href')
                                if link else None
                            ),

                            'avaliacao': None
                        }

                    # =====================================
                    # VALIDAÇÕES
                    # =====================================

                    if (
                        produto_dict['titulo']
                        and produto_dict['preco']
                        and produto_dict['url']
                    ):

                        produtos.append(produto_dict)

                except Exception as erro_card:

                    self.stdout.write(
                        self.style.WARNING(
                            f'Erro card: {erro_card}'
                        )
                    )

            # =====================================
            # TOTAL
            # =====================================

            self.stdout.write(
                self.style.SUCCESS(
                    f'TOTAL PRODUTOS: {len(produtos)}'
                )
            )

            return produtos

        # =====================================
        # REQUEST ERROR
        # =====================================

        except requests.RequestException as erro_request:

            self.stdout.write(
                self.style.ERROR(
                    f'Erro HTTP: {erro_request}'
                )
            )

            return []

        # =====================================
        # ERRO GERAL
        # =====================================

        except Exception as erro:

            self.stdout.write(
                self.style.ERROR(
                    f'ERRO GERAL: {erro}'
                )
            )

            return []
