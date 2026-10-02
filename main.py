from database import inicializar_banco
from produtos import cadastrar_bateria, listar_estoque, editar_bateria
from vendas import realizar_venda, relatorio_vendas, consultar_garantia, listar_vendas, gerenciar_vendas_adm

SENHA_ADM = "1234"  # <-- Altere para a senha do seu pai

def verificar_senha():
    senha = input("\n🔒 Digite a senha de Administrador: ").strip()
    if senha == SENHA_ADM:
        return True
    print("\n❌ Senha incorreta! Acesso negado.")
    return False

def painel_adm():
    if not verificar_senha():
        return

    while True:
        print("\n" + "="*40)
        print("       🔐 PAINEL DO ADMINISTRADOR       ")
        print("="*40)
        print("1. Cadastrar Nova Bateria")
        print("2. Editar / Ajustar Estoque de Bateria")
        print("3. Corrigir / Cancelar Venda (Estorno)")
        print("4. Ver Relatório de Faturamento e Vendedores")
        print("0. Voltar ao Menu Principal")
        print("="*40)
        
        opcao = input("\n[ADM] Escolha uma opção: ").strip()

        if opcao == "1":
            cadastrar_bateria()
        elif opcao == "2":
            editar_bateria()
        elif opcao == "3":
            gerenciar_vendas_adm()
        elif opcao == "4":
            relatorio_vendas()
        elif opcao == "0":
            print("\nSaindo do Painel ADM...")
            break
        else:
            print("\nOpção inválida!")

def menu_principal():
    inicializar_banco()
    while True:
        print("\n=== SISTEMA POWER BATERIAS ===")
        print("1. Consultar Estoque")
        print("2. Lançar Venda (Baixa Automática)")
        print("3. Ver Histórico de Vendas")
        print("4. Consultar Garantia (Placa/Nº Série)")
        print("5. 🔐 Área do Administrador (ADM)")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            listar_estoque()
        elif opcao == "2":
            realizar_venda()
        elif opcao == "3":
            listar_vendas()
        elif opcao == "4":
            consultar_garantia()
        elif opcao == "5":
            painel_adm()
        elif opcao == "0":
            print("\nSaindo do sistema... Até logo!")
            break
        else:
            print("\nOpção inválida! Tente novamente.")

if __name__ == "__main__":
    menu_principal()