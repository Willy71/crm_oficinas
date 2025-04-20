import streamlit as st

def main():
    st.set_page_config(page_title="Simple CRM", layout="wide")
    st.title("Simple CRM")

    # Sidebar for navigation
    page = st.sidebar.selectbox("Navigation", ["Dashboard", "Adicionar prospecto", "Ver prospecto"])
    if page == "Dashboard":
        st.title("Dashboard")
    elif page == "Adicionar prospecto":
        st.title("Adicionar prospecto")
    elif page == "Ver prospecto":
        st.title("Ver prospecto")


if __name__ == "__main__":
    main() 
