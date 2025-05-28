import streamlit as st
from datetime import datetime
import os

# ========================== Funções ==========================

def salvar_produto(nome, preco, estoque):
    with open('produtos.txt', 'a', encoding='utf-8') as f:
        f.write(f'{nome};{preco};{estoque}\n')
    st.success('✅ Produto cadastrado com sucesso!')


def carregar_produtos():
    produtos = []
    if os.path.exists('produtos.txt'):
        with open('produtos.txt', 'r', encoding='utf-8') as f:
            for linha in f:
                nome, preco, estoque = linha.strip().split(';')
                produtos.append({'nome': nome, 'preco': float(preco), 'estoque': int(estoque)})
    return produtos


def salvar_venda(itens, total):
    data = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('vendas.txt', 'a', encoding='utf-8') as f:
        for item in itens:
            f.write(f'{data};{item["nome"]};{item["quantidade"]};{item["subtotal"]}\n')
    st.success(f'✅ Venda concluída! Total: R${total:.2f}')


def atualizar_estoque(nome, quantidade):
    produtos = carregar_produtos()
    with open('produtos.txt', 'w', encoding='utf-8') as f:
        for p in produtos:
            if p['nome'] == nome:
                p['estoque'] -= quantidade
            f.write(f'{p["nome"]};{p["preco"]};{p["estoque"]}\n')


# ========================== Interface ==========================

st.set_page_config(page_title="🦊 Mony Cash", layout="centered")
st.title("🦊 Mony Cash - Sistema de Vendas")

menu = st.sidebar.selectbox("Menu", ["📦 Cadastro de Produto", "📑 Estoque", "🛒 Venda", "📊 Relatórios"])

# Cadastro de Produto
if menu == "📦 Cadastro de Produto":
    st.subheader("📦 Cadastro de Produto")

    nome = st.text_input("Nome do Produto")
    preco = st.number_input("Preço", min_value=0.0, format="%.2f")
    estoque = st.number_input("Estoque", min_value=0, step=1)

    if st.button("Cadastrar Produto"):
        if nome:
            salvar_produto(nome, preco, estoque)
        else:
            st.error("❌ Informe o nome do produto!")

# Estoque
elif menu == "📑 Estoque":
    st.subheader("📑 Estoque Atual")

    produtos = carregar_produtos()
    if produtos:
        estoque_data = {
            "Produto": [p['nome'] for p in produtos],
            "Preço (R$)": [f"R${p['preco']:.2f}" for p in produtos],
            "Estoque": [p['estoque'] for p in produtos]
        }
        st.table(estoque_data)
    else:
        st.info("⚠️ Nenhum produto cadastrado.")

# Venda
elif menu == "🛒 Venda":
    st.subheader("🛒 Realizar Venda")

    produtos = carregar_produtos()

    if produtos:
        produto_nomes = [p['nome'] for p in produtos]
        carrinho = []
        total = 0.0

        with st.form("form_venda"):
            produto_selecionado = st.selectbox("Selecione o Produto", produto_nomes)
            quantidade = st.number_input("Quantidade", min_value=1, step=1)

            adicionar = st.form_submit_button("Adicionar ao Carrinho")

            if adicionar:
                produto = next((p for p in produtos if p['nome'] == produto_selecionado), None)

                if produto and quantidade <= produto['estoque']:
                    subtotal = produto['preco'] * quantidade
                    carrinho.append({'nome': produto['nome'], 'quantidade': quantidade, 'subtotal': subtotal})
                    total += subtotal
                    st.success(f"Adicionado: {produto['nome']} x{quantidade} = R${subtotal:.2f}")
                else:
                    st.error("❌ Estoque insuficiente ou produto não encontrado.")

        if 'carrinho' not in st.session_state:
            st.session_state.carrinho = []
            st.session_state.total = 0.0

        if adicionar:
            st.session_state.carrinho.append({
                'nome': produto_selecionado,
                'quantidade': quantidade,
                'subtotal': next(p['preco'] for p in produtos if p['nome'] == produto_selecionado) * quantidade
            })
            st.session_state.total += next(p['preco'] for p in produtos if p['nome'] == produto_selecionado) * quantidade

        if st.session_state.carrinho:
            st.subheader("🛍️ Carrinho")
            for item in st.session_state.carrinho:
                st.text(f'{item["nome"]} x{item["quantidade"]} = R${item["subtotal"]:.2f}')
            st.text(f"💰 Total: R${st.session_state.total:.2f}")

            if st.button("Finalizar Venda"):
                for item in st.session_state.carrinho:
                    atualizar_estoque(item['nome'], item['quantidade'])
                salvar_venda(st.session_state.carrinho, st.session_state.total)
                st.session_state.carrinho = []
                st.session_state.total = 0.0

    else:
        st.info("⚠️ Nenhum produto cadastrado.")

# Relatórios
elif menu == "📊 Relatórios":
    st.subheader("📊 Relatório de Vendas")

    if os.path.exists('vendas.txt'):
        with open('vendas.txt', 'r', encoding='utf-8') as f:
            linhas = f.readlines()

        if linhas:
            for linha in linhas:
                data, nome, qtd, subtotal = linha.strip().split(';')
                st.text(f'{data} - {nome} x{qtd} = R${float(subtotal):.2f}')
        else:
            st.info("⚠️ Nenhuma venda registrada.")
    else:
        st.info("⚠️ Nenhuma venda registrada.")
