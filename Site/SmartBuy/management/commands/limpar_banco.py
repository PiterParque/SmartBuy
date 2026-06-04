from django.core.management.base import BaseCommand
from SmartBuy.models import Produto, HistoricoPreco


class Command(BaseCommand):

    help = "Apagar produtos e/ou histórico"

    def handle(self, *args, **kwargs):

        print("\n=== LIMPEZA DO BANCO ===\n")

        print("1 - Apagar TODOS os produtos e históricos")
        print("2 - Apagar apenas produtos")
        print("3 - Apagar apenas histórico")
        print("4 - Cancelar\n")

        escolha = input("Escolha uma opção: ")

        # =========================================
        # APAGAR TUDO
        # =========================================

        if escolha == "1":

            confirmar = input(
                "\nTem certeza que deseja apagar TUDO? (s/n): "
            )

            if confirmar.lower() == "s":

                total_historico = HistoricoPreco.objects.count()
                total_produtos = Produto.objects.count()

                HistoricoPreco.objects.all().delete()
                Produto.objects.all().delete()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n{total_produtos} produtos apagados"
                    )
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"{total_historico} históricos apagados"
                    )
                )

            else:

                print("\nOperação cancelada")

        # =========================================
        # APAGAR PRODUTOS
        # =========================================

        elif escolha == "2":

            confirmar = input(
                "\nTem certeza que deseja apagar os produtos? (s/n): "
            )

            if confirmar.lower() == "s":

                total_produtos = Produto.objects.count()

                Produto.objects.all().delete()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n{total_produtos} produtos apagados"
                    )
                )

            else:

                print("\nOperação cancelada")

        # =========================================
        # APAGAR HISTÓRICO
        # =========================================

        elif escolha == "3":

            confirmar = input(
                "\nTem certeza que deseja apagar o histórico? (s/n): "
            )

            if confirmar.lower() == "s":

                total_historico = HistoricoPreco.objects.count()

                HistoricoPreco.objects.all().delete()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n{total_historico} históricos apagados"
                    )
                )

            else:

                print("\nOperação cancelada")

        # =========================================
        # CANCELAR
        # =========================================

        elif escolha == "4":

            print("\nOperação cancelada")

        else:

            print("\nOpção inválida")