import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Inicializar Firebase desde secrets
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))
    firebase_admin.initialize_app(cred)

db = firestore.client()

columnas_ordenadas = ['user_id', 'name', 'address', 'phone', 'website', 'rating', 'city', 'state', 'country', 'status']
status_lista = ["Novo", "Contato Feito", "Em Negociação", "Cliente", "Descartado", "Não conferido"]

# Carregar leads do Firestore
def carregar_leads():
    docs = db.collection("leads").stream()
    dados = [doc.to_dict() for doc in docs]
    return pd.DataFrame(dados, columns=columnas_ordenadas)

# Atualizar status no Firestore
def atualizar_status(user_id, novo_status):
    docs = db.collection("leads").where("user_id", "==", user_id).stream()
    for doc in docs:
        db.collection("leads").document(doc.id).update({"status": novo_status})
        return True
    return False

df = carregar_leads()

# Adiciona link de WhatsApp
def gerar_link_whatsapp(numero):
    numero_limpo = ''.join(filter(str.isdigit, str(numero)))
    return f"https://wa.me/+55{numero_limpo}" if numero_limpo else ""

df["whatsapp"] = df["phone"].apply(gerar_link_whatsapp)

# Interface do usuário
st.title("CRM de Leads - Oficinas Mecânicas")

with st.sidebar:
    st.header("Filtros")
    status_opcao = st.selectbox("Filtrar por status:", ["Todos"] + sorted(df["status"].dropna().unique()))
    pais_opcao = st.selectbox("Filtrar por país:", ["Todos"] + sorted(df["country"].dropna().unique()))
    estado_opcao = st.selectbox("Filtrar por estado:", ["Todos"] + sorted(df["state"].dropna().unique()))
    cidade_opcao = st.selectbox("Filtrar por cidade:", ["Todas"] + sorted(df["city"].dropna().unique()))

# Aplicar filtros
filtro = df.copy()
if status_opcao != "Todos":
    filtro = filtro[filtro["status"] == status_opcao]
if pais_opcao != "Todos":
    filtro = filtro[filtro["country"] == pais_opcao]
if estado_opcao != "Todos":
    filtro = filtro[filtro["state"] == estado_opcao]
if cidade_opcao != "Todas":
    filtro = filtro[filtro["city"] == cidade_opcao]

quantidade = len(filtro)
texto_status = f"{status_opcao.lower()}" if status_opcao != "Todos" else ""
texto_cidade = f" na cidade de {cidade_opcao}" if cidade_opcao != "Todas" else ""
texto_estado = f" no estado de {estado_opcao}" if estado_opcao != "Todos" else ""
texto_pais = f" no país {pais_opcao}" if pais_opcao != "Todos" else ""

mensagem = f"Você tem {quantidade} contato{'s' if quantidade != 1 else ''}"
if texto_status:
    mensagem += f" {texto_status}"
if texto_cidade:
    mensagem += texto_cidade
elif texto_estado:
    mensagem += texto_estado
elif texto_pais:
    mensagem += texto_pais

st.markdown(f"**{mensagem}**")

st.markdown("### Resultados")
for index, row in filtro.iterrows():
    st.markdown(f"**{row['name']}**")
    st.markdown(f"Endereço: {row['address']}")
    st.markdown(f"Site: [{row['website']}]({row['website']})" if row['website'] else "Site: N/A")
    st.markdown(f"Cidade: {row['city']} | Estado: {row['state']} | País: {row['country']}")

    if row['whatsapp']:
        st.markdown(f"[Enviar mensagem no WhatsApp]({row['whatsapp']})")
    else:
        st.markdown("WhatsApp: N/A")

    novo_status = st.selectbox(f"Status de {row['name']}:", status_lista,
                               index=status_lista.index(row['status']) if row['status'] in status_lista else 0,
                               key=f"status_{index}")
    
    if novo_status != row['status']:
        sucesso = atualizar_status(row["user_id"], novo_status)
        if sucesso:
            st.success(f"Status atualizado para {row['name']}")
        else:
            st.error(f"Erro ao atualizar status de {row['name']}")
    st.markdown("---")
