# Importar as Bibliotecas
import tkinter as tk
from tkinter import ttk
import sqlite3
from sqlite3 import Error

class Sistema:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Cadastro")

        # Criar tabela no banco de dados
        self.criar_tabela()

        # Itens da interface
        self.label_nome = ttk.Label(root, text="Nome do Produto:")
        self.entry_nome = ttk.Entry(root)

        self.label_preco = ttk.Label(root, text="Preço do Produto:")
        self.entry_preco = ttk.Entry(root)

        self.botao_adicionar = ttk.Button(root, text="Adicionar Produto", command=self.adicionar_produto)

        self.label_resultado = ttk.Label(root, text="Preço com Acréscimo (10%):")

        # Lista de produtos
        self.lista_produtos = tk.Listbox(root)
        self.lista_produtos.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

        # Criação dos botões Editar e Excluir
        self.botao_editar = ttk.Button(root, text="Editar", command=self.editar_produto)
        self.botao_excluir = ttk.Button(root, text="Excluir", command=self.excluir_produto)

        # Posição dos elementos 
        self.label_nome.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        self.entry_nome.grid(row=0, column=1, padx=10, pady=5)

        self.label_preco.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        self.entry_preco.grid(row=1, column=1, padx=10, pady=5)

        self.botao_adicionar.grid(row=2, column=0, columnspan=2, pady=10)

        self.label_resultado.grid(row=3, column=0, columnspan=2, pady=5)

        self.botao_editar.grid(row=5, column=0, pady=5)
        self.botao_excluir.grid(row=5, column=1, pady=5)

        # Atualizar a lista de produtos
        self.atualizar_lista_produtos()

    # Criar tabela
    def criar_tabela(self):
       
        
        conn = sqlite3.connect('cadastro.db')
        cursor = conn.cursor()
        
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    preco REAL
                )
            ''')
        conn.commit()
        conn.close()
            

    # Adicionar Produto
    def adicionar_produto(self):
        nome = self.entry_nome.get()
        preco = float(self.entry_preco.get())

        # Inserir produto no banco de dados
        self.inserir_produto(nome, preco)

        # Atualizar a lista de produtos
        self.atualizar_lista_produtos()

        # Atualizar a label com o preço acrescido
        id_produto = self.obter_ultimo_id()
        preco_acrescido = self.calcular_acrescimo(preco)
        self.atualizar_preco_label(preco_acrescido)

    # Inserir o produto
    def inserir_produto(self, nome, preco):
        conn = sqlite3.connect('cadastro.db')
        cursor = conn.cursor()

        cursor.execute('INSERT INTO produtos (nome, preco) VALUES (?, ?)', (nome, preco))

        conn.commit()
        conn.close()

    # Calcular o acrescimo
    def calcular_acrescimo(self, preco):
        return preco * 1.1

    def obter_ultimo_id(self):
        conn = sqlite3.connect('cadastro.db')
        cursor = conn.cursor()

        cursor.execute('SELECT MAX(id) FROM produtos')
        ultimo_id = cursor.fetchone()[0]

        conn.close()

        return ultimo_id

    def atualizar_lista_produtos(self):
        conn = sqlite3.connect('cadastro.db')
        cursor = conn.cursor()

        # Limpar a lista antes de atualizar
        self.lista_produtos.delete(0, tk.END)

        # Obter todos os produtos
        cursor.execute('SELECT id, nome FROM produtos')
        produtos = cursor.fetchall()

        # Adicionar os nomes dos produtos à lista
        for produto in produtos:
            self.lista_produtos.insert(tk.END, f"{produto[1]} (ID: {produto[0]})")

        conn.close()

    def atualizar_preco_label(self, preco_acrescido):
        self.label_resultado.config(text=f"Preço com Acréscimo (10%): R$ {preco_acrescido:.2f}")

    def editar_produto(self):
        # Obter o item selecionado na lista
        selecao = self.lista_produtos.curselection()

        if selecao:
            id_produto = int(self.lista_produtos.get(selecao[0]).split("(ID: ")[1][:-1])
            
            # Abrir uma nova janela para editar o produto
            janela_edicao = tk.Toplevel(self.root)
            janela_edicao.title("Editar Produto")

            # Elementos da janela de edição
            label_novo_nome = ttk.Label(janela_edicao, text="Novo Nome:")
            entry_novo_nome = ttk.Entry(janela_edicao)

            label_novo_preco = ttk.Label(janela_edicao, text="Novo Preço:")
            entry_novo_preco = ttk.Entry(janela_edicao)

            botao_salvar_edicao = ttk.Button(janela_edicao, text="Salvar Edição", command=lambda: self.salvar_edicao(id_produto, entry_novo_nome.get(), entry_novo_preco.get(), janela_edicao))

            # Posicionamento dos elementos na janela de edição
            label_novo_nome.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
            entry_novo_nome.grid(row=0, column=1, padx=10, pady=5)

            label_novo_preco.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
            entry_novo_preco.grid(row=1, column=1, padx=10, pady=5)

            botao_salvar_edicao.grid(row=2, column=0, columnspan=2, pady=10)

    def salvar_edicao(self, id_produto, novo_nome, novo_preco, janela_edicao):
        # Atualizar o produto no banco de dados
        conn = sqlite3.connect('cadastro.db')
        cursor = conn.cursor()

        cursor.execute('UPDATE produtos SET nome = ?, preco = ? WHERE id = ?', (novo_nome, float(novo_preco), id_produto))

        conn.commit()
        conn.close()

        # Atualizar a lista de produtos
        self.atualizar_lista_produtos()

        # Fechar a janela de edição
        janela_edicao.destroy()

    def excluir_produto(self):
        # Obter o item selecionado na lista
        selecao = self.lista_produtos.curselection()

        if selecao:
            id_produto = int(self.lista_produtos.get(selecao[0]).split("(ID: ")[1][:-1])

            # Excluir o produto do banco de dados
            conn = sqlite3.connect('cadastro.db')
            cursor = conn.cursor()

            cursor.execute('DELETE FROM produtos WHERE id = ?', (id_produto,))

            conn.commit()
            conn.close()

            # Atualizar a lista de produtos
            self.atualizar_lista_produtos()


if __name__ == "__main__":
    root = tk.Tk()
    app = Sistema(root)
    root.mainloop()
# Fim
