import streamlit as st

from components.sidebar import GRUPOS

# Pergunta que cada página responde (mesma ordem e nomes do menu lateral)
PAGINAS = {
    "Visão Geral": "Como está a saúde financeira no ano e cenário escolhidos?",
    "Indicadores": "Como estão rentabilidade, liquidez e estrutura de capital?",
    "Tendência": "Como os números evoluem ao longo dos anos e onde há sinais de atenção?",
    "Comparação": "Como os cenários se saem lado a lado no mesmo ano?",
    "Ranking": "Quais cenários têm o maior e o menor EBITDA?",
    "Metas x Realizado": "O resultado alcançou a meta definida?",
    "Sensibilidade": "Quanto o caixa reage a mudanças nos fatores financeiros?",
    "Simular novo cenário": "E se a receita, os custos ou os investimentos mudarem?",
    "Regressão": "O que mais influencia a Geração de Caixa?",
    "Insights": "Quais são os destaques do ano, prontos para apresentar?",
}

PASSOS = [
    ("1", "Escolha o recorte",
     "No topo de cada página, escolha o ano e o cenário. Os números e gráficos "
     "mudam na hora."),
    ("2", "Leia os indicadores",
     "Comece pela Visão Geral e aprofunde em Indicadores e Tendência. "
     "Passe o mouse nos gráficos para ver os valores."),
    ("3", "Compare e simule",
     "Use Comparação e Ranking para ver os melhores cenários e o simulador "
     "para testar o que acontece se algo mudar."),
]

GLOSSARIO = [
    ("Cenário", "Uma das 1.200 simulações da concessão ao longo de 12 anos. Cada cenário "
     "combina valores diferentes de receita, custos e outras variáveis."),
    ("Receita", "Dinheiro que entra com a operação, antes de qualquer desconto."),
    ("EBITDA", "Resultado da operação antes de juros, impostos, depreciação e amortização. "
     "Mostra quanto a operação gera por si só."),
    ("Margem EBITDA", "EBITDA dividido pela receita: quanto de cada R$ 1 de receita vira "
     "resultado operacional."),
    ("Resultado Líquido", "O lucro que sobra depois de todas as despesas, juros e impostos."),
    ("Margem Líquida", "Resultado Líquido dividido pela receita."),
    ("Geração de Caixa", "Quanto o caixa aumentou ou diminuiu no ano, somando tudo o que "
     "entrou e saiu, inclusive investimentos."),
    ("NOPAT", "Lucro operacional depois dos impostos, sem considerar como a empresa é financiada."),
    ("ROIC", "Retorno sobre o capital investido: quanto o negócio rende sobre o dinheiro aplicado nele."),
    ("WACC", "Custo médio do dinheiro usado pela empresa (capital próprio e dívidas)."),
    ("EVA", "Valor econômico agregado: o lucro que sobra depois de pagar o custo do capital. "
     "Positivo significa que o negócio gera valor."),
    ("Liquidez Corrente", "Ativos de curto prazo divididos pelas dívidas de curto prazo. "
     "Acima de 1, há mais recursos do que obrigações no curto prazo."),
]

PERGUNTAS = [
    ("Por que alguns indicadores aparecem como N/D?",
     "N/D significa que a base não tem esse valor para o recorte escolhido. Por exemplo, "
     "ROIC e EVA não existem no último ano da base. Os dados ausentes não são inventados."),
    ("Em que unidade estão os valores?",
     "Em reais. Nos gráficos e cards, os valores aparecem em milhões (mi) ou bilhões (bi) "
     "para facilitar a leitura."),
    ("A Margem EBITDA passa de 100%. Está errado?",
     "Em alguns recortes a margem calculada na planilha passa de 100%. A Visão Geral avisa "
     "quando isso acontece; vale validar a fórmula antes de interpretar o número."),
    ("O que o simulador considera?",
     "Ele refaz as contas da DRE e do fluxo de caixa com as premissas escolhidas. Os tributos "
     "acompanham a receita, a alíquota de imposto é mantida e os investimentos afetam só o caixa."),
    ("A Regressão prova que um fator causa o outro?",
     "Não. Ela mostra como os valores andam juntos nos cenários simulados. É uma pista para "
     "investigar, não uma prova de causa e efeito."),
    ("Esqueci minha senha. E agora?",
     "Na tela de entrada, clique em “Esqueceu sua senha?”, informe seu e-mail e use o código "
     "de 6 dígitos para criar uma nova senha."),
    ("Como mudo a página que abre quando entro?",
     "Em Configurações, no card Preferências, escolha a página inicial. Ela vale a partir do "
     "próximo acesso."),
]

