import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import re

# Conectar ao banco de dados
def conectar():
    return sqlite3.connect('containers.db')

# Criar a tabela de containers, se não existir
def criar_tabela():
    conn = conectar()
    c = conn.cursor()
    c.execute(''' 
        CREATE TABLE IF NOT EXISTS containers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL,
            pano TEXT NOT NULL,
            localizacao TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Validar o número do container (4 dígitos)
def validar_numero(numero):
    if len(numero) == 4 and numero.isdigit():
        return True
    return False

# Validar a localização do container (formato 000-000)
def validar_localizacao(localizacao):
    if re.match(r'^\d{3}-\d{3}$', localizacao):
        return True
    return False

# Função para formatar o número do container (apenas 4 dígitos)
def formatar_numero(event):
    numero = numero_entry.get().replace("-", "")  # Remover qualquer hífen existente
    if len(numero) > 4:  # Impede que o usuário digite mais de 4 números
        numero = numero[:4]
    numero_entry.delete(0, tk.END)  # Apagar o conteúdo atual do campo
    numero_entry.insert(0, numero)  # Inserir o número formatado

# Função para formatar a localização (adicionando o hífen automaticamente)
def formatar_localizacao(event):
    localizacao = localizacao_entry.get().replace("-", "")  # Remover hífens existentes
    if len(localizacao) > 6:  # Impede que o usuário digite mais de 6 números
        localizacao = localizacao[:6]
    if len(localizacao) > 3:
        localizacao = localizacao[:3] + "-" + localizacao[3:]
    localizacao_entry.delete(0, tk.END)  # Apagar o conteúdo atual do campo
    localizacao_entry.insert(0, localizacao)  # Inserir a nova localização formatada

# Cadastrar um novo container
def cadastrar_container():
    numero = numero_entry.get()
    pano = pano_entry.get()
    localizacao = localizacao_entry.get()

    if not validar_numero(numero):
        messagebox.showerror("Erro", "O número do container deve ter 4 dígitos!")
        return
    
    if not validar_localizacao(localizacao):
        messagebox.showerror("Erro", "A localização deve seguir o formato '000-000'!")
        return

    conn = conectar()
    try:
        c = conn.cursor()
        c.execute(''' 
            INSERT INTO containers (numero, pano, localizacao)
            VALUES (?, ?, ?) 
        ''', (numero, pano, localizacao))
        conn.commit()
        messagebox.showinfo("Sucesso", "Container cadastrado com sucesso!")
        atualizar_lista()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao cadastrar container: {e}")
    finally:
        conn.close()

# Atualizar a lista de containers (sem filtro por localização)
def atualizar_lista():
    tree.delete(*tree.get_children())  # Limpar a tabela de exibição
    conn = conectar()
    try:
        c = conn.cursor()
        termo_pesquisa = search_entry.get()
        
        # Apenas containers com localizações cadastradas serão buscados
        query = 'SELECT numero, pano, localizacao FROM containers WHERE 1=1'
        params = []
        
        if termo_pesquisa:
            query += ' AND localizacao LIKE ?'
            params.append('%' + termo_pesquisa + '%')
        
        c.execute(query, params)
        containers = c.fetchall()
        for container in containers:
            tree.insert('', 'end', values=(container[0], container[1], container[2]))
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao consultar containers: {e}")
    finally:
        conn.close()

# Deletar um container
def deletar_container():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Erro", "Selecione um container para deletar!")
        return

    container_id = tree.item(selected_item)['values'][0]
    if messagebox.askyesno("Confirmar Exclusão", "Você tem certeza que deseja excluir este container?"):
        conn = conectar()
        try:
            c = conn.cursor()
            c.execute('DELETE FROM containers WHERE numero = ?', (container_id,))
            conn.commit()
            messagebox.showinfo("Sucesso", "Container deletado com sucesso!")
            atualizar_lista()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao deletar container: {e}")
        finally:
            conn.close()

# Função para exibir a tela de containers
def exibir_containers():
    cadastro_frame.pack_forget()  # Esconde a tela de cadastro
    exibicao_frame.pack(fill="both", expand=True)  # Exibe a tela de exibição

# Função para voltar para o cadastro
def voltar_para_cadastro():
    exibicao_frame.pack_forget()  # Esconde a tela de exibição
    cadastro_frame.pack(fill="both", expand=True)  # Exibe a tela de cadastro

# Criar a interface gráfica
root = tk.Tk()
root.title("Cadastro de Containers")
root.geometry("631x405")  # Tamanho inicial ajustado para 631x405 pixels
root.resizable(True, True)  # Permite que a janela seja redimensionada
root.config(bg="#f5f5f5")  # Cor de fundo agradável

# Tela de Cadastro
cadastro_frame = tk.Frame(root, bg="#f5f5f5")
cadastro_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Labels e campos de entrada para o cadastro
numero_label = tk.Label(cadastro_frame, text="Número do Container (4 dígitos):", bg="#f5f5f5")
numero_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
numero_entry = tk.Entry(cadastro_frame, font=("Arial", 12))
numero_entry.grid(row=0, column=1, padx=10, pady=5)
numero_entry.bind("<KeyRelease>", formatar_numero)  # Chama a função de formatação para o número

pano_label = tk.Label(cadastro_frame, text="Pano:", bg="#f5f5f5")
pano_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
pano_entry = tk.Entry(cadastro_frame, font=("Arial", 12))
pano_entry.grid(row=1, column=1, padx=10, pady=5)

localizacao_label = tk.Label(cadastro_frame, text="Localização (Formato 000-000):", bg="#f5f5f5")
localizacao_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
localizacao_entry = tk.Entry(cadastro_frame, font=("Arial", 12))
localizacao_entry.grid(row=2, column=1, padx=10, pady=5)
localizacao_entry.bind("<KeyRelease>", formatar_localizacao)  # Chama a função de formatação para a localização

# Botões para ações no cadastro
buttons_frame = tk.Frame(cadastro_frame, bg="#f5f5f5")
buttons_frame.grid(row=3, column=0, columnspan=2, pady=10)

cadastrar_button = ttk.Button(buttons_frame, text="Cadastrar Container", command=cadastrar_container)
cadastrar_button.grid(row=0, column=0, padx=10, pady=5)

# Botão para exibir containers
exibir_button = ttk.Button(cadastro_frame, text="Exibir Containers", command=exibir_containers)
exibir_button.grid(row=4, column=0, columnspan=2, pady=10)

# Tela de Exibição
exibicao_frame = tk.Frame(root, bg="#f5f5f5")
exibicao_frame.pack_forget()

# Caixa de pesquisa e treeview
search_label = tk.Label(exibicao_frame, text="Pesquisar:", bg="#f5f5f5")
search_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
search_entry = tk.Entry(exibicao_frame, font=("Arial", 12))
search_entry.grid(row=0, column=1, padx=10, pady=10)

# Botão para pesquisar containers
search_button = ttk.Button(exibicao_frame, text="Pesquisar", command=atualizar_lista)
search_button.grid(row=0, column=2, padx=10, pady=10)

# Treeview para exibir containers cadastrados
columns = ("numero", "pano", "localizacao")  # Removendo a coluna "id"
tree = ttk.Treeview(exibicao_frame, columns=columns, show="headings")
tree.heading("numero", text="Número")
tree.heading("pano", text="Pano")
tree.heading("localizacao", text="Localização")
tree.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

# Botão para excluir container
deletar_button = ttk.Button(exibicao_frame, text="Deletar Container", command=deletar_container)
deletar_button.grid(row=4, column=0, columnspan=3, pady=10)

# Botão para voltar para o cadastro
voltar_button = ttk.Button(exibicao_frame, text="Voltar para Cadastro", command=voltar_para_cadastro)
voltar_button.grid(row=5, column=0, columnspan=3, pady=10)

# Iniciar a aplicação
criar_tabela()  # Apenas cria a tabela se não existir
atualizar_lista()  # Atualiza a lista de containers cadastrados

root.mainloop()
