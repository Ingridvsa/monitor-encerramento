import streamlit as st
import pandas as pd
import calendar

# =========================
# Carregamento dos dados
# =========================
@st.cache_data
def load_data(path: str):
    df = pd.read_excel(path)

    # Garante que a coluna de data está em formato datetime
    df["Data Encerramento"] = pd.to_datetime(
        df["Data Encerramento"], dayfirst=True, errors="coerce"
    )

    # Cria colunas auxiliares de Ano e Mês
    df["Ano Encerramento"] = df["Data Encerramento"].dt.year
    df["Mes Encerramento"] = df["Data Encerramento"].dt.month

    return df


# Caminho do arquivo Excel
EXCEL_PATH = "ENCERRAMENTOS.xlsx"

df_raw = load_data(EXCEL_PATH)

# Renomear para facilitar o uso no código (opcional, só pra ficar mais curto)
COL_DATA = "Data Encerramento"
COL_CELULA = "Célula"
COL_RESP = "Responsável Encerramento"
COL_TIPO = "Tipo Encerramento"

df = df_raw.copy()

# =========================
# Layout geral
# =========================
st.set_page_config(
    page_title="Dashboard de Encerramentos",
    layout="wide",
)

st.title("📊 Dashboard de Encerramentos")

st.markdown(
    """
Este painel mostra a **quantidade de encerramentos (acordos)** com base na planilha de encerramentos.

- A coluna **Célula** é usada para agrupar os dados;
- A coluna **Responsável Encerramento** identifica quem encerrou;
- A coluna **Data Encerramento** permite filtrar por período, mês e ano;
- A coluna **Tipo Encerramento** mostra o tipo de encerramento.

Por padrão, ao entrar, **nenhum filtro específico de célula ou responsável** é aplicado (todas as células juntas).
"""
)

# =========================
# Barra lateral – Filtros
# =========================
st.sidebar.header("Filtros")

# Limites de datas
min_date = df[COL_DATA].min()
max_date = df[COL_DATA].max()

# Período (data inicial e final)
periodo = st.sidebar.date_input(
    "Período (Data de Encerramento)",
    value=[min_date, max_date] if pd.notnull(min_date) and pd.notnull(max_date) else [],
)

# Ano
anos_disponiveis = sorted(df["Ano Encerramento"].dropna().unique())
anos_sel = st.sidebar.multiselect("Ano de Encerramento", anos_disponiveis)

# Mês
meses_disponiveis = sorted(df["Mes Encerramento"].dropna().unique())
meses_label = {m: calendar.month_name[m] for m in meses_disponiveis}
meses_sel = st.sidebar.multiselect(
    "Mês de Encerramento",
    meses_disponiveis,
    format_func=lambda m: meses_label.get(m, m),
)

# Célula
celulas_disponiveis = sorted(df[COL_CELULA].dropna().unique())
celulas_sel = st.sidebar.multiselect("Célula", celulas_disponiveis)

# Responsável
responsaveis_disponiveis = sorted(df[COL_RESP].dropna().unique())
responsaveis_sel = st.sidebar.multiselect("Responsável pelo Encerramento", responsaveis_disponiveis)

# =========================
# Aplicação dos filtros
# =========================
df_filtrado = df.copy()

# Filtro por período (data inicial e final)
if isinstance(periodo, list) and len(periodo) == 2:
    data_inicio, data_fim = periodo
    if data_inicio and data_fim:
        df_filtrado = df_filtrado[
            (df_filtrado[COL_DATA] >= pd.to_datetime(data_inicio))
            & (df_filtrado[COL_DATA] <= pd.to_datetime(data_fim))
        ]

# Filtro por ano
if anos_sel:
    df_filtrado = df_filtrado[df_filtrado["Ano Encerramento"].isin(anos_sel)]

# Filtro por mês
if meses_sel:
    df_filtrado = df_filtrado[df_filtrado["Mes Encerramento"].isin(meses_sel)]

# Filtro por célula
if celulas_sel:
    df_filtrado = df_filtrado[df_filtrado[COL_CELULA].isin(celulas_sel)]

# Filtro por responsável
if responsaveis_sel:
    df_filtrado = df_filtrado[df_filtrado[COL_RESP].isin(responsaveis_sel)]

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
        st.dataframe(encerr_por_celula, use_container_width=True)
        st.bar_chart(
            data=encerr_por_celula.set_index(COL_CELULA)["Quantidade"]
        )
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
        st.dataframe(tipo_counts, use_container_width=True)
    else:
        st.info("Nenhum tipo de encerramento encontrado com os filtros atuais.")

# =========================
# MODO COMPARAR CÉLULAS
# =========================
else:
    st.subheader("Comparação entre Células")

    # Seleção de 2 a 3 células
    celulas_comp = st.multiselect(
        "Selecione de 2 a 3 Células para comparar",
        celulas_disponiveis,
        max_selections=3,
    )

    if len(celulas_comp) < 2:
        st.warning("Selecione pelo menos 2 células para comparação.")
    else:
        # Mesmo df_filtrado (com período, ano, mês, responsável etc.) é usado aqui
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