PAGE_STYLE = """
<style>
    .st-key-ajd_page {
        padding: 28px 32px 40px;
        gap: 16px !important;
    }

    .ajd-eyebrow {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .12em;
        color: var(--cti-blue);
        margin-bottom: 4px;
    }

    .ajd-title {
        font-size: 30px;
        font-weight: 700;
        color: var(--cti-text);
        line-height: 1.15;
    }

    .ajd-subtitle {
        font-size: 13px;
        color: var(--cti-muted);
        margin-top: 4px;
    }

    .ajd-section-title {
        font-size: 16px;
        font-weight: 700;
        color: var(--cti-text);
        margin-top: 12px;
    }

    .ajd-section-note {
        font-size: 12px;
        color: #8AA4BF;
        margin-top: 2px;
    }

    /* passos: mesmo espaçamento (16px) das colunas dos cartões de páginas,
       para as duas grades ficarem alinhadas */
    .ajd-passos {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 16px;
    }

    .ajd-passo,
    .ajd-glossario,
    [class*="st-key-ajd_pagina_"],
    .st-key-ajd_faq {
        background: #fff;
        border: 1px solid #E1ECF7;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0, 75, 133, .05);
    }

    .ajd-passo {
        padding: 18px 20px;
    }

    .ajd-passo-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 30px;
        height: 30px;
        border-radius: 8px;
        background: var(--cti-blue);
        color: #fff;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .ajd-passo strong,
    .ajd-pagina-nome {
        display: block;
        font-size: 14px;
        font-weight: 700;
        color: var(--cti-text);
        margin-bottom: 4px;
    }

    /* !important: o estilo de parágrafo do Streamlit ganharia e aumentaria a fonte */
    .st-key-ajd_page .ajd-passo p,
    .st-key-ajd_page p.ajd-pagina-texto {
        margin: 0 !important;
        font-size: 12.5px !important;
        line-height: 1.5 !important;
        color: var(--cti-muted) !important;
    }

    /* cartões das páginas */
    [class*="st-key-ajd_pagina_"] {
        padding: 16px 18px;
        gap: 10px !important;
    }

    .st-key-ajd_page [data-testid="stHorizontalBlock"]:has([class*="st-key-ajd_pagina_"]) {
        align-items: stretch;
    }

    .st-key-ajd_page [data-testid="stColumn"]:has([class*="st-key-ajd_pagina_"]) > div,
    .st-key-ajd_page [data-testid="stLayoutWrapper"]:has(> [class*="st-key-ajd_pagina_"]),
    [class*="st-key-ajd_pagina_"] {
        height: 100%;
    }

    .ajd-pagina-grupo {
        font-size: 10.5px;
        font-weight: 700;
        letter-spacing: .07em;
        color: #8AA4BF;
        margin-bottom: 4px;
    }

    [class*="st-key-ajd_pagina_"] .stButton button {
        background: #EEF5FC;
        color: var(--cti-blue);
        border: none;
        border-radius: 10px;
        font-weight: 600;
        font-size: 12.5px;
    }

    [class*="st-key-ajd_pagina_"] .stButton button:hover {
        background: #DCEBFC;
        color: var(--cti-blue);
    }

    /* glossário */
    .ajd-glossario {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0 28px;
        padding: 8px 22px;
    }

    .ajd-termo {
        padding: 12px 0;
        border-bottom: 1px solid #EEF3F9;
        font-size: 12.5px;
        line-height: 1.5;
        color: var(--cti-muted);
    }

    .ajd-termo b {
        display: block;
        font-size: 13px;
        color: var(--cti-text);
        margin-bottom: 2px;
    }

    /* perguntas frequentes */
    .st-key-ajd_faq {
        padding: 6px 14px;
    }

    .st-key-ajd_faq [data-testid="stExpander"] details {
        border: none;
        border-bottom: 1px solid #EEF3F9;
        border-radius: 0;
    }

    @media (max-width: 900px) {
        .ajd-passos,
        .ajd-glossario {
            grid-template-columns: 1fr;
        }
    }
</style>
"""


