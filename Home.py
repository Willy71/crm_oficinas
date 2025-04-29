
import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

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

# Adiciona link de WhatsApp
def gerar_link_whatsapp(numero):
    numero_limpo = ''.join(filter(str.isdigit, str(numero)))
    return f"https://wa.me/+55{numero_limpo}" if numero_limpo else ""

st.title("CRM de Leads - Oficinas Mecânicas")

with st.sidebar:
    st.header("Filtros")
    status_opcao = st.selectbox("Filtrar por status:", ["Todos"] + status_lista)
    pais_opcao = st.text_input("Filtrar por país:")
    estado_opcao = st.text_input("Filtrar por estado:")
    cidade_opcao = st.text_input("Filtrar por cidade:")
    aplicar_filtro = st.button("Filtrar")

if aplicar_filtro:
    df = carregar_leads()
    df["whatsapp"] = df["phone"].apply(gerar_link_whatsapp)

    # Aplicar filtros
    filtro = df.copy()
    if status_opcao != "Todos":
        filtro = filtro[filtro["status"] == status_opcao]
    if pais_opcao:
        filtro = filtro[filtro["country"].str.lower() == pais_opcao.lower()]
    if estado_opcao:
        filtro = filtro[filtro["state"].str.lower() == estado_opcao.lower()]
    if cidade_opcao:
        filtro = filtro[filtro["city"].str.lower() == cidade_opcao.lower()]

    quantidade = len(filtro)
    st.markdown(f"**Você tem {quantidade} contato{'s' if quantidade != 1 else ''}**")
    
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
else:
    st.info("Use os filtros à esquerda e clique em **Filtrar** para ver os resultados.")
