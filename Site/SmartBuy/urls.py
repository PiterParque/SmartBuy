
from django.urls import path
from SmartBuy import views

urlpatterns = [
    path("",views.index,name="index"),
    path("MelhoresAvaliacoes",views.produtos_melhores_avaliacoes,name="melhores_avaliacoes"),
    path("product/<int:id>",views.produto,name="produto"),
    path("lista",views.pesquisar,name="pesquisa"),
    path("categoria/<str:categoria>",views.categoria,name="categoria"),
    path("loja/<str:loja>",views.loja,name="loja"),
    path("queda/",views.queda_preco,name="queda"),
    path("marcas/<str:marca>",views.marcas,name="marcas"),
    path("alerta/<int:produto_id>/",views.criar_alerta,name="criar_alerta")
    
]