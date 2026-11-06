import streamlit as st

from data.load_data import carregar_dicionario

ESTILO = """
<style>
    div[class*="_como_interpretar"] {
        background: #fff;
        border: 1px solid #E1ECF7;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0, 75, 133, .05);
        padding: 6px 14px;
    }

    div[class*="_como_interpretar"] [data-testid="stExpander"] details {
        border: none;
    }
</style>
"""


def como_interpretar(pagina, topicos, limitacao=None):
    st.markdown(ESTILO, unsafe_allow_html=True)

    with st.container(key=f"{pagina}_como_interpretar"):
        with st.expander("Como interpretar", icon=":material/menu_book:"):
            st.markdown("\n".join(f"- {topico}" for topico in topicos))

            if limitacao:
                st.markdown(f"**Limitação:** {limitacao}")


def dicionario_indicadores(chave):
    try:
        dicionario = carregar_dicionario()
    except Exception as erro:
        st.caption(f"Dicionário de indicadores indisponível: {erro}")
        return

    st.markdown(ESTILO, unsafe_allow_html=True)

    with st.container(key=f"{chave}_como_interpretar_dicionario"):
        with st.expander(
            "Dicionário: como cada indicador é calculado",
            icon=":material/functions:",
        ):
            st.dataframe(
                dicionario,
                hide_index=True,
                use_container_width=True,
                height=420,
            )
            st.caption(
                "Fonte: aba Dicionário de KPIs financeiros da planilha "
                "Analise_Financeira.xlsx."
            )