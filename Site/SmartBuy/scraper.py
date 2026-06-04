# produtos/scraper.py

import requests
from bs4 import BeautifulSoup

URL = "https://site.com/produtos"

def pegar_produtos():
    response = requests.get(URL)

    soup = BeautifulSoup(response.text, "html.parser")

    produtos = []

    cards = soup.find_all("div", class_="produto")

    for card in cards:
        nome = card.find("h2").text.strip()

        preco = (
            card.find("span", class_="preco")
            .text
            .replace("R$", "")
            .replace(".", "")
            .replace(",", ".")
            .strip()
        )

        link = card.find("a")["href"]

        produtos.append({
            "nome": nome,
            "preco": float(preco),
            "link": link
        })

    return produtos