def _ir_para(pagina):
    st.session_state["pagina_atual"] = pagina
    st.session_state["cti_navegar_para"] = pagina


def _titulo_secao(titulo, nota=None):
    html = f'<div class="ajd-section-title">{titulo}</div>'
    if nota:
        html += f'<div class="ajd-section-note">{nota}</div>'
    st.markdown(html, unsafe_allow_html=True)


def _passos():
    _titulo_secao("Primeiros passos")
    itens = "".join(
        f'<div class="ajd-passo"><span class="ajd-passo-num">{num}</span>'
        f"<strong>{titulo}</strong><p>{texto}</p></div>"
        for num, titulo, texto in PASSOS
    )
    st.markdown(f'<div class="ajd-passos">{itens}</div>', unsafe_allow_html=True)


def _paginas():
    _titulo_secao("Conheça as páginas", "Cada página responde a uma pergunta.")

    # Mesma ordem e grupos do menu lateral
    paginas = [
        (grupo or "INÍCIO", nome)
        for grupo, itens in GRUPOS
        for nome, _ in itens
        if nome in PAGINAS
    ]

    # 5 por linha: as 10 páginas formam 2 linhas completas (com 3, sobrava
    # um cartão sozinho na última linha)
    por_linha = 5
    for inicio in range(0, len(paginas), por_linha):
        colunas = st.columns(por_linha, gap="small")
        for coluna, (grupo, nome) in zip(colunas, paginas[inicio:inicio + por_linha]):
            with coluna:
                chave = "".join(c if c.isalnum() else "_" for c in nome.lower())
                with st.container(key=f"ajd_pagina_{chave}"):
                    st.markdown(
                        f'<div class="ajd-pagina-grupo">{grupo}</div>'
                        f'<span class="ajd-pagina-nome">{nome}</span>'
                        f'<p class="ajd-pagina-texto">{PAGINAS[nome]}</p>',
                        unsafe_allow_html=True,
                    )
                    st.button(
                        "Abrir",
                        icon=":material/arrow_forward:",
                        key=f"ajd_abrir_{chave}",
                        on_click=_ir_para,
                        args=(nome,),
                    )


def _glossario():
    _titulo_secao("Glossário", "Os termos que aparecem no painel, em poucas palavras.")
    termos = "".join(
        f'<div class="ajd-termo"><b>{termo}</b>{definicao}</div>'
        for termo, definicao in GLOSSARIO
    )
    st.markdown(f'<div class="ajd-glossario">{termos}</div>', unsafe_allow_html=True)


def _perguntas():
    _titulo_secao("Perguntas frequentes")
    with st.container(key="ajd_faq"):
        for pergunta, resposta in PERGUNTAS:
            with st.expander(pergunta):
                st.markdown(resposta)


def render_ajuda():
    st.markdown(PAGE_STYLE, unsafe_allow_html=True)

    with st.container(key="ajd_page"):
        st.markdown("""
            <div class="ajd-eyebrow">PAINEL FINANCEIRO</div>
            <div class="ajd-title">Guia do painel</div>
            <div class="ajd-subtitle">
                Veja como transformar dados em decisões melhores.
            </div>
        """, unsafe_allow_html=True)

        _passos()
        _paginas()
        _glossario()
        _perguntas()
