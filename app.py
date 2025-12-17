import streamlit as st
import pandas as pd
import calendar
import altair as alt
import requests
from io import BytesIO

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

# ============================
# TEMA ALTAIR (FUNDO + LETRAS)
# ============================
def qca_altair_theme():
    return {
        "config": {
            "background": PRIMARY_COLOR,
            "view": {"fill": PRIMARY_COLOR, "stroke": None},
            "axis": {
                "labelColor": TEXT_COLOR,
                "titleColor": TEXT_COLOR,
                "gridColor": "#2A2F55",
                "domainColor": TEXT_COLOR,
                "tickColor": TEXT_COLOR,
            },
            "legend": {"labelColor": TEXT_COLOR, "titleColor": TEXT_COLOR},
            "title": {"color": TEXT_COLOR},
        }
    }

alt.themes.register("qca", qca_altair_theme)
alt.themes.enable("qca")

# ============================
# CSS STREAMLIT (EDGE SAFE)
# ============================
st.markdown(
    rf"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,1,0');

:root {{
  color-scheme: dark;
}}

/* RESET */
* {{
  box-sizing: border-box !important;
  forced-color-adjust: none !important;
}}

html, body, .stApp {{
  background: #1E2245 !important;
  color: #FFFFFF !important;
  font-family: "Inter","Segoe UI","Roboto","Helvetica Neue",Arial,sans-serif !important;
}}

/* REMOVE FAIXAS PRETAS */
div[data-testid="stAppViewContainer"],
main,
section[data-testid="stMain"],
header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"] {{
  background: #1E2245 !important;
}}

/* SIDEBAR */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {{
  background: #1E2245 !important;
  color: #FFFFFF !important;
}}

/* TEXTOS */
h1,h2,h3,h4,h5,h6,p,label,small,li,span,div {{
  color: #FFFFFF !important;
}}

/* =========================
   BOTÕES
   ========================= */
.stButton > button,
button[kind="primary"],
button[kind="secondary"] {{
  background: #800E35 !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 700 !important;
}}

.stButton > button:hover {{
  background: #A01248 !important;
}}

/* =========================
   INPUTS / DATE / NUMBER
   ========================= */
div[data-baseweb="input"] input,
div[data-baseweb="base-input"] input {{
  background: #2A2F55 !important;
  color: #FFFFFF !important;
  border: 1px solid #800E35 !important;
  border-radius: 8px !important;
  caret-color: #FFFFFF !important;
  -webkit-text-fill-color: #FFFFFF !important;
}}

/* =========================
   SELECT / MULTISELECT
   ========================= */
div[data-baseweb="select"] > div {{
  background: #2A2F55 !important;
  border: 1px solid #800E35 !important;
  border-radius: 8px !important;
}}

div[data-baseweb="select"] input,
div[data-baseweb="select"] span {{
  color: #FFFFFF !important;
}}

div[data-baseweb="select"] svg {{
  fill: #FFFFFF !important;
}}

/* tags multiselect */
div[data-baseweb="tag"] {{
  background: #1E2245 !important;
  border: 1px solid #800E35 !important;
  color: #FFFFFF !important;
}}

/* dropdown */
div[role="listbox"] {{
  background: #11142A !important;
  border: 1px solid #800E35 !important;
}}

li[role="option"]:hover {{
  background: #800E35 !important;
}}

/* =========================
   DATE PICKER
   ========================= */
div[data-baseweb="popover"] > div,
div[role="dialog"] {{
  background: #11142A !important;
  border: 1px solid #800E35 !important;
  border-radius: 10px !important;
}}

/* =========================
   RADIO (REMOVE FAIXA)
   ========================= */
div[data-testid="stRadio"] * {{
  box-shadow: none !important;
  border: none !important;
}}

div[data-testid="stRadio"] label {{
  background: transparent !important;
}}

