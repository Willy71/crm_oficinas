import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account  import Credentials

# Cargar credenciales y autorizar
# Ruta al archivo de credenciales
# Scopes necesarios
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_INFO = st.secrets["gsheets"]

# Clave de la hoja de cálculo (la parte de la URL después de "/d/" y antes de "/edit")
SPREADSHEET_KEY = "1X6nJrJMTN_qBUJ6bV9GzLK1BVUS6hiLEExhslrfV6xs"  # Reemplazá esto por tu clave real
SHEET_NAME = 'sheet1'  # Nombre de la hoja dentro del documento
credentials = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
client = gspread.authorize(credentials)
credenciales_json = credentials

# Autenticando com Google Sheets

#credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
#client = gspread.authorize(credentials)

def inicializar_hoja():
    try:
        # Abrir la hoja de cálculo
        spreadsheet = gc.open_by_key(SPREADSHEET_KEY)
        
        # Intentar abrir la hoja específica
        try:
            worksheet = spreadsheet.worksheet(SHEET_NAME)
        except gspread.exceptions.WorksheetNotFound:
            # Si la hoja no existe, crearla
            worksheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows=100, cols=50)
            # Agregar los encabezados de las columnas
            worksheet.append_row(columnas_ordenadas)  # Asegúrate de definir `columnas_ordenadas`
        
        return worksheet
    except Exception as e:
        st.error(f"Erro ao acessar planilha: {str(e)}")
        return None

# Función para cargar datos desde Google Sheets
def cargar_datos(worksheet):
    try:
        records = worksheet.get_all_records()
        if not records:
            # Si no hay registros, crear un DataFrame vacío con las columnas necesarias
            return pd.DataFrame(columns=columnas_ordenadas)
        else:
            # Convertir los registros a DataFrame
            df = pd.DataFrame(records)
            # Asegurarse de que la columna 'user_id' sea numérica
            df['user_id'] = pd.to_numeric(df['user_id'], errors='coerce').fillna(0).astype(int)
            return df
    except Exception as e:
        st.error(f"Erro ao cargar dados: {str(e)}")
        return pd.DataFrame(columns=columnas_ordenadas)

columnas_ordenadas = ['name', 'address','phone', 'webpage', 'rating', 'city', 'state','country', 'status']
# Inicializar la hoja de cálculo
worksheet = inicializar_hoja()

# Cargar datos desde Google Sheets
df = cargar_datos(worksheet)



# Acessando a planilha

#sheet = client.open_by_key(SPREADSHEET_KEY).sheet1

#data = sheet.get_all_records()
#df = pd.DataFrame(data)

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
