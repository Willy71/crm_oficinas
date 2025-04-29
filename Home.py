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

# Carregar opções únicas para filtros
def carregar_opcoes_unicas(campo):
    docs = db.collection("leads").select([campo]).stream()
    valores = set()
    for doc in docs:
        data = doc.to_dict()
        if campo in data and data[campo]:
            valores.add(data[campo])
    return sorted(valores)

# Adiciona link de WhatsApp
def gerar_link_whatsapp(numero):
    numero_limpo = ''.join(filter(str.isdigit, str(numero)))
    return f"https://wa.me/+55{numero_limpo}" if numero_limpo else ""

st.title("CRM de Leads - Oficinas Mecânicas")

with st.sidebar:
    st.header("Filtros")
    status_opcao = st.selectbox("Filtrar por status:", ["Todos"] + status_lista)
    pais_opcao = st.selectbox("Filtrar por país:", ["Todos"] + carregar_opcoes_unicas("country"))
    estado_opcao = st.selectbox("Filtrar por estado:", ["Todos"] + carregar_opcoes_unicas("state"))
    cidade_opcao = st.selectbox("Filtrar por cidade:", ["Todas"] + carregar_opcoes_unicas("city"))
    if st.button("Filtrar"):
        df = carregar_leads()
        df["whatsapp"] = df["phone"].apply(gerar_link_whatsapp)
        if status_opcao != "Todos":
            df = df[df["status"] == status_opcao]
        if pais_opcao != "Todos":
            df = df[df["country"] == pais_opcao]
        if estado_opcao != "Todos":
            df = df[df["state"] == estado_opcao]
        if cidade_opcao != "Todas":
            df = df[df["city"] == cidade_opcao]
        st.session_state["dados_filtrados"] = df.reset_index(drop=True)

# Recuperar datos da sessão
filtro = st.session_state.get("dados_filtrados", None)

if filtro is not None and not filtro.empty:
    quantidade = len(filtro)
    st.markdown(f"**Você tem {quantidade} contato{'s' if quantidade != 1 else ''}**")
    st.markdown("### Resultados")
    for index in range(len(filtro)):
        row = filtro.loc[index]
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
            user_id = row.get("user_id")
            if user_id and isinstance(user_id, str):
                sucesso = atualizar_status(user_id, novo_status)
                if sucesso:
                    st.success(f"Status atualizado para {row['name']}")
                    st.session_state["dados_filtrados"].at[index, "status"] = novo_status
                else:
                    st.error(f"Erro ao atualizar status de {row['name']}")
            else:
                st.warning(f"ID inválido para {row['name']}, não foi possível atualizar.")

            if sucesso:
                st.success(f"Status atualizado para {row['name']}")
                st.session_state["dados_filtrados"].at[index, "status"] = novo_status
            else:
                st.error(f"Erro ao atualizar status de {row['name']}")
        st.markdown("---")
else:
    st.info("Use os filtros à esquerda e clique em **Filtrar** para ver os resultados.")

# Guardar archivo final
#ruta_final_solucion = "/mnt/data/home_crm_solucion_final.py"
#with open(ruta_final_solucion, "w", encoding="utf-8") as f:
    #f.write(codigo_final)

#ruta_final_solucion
