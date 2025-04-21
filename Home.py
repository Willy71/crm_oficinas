import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Autenticando com Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(credentials)



# Acessando a planilha
SPREADSHEET_KEY = "1X6nJrJMTN_qBUJ6bV9GzLK1BVUS6hiLEExhslrfV6xs"  # Reemplazá esto por tu clave real
sheet = client.open_by_key(SPREADSHEET_KEY).sheet1

data = sheet.get_all_records()
df = pd.DataFrame(data)

# Adiciona link de WhatsApp
def gerar_link_whatsapp(numero):
    numero_limpo = ''.join(filter(str.isdigit, str(numero)))
    return f"https://wa.me/{numero_limpo}" if numero_limpo else ""

df["whatsapp"] = df["phone"].apply(gerar_link_whatsapp)

# Interface do usuário
st.title("CRM de Leads - Oficinas Mecânicas")

# Filtros
status_opcao = st.selectbox("Filtrar por status:", ["Todos"] + sorted(df["status"].unique()))
cidade_opcao = st.selectbox("Filtrar por cidade:", ["Todas"] + sorted(df["city"].unique()))
estado_opcao = st.selectbox("Filtrar por estado:", ["Todos"] + sorted(df["state"].unique()))
pais_opcao = st.selectbox("Filtrar por país:", ["Todos"] + sorted(df["country"].unique()))

# Aplica os filtros
filtro = df.copy()
if status_opcao != "Todos":
    filtro = filtro[filtro["status"] == status_opcao]
if cidade_opcao != "Todas":
    filtro = filtro[filtro["city"] == cidade_opcao]
if estado_opcao != "Todos":
    filtro = filtro[filtro["state"] == estado_opcao]
if pais_opcao != "Todos":
    filtro = filtro[filtro["country"] == pais_opcao]

# Exibe resultados
st.markdown("### Resultados")
for index, row in filtro.iterrows():
    st.markdown(f"**{row['name']}**")
    st.markdown(f"Endereço: {row['address']}")
    st.markdown(f"Site: [{row['website']}]({row['website']})" if row['website'] else "Site: N/A")
    st.markdown(f"Avaliação: {row['rating']}")
    st.markdown(f"Cidade: {row['city']} | Estado: {row['state']} | País: {row['country']}")
    if row['whatsapp']:
        st.markdown(f"[Enviar mensagem no WhatsApp]({row['whatsapp']})")
    else:
        st.markdown("WhatsApp: N/A")
    st.markdown("---")