div[data-testid="stRadio"] input[type="radio"] {{
  accent-color: #800E35 !important;
}}

/* =========================
   SETA DA SIDEBAR (100% FIXA)
   ========================= */

/* ESCONDE TEXTO */
span[data-testid="stIconMaterial"] {{
  text-indent: -9999px !important;
  overflow: hidden !important;
  position: relative !important;
  width: 30px !important;
  height: 30px !important;
}}

/* SIDEBAR ABERTA */
div[data-testid="stSidebarCollapseButton"]
span[data-testid="stIconMaterial"]::before {{
  content: "keyboard_double_arrow_left";
  font-family: "Material Symbols Rounded" !important;
  font-variation-settings: "FILL" 1;
  font-size: 26px;
  color: #FFFFFF;
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}}

/* SIDEBAR FECHADA */
div[data-testid="collapsedControl"]
span[data-testid="stIconMaterial"]::before {{
  content: "keyboard_double_arrow_right";
  font-family: "Material Symbols Rounded" !important;
  font-variation-settings: "FILL" 1;
  font-size: 26px;
  color: #FFFFFF;
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}}

</style>
""",
    unsafe_allow_html=True
)

# ======================================
# PINs e regras de acesso
# ======================================
PIN_RULES = {
    "9999": {"all": True, "cells": None, "label": "Controller"},
    "1375": {"all": False, "cells": ["CredSystem", "Credsystem - Administrativo"], "label": "CredSystem"},
    "4820": {"all": False, "cells": ["Samsung"], "label": "Samsung"},
    "7312": {"all": False, "cells": ["Asus", "Lenovo - Service", "Lenovo - Web"], "label": "Lenovo"},
    "2648": {"all": False, "cells": ["Cardif", "Generali Brasil Seguros S.A.", "Ressarci - Movida"], "label": "Cardif / Generali / Movida"},
    "5903": {"all": False, "cells": ["GOL", "Smiles"], "label": "GOL / Smiles"},
    "8241": {"all": False, "cells": ["Whirlpool"], "label": "Whirlpool"},
    "4167": {"all": False, "cells": ["Extrafarma", "ALE"], "label": "ALE / Extrafarma"},
}

def get_pin_rule(pin_input: str):
    if not pin_input:
        return None
    return PIN_RULES.get(pin_input.strip())

# ======================================
# LINK DO SHAREPOINT (DOWNLOAD DIRETO)
# ======================================
EXCEL_URL = (
    "https://queirozcavalcanti-my.sharepoint.com/:x:/g/personal/"
    "gabrielpontual_queirozcavalcanti_adv_br/"
    "IQD_stp8RpavSacdSbEwVs_qASnwn5uLtsyuQ3srFOgRb9s"
    "?download=1"
)

# ======================================
# Carregamento dos dados (via URL)
# ======================================
@st.cache_data(ttl=600)
def load_data_from_url(url: str) -> pd.DataFrame:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    content = r.content

    if not content.startswith(b"PK"):
        raise ValueError(
            "O link não retornou um .xlsx válido (possível página de permissão do SharePoint). "
            "Verifique se o compartilhamento permite acesso por link e download."
        )

    df = pd.read_excel(BytesIO(content), sheet_name=0, header=0, engine="openpyxl")

    df.columns = (
        df.columns.astype(str)
        .str.replace("\xa0", " ", regex=False)
        .str.strip()
    )

    required_cols = ["Data Encerramento", "Tipo Encerramento", "Responsável Encerramento", "Célula"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise KeyError(
            f"Colunas não encontradas: {missing}. "
            f"Colunas detectadas (até 30): {list(df.columns)[:30]}"
        )

    df["Data Encerramento"] = pd.to_datetime(df["Data Encerramento"], dayfirst=True, errors="coerce")
    df["Ano Encerramento"] = df["Data Encerramento"].dt.year
    df["Mes Encerramento"] = df["Data Encerramento"].dt.month
    return df

# Sidebar: botão para atualização
st.sidebar.markdown("### Atualização da Base")
if st.sidebar.button("Atualizar dados agora"):
    st.cache_data.clear()
    st.rerun()

# Carrega base
try:
    df_raw = load_data_from_url(EXCEL_URL)
except Exception as e:
    st.error("Não foi possível carregar a planilha do SharePoint.")
    st.exception(e)
    st.stop()

# Colunas
COL_DATA = "Data Encerramento"
COL_CELULA = "Célula"
COL_RESP = "Responsável Encerramento"
COL_TIPO = "Tipo Encerramento"

# ======================================
# Regras de classificação FAVO / DESF
# ======================================
FAVO_TYPES = {
    "ACORDO", "ACORDO PRÉVIO", "ACORDO PREVIO", "DESISTÊNCIA", "DESISTENCIA",
    "DESISTÊNCIA DA RECLAMAÇÃO", "EXTINTO SEM JULGAMENTO DO MÉRITO",
    "EXTINTO SEM JULGAMENTO", "IMPROCEDENTE", "NÃO FUNDAMENTADA",
    "NAO FUNDAMENTADA SEM PECÚNIA", "COM MULTA",
}
DESF_TYPES = {"PROCEDENTE", "PROCEDENTE EM PARTE"}
IGNORE_TYPES = {"DESCONSIDERAÇÃO DE PATROCÍNIO", "DESCONTRATAÇÃO", "CADASTRO DUPLICADO OU EQUIVOCADO"}

df_raw[COL_TIPO] = df_raw[COL_TIPO].astype(str).str.upper().str.strip()
df_raw[COL_CELULA] = df_raw[COL_CELULA].astype(str).str.replace("\xa0", " ", regex=False).str.strip()

def classificar_tipo(tipo: str) -> str:
    if tipo in IGNORE_TYPES:
        return "IGNORAR"
    if tipo in FAVO_TYPES:
        return "FAVORÁVEL"
    if tipo in DESF_TYPES:
        return "DESFAVORÁVEL"
    return None

df_raw["Classificação"] = df_raw[COL_TIPO].apply(classificar_tipo)
df_raw = df_raw[df_raw["Classificação"] != "IGNORAR"]
df_raw = df_raw[df_raw["Classificação"].notna()]

# ======================================
# LOGIN POR PIN
# ======================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.pin_label = None
    st.session_state.pin_rule = None

if not st.session_state.logged_in:
    st.title("🔐 Dashboard de Encerramentos – Login")
    st.markdown("Para acessar o painel, informe o **PIN** da sua coordenação.")
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
    st.stop()

# ======================================
# USUÁRIO AUTENTICADO – APLICA REGRA DO PIN
# ======================================
rule = st.session_state.pin_rule
df = df_raw.copy()

allowed_cells = None
if rule is not None:
    if rule.get("all", False):
        allowed_cells = sorted(df[COL_CELULA].dropna().unique())
    else:
        allowed_cells = [c.strip() for c in rule["cells"]]
        df = df[df[COL_CELULA].isin(allowed_cells)]

# Sidebar info
st.sidebar.markdown("### Usuário autenticado")
st.sidebar.write(f"**Perfil:** {st.session_state.pin_label}")

st.sidebar.markdown("### Células liberadas pelo PIN")
st.sidebar.write(", ".join(allowed_cells) if allowed_cells else "Nenhuma célula liberada (verificar PIN).")

if st.sidebar.button("Logout"):
    for k in ["logged_in", "pin_label", "pin_rule"]:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()

# ======================================
# DASHBOARD
# ======================================
st.title("📊 Dashboard de Encerramentos")
st.markdown("Este painel mostra a **quantidade de encerramentos** com base na planilha de encerramentos.")

# Filtros
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

tipos_disponiveis = sorted(df[COL_TIPO].dropna().unique())
tipos_sel = st.sidebar.multiselect("Tipo de Encerramento", tipos_disponiveis)

# Aplica filtros
df_filtrado = df.copy()

if isinstance(periodo, list) and len(periodo) == 2:
    data_inicio, data_fim = periodo
    if data_inicio and data_fim:
        df_filtrado = df_filtrado[
            (df_filtrado[COL_DATA] >= pd.to_datetime(data_inicio))
            & (df_filtrado[COL_DATA] <= pd.to_datetime(data_fim))
        ]

if anos_sel:
    df_filtrado = df_filtrado[df_filtrado["Ano Encerramento"].isin(anos_sel)]
if meses_sel:
    df_filtrado = df_filtrado[df_filtrado["Mes Encerramento"].isin(meses_sel)]
if celulas_sel:
    df_filtrado = df_filtrado[df_filtrado[COL_CELULA].isin(celulas_sel)]
if responsaveis_sel:
    df_filtrado = df_filtrado[df_filtrado[COL_RESP].isin(responsaveis_sel)]
if tipos_sel:
    df_filtrado = df_filtrado[df_filtrado[COL_TIPO].isin(tipos_sel)]

modo = st.radio("Modo de visualização", ["Visão Geral", "Comparar Células"], horizontal=True)

if modo == "Visão Geral":
    st.subheader("Visão Geral dos Encerramentos")

    total_encerramentos = len(df_filtrado)
    total_celulas = df_filtrado[COL_CELULA].nunique()
    total_responsaveis = df_filtrado[COL_RESP].nunique()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total de Encerramentos", total_encerramentos)
    c2.metric("Quantidade de Células", total_celulas)
    c3.metric("Responsáveis Diferentes", total_responsaveis)

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

        chart_bar = (
            alt.Chart(encerr_por_celula)
            .mark_bar(color="#8FD0FF")
            .encode(
                x=alt.X(f"{COL_CELULA}:N", sort="-y", title=None, axis=alt.Axis(labelAngle=0, labelLimit=120, labelOverlap=False, labelPadding=10, tickSize=0)),
                y=alt.Y("Quantidade:Q", title=None),
            )
        )

        labels = (
            alt.Chart(encerr_por_celula)
            .mark_text(dy=-8, color="white", fontSize=12, fontWeight="bold")
            .encode(
                x=alt.X(f"{COL_CELULA}:N", sort="-y"),
                y=alt.Y("Quantidade:Q"),
                text=alt.Text("Quantidade:Q"),
            )
        )

        st.altair_chart((chart_bar + labels).properties(height=420), use_container_width=True)
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

    st.markdown("### Encerramentos Favoráveis x Desfavoráveis")
    if total_encerramentos > 0:
        resultado_classificacao = (
            df_filtrado["Classificação"]
            .value_counts()
            .rename_axis("Classificação")
            .reset_index(name="Quantidade")
        )

        resultado_plot = resultado_classificacao[
            resultado_classificacao["Classificação"].isin(["FAVORÁVEL", "DESFAVORÁVEL"])
        ]

        if not resultado_plot.empty:
            color_scale = alt.Scale(
                domain=["FAVORÁVEL", "DESFAVORÁVEL"],
                range=["#1CB66F", "#C7373A"],
            )

            chart = (
                alt.Chart(resultado_plot)
                .mark_bar(size=60)
                .encode(
                    x=alt.X("Quantidade:Q", title=None),
                    y=alt.Y("Classificação:N", title=None),
                    color=alt.Color(
                        "Classificação:N",
                        scale=color_scale,
                        legend=alt.Legend(orient="bottom", direction="horizontal", title=None),
                    ),
                )
                .properties(width="container", height=300)
            )

            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Nenhum encerramento FAVORÁVEL ou DESFAVORÁVEL encontrado com os filtros.")
    else:
        st.info("Nenhum encerramento para classificar com os filtros atuais.")

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
