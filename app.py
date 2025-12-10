import streamlit as st
import pandas as pd
import calendar

# ======================================
# CONFIGURAÇÃO INICIAL
# ======================================
st.set_page_config(
    page_title="Dashboard de Encerramentos",
    layout="wide",
)

# ====================================
# Tema personalizado QCA / Credsystem
# ====================================
PRIMARY_COLOR = "#1E2245"
SECONDARY_COLOR = "#800E35"
TEXT_COLOR = "#FFFFFF"

st.markdown(
    f"""
    <style>

    /* Fundo geral */
    .stApp {{
        background-color: {PRIMARY_COLOR} !important;
        color: {TEXT_COLOR} !important;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {PRIMARY_COLOR} !important;
        color: {TEXT_COLOR} !important;
    }}

    /* Títulos, textos e labels */
    html, body, [class*="st-"], .stMarkdown, .stTextInput, label, p, span {{
        color: {TEXT_COLOR} !important;
    }}

    /* Inputs (caixa de texto, select, multiselect...) */
    input, textarea, select, .stTextInput > div > div > input {{
        background-color: #2A2F55 !important;
        color: {TEXT_COLOR} !important;
        border: 1px solid {SECONDARY_COLOR} !important;
        border-radius: 6px;
    }}

    /* Botões */
    .stButton>button {{
        background-color: {SECONDARY_COLOR} !important;
        color: white !important;
        border: none;
        border-radius: 6px;
        padding: 8px 20px;
        font-weight: 600;
    }}
    .stButton>button:hover {{
        background-color: #A01248 !important;
        color: white !important;
        border: none;
    }}

    /* Métricas */
    div[data-testid="stMetricValue"], 
    div[data-testid="stMetricLabel"] {{
        color: {TEXT_COLOR} !important;
    }}

    /* DataFrames e tabelas */
    .stDataFrame, .stTable {{
        background-color: transparent !important;
        color: {TEXT_COLOR} !important;
    }}

    /* Containers (cards, caixas, markdown blocks) */
    .stContainer, .stMarkdown {{
        background-color: transparent !important;
    }}

    /* Selectbox e multiselect fundo */
    div[data-baseweb="select"] > div {{
        background-color: #2A2F55 !important;
        color: {TEXT_COLOR} !important;
        border-color: {SECONDARY_COLOR} !important;
    }}

    /* Hover do dropdown */
    li[role="option"]:hover {{
        background-color: {SECONDARY_COLOR} !important;
        color: white !important;
    }}

    /* Barra superior (deploy, logotipo do streamlit) */
    header[data-testid="stHeader"] {{
        background: none !important;
    }}

    /* Remover bordas claras padrão */
    .block-container {{
        padding-top: 1.5rem;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# ======================================
# PINs e regras de acesso
# ======================================
PIN_RULES = {
    # 9999 -> vê todas as células
    "9999": {
        "all": True,
        "cells": None,
        "label": "Controller",
    },

    # 1375 -> CredSystem, Credsystem - Administrativo
    "1375": {
        "all": False,
        "cells": ["CredSystem", "Credsystem - Administrativo"],
        "label": "CredSystem",
    },

    # 4820 -> Samsung
    "4820": {
        "all": False,
        "cells": ["Samsung"],
        "label": "Samsung",
    },

    # 7312 -> Asus, Lenovo - Service, Lenovo - Web
    "7312": {
        "all": False,
        "cells": ["Asus", "Lenovo - Service", "Lenovo - Web"],
        "label": "Lenovo",
    },

    # 2648 -> Cardif, Generali Brasil Seguros S.A., Ressarci - Movida
    "2648": {
        "all": False,
        "cells": ["Cardif", "Generali Brasil Seguros S.A.", "Ressarci - Movida"],
        "label": "Cardif / Generali / Movida",
    },

    # 5903 -> GOL, Smiles
    "5903": {
        "all": False,
        "cells": ["GOL", "Smiles"],
        "label": "GOL / Smiles",
    },

    # 8241 -> Whirlpool
    "8241": {
        "all": False,
        "cells": ["Whirlpool"],
        "label": "Whirlpool",
    },

    # 4167 -> Extrafarma, ALE
    "4167": {
        "all": False,
        "cells": ["Extrafarma", "ALE"],
        "label": "ALE / Extrafarma",
    },
}


def get_pin_rule(pin_input: str):
    """Retorna a regra de acesso para o PIN informado (case-insensitive)."""
    if not pin_input:
        return None
    pin_clean = pin_input.strip().lower()
    return PIN_RULES.get(pin_clean)


# ======================================
# Carregamento dos dados
# ======================================
@st.cache_data
def load_data(path: str):
    df = pd.read_excel(path)

    # Ajuste AQUI os nomes das colunas se forem diferentes na planilha
    # Supondo:
    # AG = "Data Encerramento"
    # AM = "Responsável Encerramento"
    # AS = "Célula"
    # AK = "Tipo Encerramento"

    df["Data Encerramento"] = pd.to_datetime(
        df["Data Encerramento"], dayfirst=True, errors="coerce"
    )

    df["Ano Encerramento"] = df["Data Encerramento"].dt.year
    df["Mes Encerramento"] = df["Data Encerramento"].dt.month

    return df


EXCEL_PATH = r"C:\Users\ingridaleixo\OneDrive - Queiroz Cavalcanti Advocacia\NÚCLEO CONTROLLER\Planilhas - Auditorias\ENCERRAMENTOS.xlsx"
df_raw = load_data(EXCEL_PATH)

# Nomes das colunas utilizadas no código
COL_DATA = "Data Encerramento"
COL_CELULA = "Célula"
COL_RESP = "Responsável Encerramento"
COL_TIPO = "Tipo Encerramento"


# ======================================
# CONTROLE DE SESSÃO (LOGIN POR PIN)
# ======================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.pin_label = None
    st.session_state.pin_rule = None

if not st.session_state.logged_in:
    # Tela de login
    st.title("🔐 Dashboard de Encerramentos – Login")

    st.markdown(
        """
        Para acessar o painel, informe o **PIN** da sua coordenação.
        """
    )

    pin_input = st.text_input("Digite seu PIN:", type="password")

    if st.button("Entrar"):
        rule = get_pin_rule(pin_input)
        if rule is None:
            st.error("PIN inválido. Verifique e tente novamente.")
        else:
            st.session_state.logged_in = True
            st.session_state.pin_label = rule["label"]
            st.session_state.pin_rule = rule
            st.success("PIN aceito! Carregando dashboard...")
            st.rerun()


    # Não deixa seguir adiante sem login
    st.stop()


# ======================================
# USUÁRIO AUTENTICADO – APLICA REGRA DO PIN
# ======================================
rule = st.session_state.pin_rule
df = df_raw.copy()

if rule and not rule.get("all", False):
    allowed_cells = rule["cells"]
    df = df[df[COL_CELULA].isin(allowed_cells)]

# ======================================
# BARRA LATERAL – INFO DO PIN E LOGOUT
# ======================================
st.sidebar.markdown("### Usuário autenticado")
st.sidebar.write(f"**Perfil:** {st.session_state.pin_label}")

if st.sidebar.button("Trocar PIN / Logout"):
    for k in ["logged_in", "pin_label", "pin_rule"]:
        if k in st.session_state:
            del st.session_state[k]   
    st.rerun()



# ======================================
# A PARTIR DAQUI É O MESMO DASHBOARD DE ANTES,
# SÓ QUE JÁ COM O DF RESTRITO ÀS CÉLULAS DO PIN
# ======================================

st.title("📊 Dashboard de Encerramentos")

st.markdown(
    """
Este painel mostra a **quantidade de encerramentos** com base na planilha de encerramentos.

- A coluna **Célula** é usada para agrupar os dados;
- A coluna **Responsável Encerramento** identifica quem encerrou;
- A coluna **Data Encerramento** permite filtrar por período, mês e ano;
- A coluna **Tipo Encerramento** mostra o tipo de encerramento.

"""
)

# =========================
# Barra lateral – Filtros
# =========================
st.sidebar.header("Filtros")

min_date = df[COL_DATA].min()
max_date = df[COL_DATA].max()

periodo = st.sidebar.date_input(
    "Período (Data de Encerramento)",
    value=[min_date, max_date] if pd.notnull(min_date) and pd.notnull(max_date) else [],
)

anos_disponiveis = sorted(df["Ano Encerramento"].dropna().unique())
anos_sel = st.sidebar.multiselect("Ano de Encerramento", anos_disponiveis)

meses_disponiveis = sorted(df["Mes Encerramento"].dropna().unique())
meses_label = {m: calendar.month_name[m] for m in meses_disponiveis}
meses_sel = st.sidebar.multiselect(
    "Mês de Encerramento",
    meses_disponiveis,
    format_func=lambda m: meses_label.get(m, m),
)

celulas_disponiveis = sorted(df[COL_CELULA].dropna().unique())
celulas_sel = st.sidebar.multiselect("Célula", celulas_disponiveis)

responsaveis_disponiveis = sorted(df[COL_RESP].dropna().unique())
responsaveis_sel = st.sidebar.multiselect("Responsável pelo Encerramento", responsaveis_disponiveis)

# Tipos de encerramento
tipos_disponiveis = sorted(df[COL_TIPO].dropna().unique())
tipos_sel = st.sidebar.multiselect("Tipo de Encerramento", tipos_disponiveis)


# =========================
# Aplicação dos filtros
# =========================
df_filtrado = df.copy()

# Período
if isinstance(periodo, list) and len(periodo) == 2:
    data_inicio, data_fim = periodo
    if data_inicio and data_fim:
        df_filtrado = df_filtrado[
            (df_filtrado[COL_DATA] >= pd.to_datetime(data_inicio))
            & (df_filtrado[COL_DATA] <= pd.to_datetime(data_fim))
        ]

# Ano
if anos_sel:
    df_filtrado = df_filtrado[df_filtrado["Ano Encerramento"].isin(anos_sel)]

# Mês
if meses_sel:
    df_filtrado = df_filtrado[df_filtrado["Mes Encerramento"].isin(meses_sel)]

# Célula
if celulas_sel:
    df_filtrado = df_filtrado[df_filtrado[COL_CELULA].isin(celulas_sel)]

# Responsável
if responsaveis_sel:
    df_filtrado = df_filtrado[df_filtrado[COL_RESP].isin(responsaveis_sel)]

# Tipo de Encerramento
if tipos_sel:
    df_filtrado = df_filtrado[df_filtrado[COL_TIPO].isin(tipos_sel)]

# =========================
# Modo de visualização
# =========================
modo = st.radio(
    "Modo de visualização",
    ["Visão Geral", "Comparar Células"],
    horizontal=True,
)

# =========================
# VISÃO GERAL
# =========================
if modo == "Visão Geral":
    st.subheader("Visão Geral dos Encerramentos")

    total_encerramentos = len(df_filtrado)
    total_celulas = df_filtrado[COL_CELULA].nunique()
    total_responsaveis = df_filtrado[COL_RESP].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Encerramentos", total_encerramentos)
    col2.metric("Quantidade de Células", total_celulas)
    col3.metric("Responsáveis Diferentes", total_responsaveis)

    st.markdown("### Quantidade de Encerramentos por Célula")
    if total_encerramentos > 0:
        encerr_por_celula = (
            df_filtrado.groupby(COL_CELULA)
            .size()
            .sort_values(ascending=False)
            .rename("Quantidade")
            .reset_index()
        )
        st.dataframe(encerr_por_celula, use_container_width=True, hide_index=True)
        st.bar_chart(encerr_por_celula.set_index(COL_CELULA)["Quantidade"])
    else:
        st.info("Nenhum encerramento encontrado com os filtros atuais.")

    st.markdown("### Detalhamento por Tipo de Encerramento")
    if total_encerramentos > 0:
        tipo_counts = (
            df_filtrado.groupby(COL_TIPO)
            .size()
            .sort_values(ascending=False)
            .rename("Quantidade")
            .reset_index()
        )
        st.dataframe(tipo_counts, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum tipo de encerramento encontrado com os filtros atuais.")

# =========================
# MODO COMPARAR CÉLULAS
# =========================
else:
    st.subheader("Comparação entre Células")

    celulas_comp = st.multiselect(
        "Selecione de 2 a 3 Células para comparar",
        celulas_disponiveis,
        max_selections=3,
    )

    if len(celulas_comp) < 2:
        st.warning("Selecione pelo menos 2 células para comparação.")
    else:
        cols = st.columns(len(celulas_comp))

        for col, cel in zip(cols, celulas_comp):
            with col:
                st.markdown(f"#### Célula: {cel}")

                df_cel = df_filtrado[df_filtrado[COL_CELULA] == cel]

                total_cel = len(df_cel)
                tipos_unicos = df_cel[COL_TIPO].nunique()

                st.metric("Total de Encerramentos", total_cel)
                st.metric("Tipos de Encerramento", tipos_unicos)

                if total_cel > 0:
                    st.markdown("**Encerramentos por Tipo**")
                    tipo_counts_cel = (
                        df_cel.groupby(COL_TIPO)
                        .size()
                        .sort_values(ascending=False)
                        .rename("Quantidade")
                        .reset_index()
                    )
                    st.table(tipo_counts_cel)
                else:
                    st.info("Nenhum encerramento para essa célula com os filtros atuais.")
