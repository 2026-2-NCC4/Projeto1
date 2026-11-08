"""Base dos relatórios em PDF: layout CTI e blocos reutilizáveis."""
import io
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # sem janela: só gera imagens

import matplotlib.pyplot as plt
from fpdf import FPDF
from fpdf.enums import XPos, YPos

ASSETS = Path(__file__).resolve().parents[1] / "assets"
LOGO = ASSETS / "logo cti 1.png"

# Fonte com acentos e símbolos (−, →, ↑): a DejaVu que já vem com o matplotlib
FONTES = Path(matplotlib.get_data_path()) / "fonts" / "ttf"

AZUL = (0, 75, 133)
TEXTO = (16, 43, 80)
CINZA = (85, 121, 159)
CINZA_CLARO = (138, 164, 191)
LINHA = (220, 232, 242)
FUNDO = (238, 245, 252)
VERDE = (46, 139, 106)
LARANJA = (194, 65, 12)

CORES_GRAFICO = ["#1677E8", "#58B99A", "#E7A23B", "#6D6AE8", "#C65B5B"]


class RelatorioPDF(FPDF):
    """PDF A4 com cabeçalho, rodapé e os blocos usados pelos relatórios."""

    def __init__(self, titulo, subtitulo, filtros):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.titulo_relatorio = titulo
        self.gerado_em = datetime.now().strftime("%d/%m/%Y %H:%M")

        self.add_font("DejaVu", "", str(FONTES / "DejaVuSans.ttf"))
        self.add_font("DejaVu", "B", str(FONTES / "DejaVuSans-Bold.ttf"))
        self.add_font("DejaVu", "I", str(FONTES / "DejaVuSans-Oblique.ttf"))

        self.set_margins(18, 22, 18)
        self.set_auto_page_break(auto=True, margin=20)
        self.set_title(f"CTI | {titulo}")
        self.set_author("CTI Analytics")
        self.alias_nb_pages()
        self.add_page()
        self._capa(titulo, subtitulo, filtros)

    def multi_cell(self, *args, **kwargs):
        # o padrão do fpdf2 é justificado, que abre espaços estranhos nas linhas
        kwargs.setdefault("align", "L")
        return super().multi_cell(*args, **kwargs)

    # ---------- Moldura de todas as páginas ----------

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("DejaVu", "", 8)
        self.set_text_color(*CINZA_CLARO)
        self.set_y(10)
        self.cell(0, 5, f"CTI Analytics  ·  {self.titulo_relatorio}", align="L")
        self.set_draw_color(*LINHA)
        self.line(self.l_margin, 16, self.w - self.r_margin, 16)
        self.set_y(22)

    def footer(self):
        self.set_y(-14)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(*CINZA_CLARO)
        self.cell(0, 5, f"Gerado em {self.gerado_em}", align="L")
        self.set_x(self.l_margin)
        self.cell(0, 5, f"Página {self.page_no()} de {{nb}}", align="R")

    def _capa(self, titulo, subtitulo, filtros):
        # faixa azul no topo da primeira página
        self.set_fill_color(*AZUL)
        self.rect(0, 0, self.w, 34, style="F")
        if LOGO.is_file():
            # o logo é escuro: vai num selo branco
            self.set_fill_color(255, 255, 255)
            self.rect(self.l_margin, 9, 38, 16, style="F", round_corners=True, corner_radius=3)
            self.image(str(LOGO), x=self.l_margin + 3, y=11.5, h=11)
        self.set_font("DejaVu", "B", 9)
        self.set_text_color(255, 255, 255)
        self.set_xy(self.l_margin + 46, 11)
        self.cell(0, 5, "RELATÓRIO INTERPRETATIVO")
        self.set_font("DejaVu", "", 8)
        self.set_xy(self.l_margin + 46, 17)
        self.cell(0, 5, "Plataforma Analítica de Planejamento Financeiro")

        self.set_y(44)
        self.set_font("DejaVu", "B", 20)
        self.set_text_color(*TEXTO)
        self.cell(0, 10, titulo, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("DejaVu", "", 10)
        self.set_text_color(*CINZA)
        self.multi_cell(0, 5, subtitulo, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # filtros usados, para o leitor saber exatamente o recorte
        self.ln(3)
        texto = "   ·   ".join(f"{rotulo}: {valor}" for rotulo, valor in filtros)
        self.set_fill_color(*FUNDO)
        self.set_font("DejaVu", "", 9)
        self.set_text_color(*TEXTO)
        self.multi_cell(0, 8, f"  Recorte do relatório  —  {texto}", fill=True,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)

    # ---------- Blocos ----------

    def secao(self, titulo, nota=None):
        # não deixa o título de uma seção sozinho no fim da página
        if self.get_y() > self.h - 60:
            self.add_page()
        self.ln(3)
        self.set_font("DejaVu", "B", 13)
        self.set_text_color(*TEXTO)
        self.cell(0, 8, titulo, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*AZUL)
        self.set_line_width(0.6)
        self.line(self.l_margin, self.get_y(), self.l_margin + 14, self.get_y())
        self.set_line_width(0.2)
        self.ln(2.5)
        if nota:
            self.set_font("DejaVu", "", 8.5)
            self.set_text_color(*CINZA)
            self.multi_cell(0, 4.5, nota, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(1.5)

    def subtitulo(self, texto):
        if self.get_y() > self.h - 50:
            self.add_page()
        self.set_font("DejaVu", "B", 10)
        self.set_text_color(*TEXTO)
        self.cell(0, 6, texto, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def leitura(self, texto):
        """Frase interpretativa logo abaixo de um gráfico."""
        self.set_font("DejaVu", "", 9)
        self.set_text_color(*CINZA)
        self.set_x(self.l_margin + 2)
        self.multi_cell(0, 4.8, f"Leitura: {texto}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

    def paragrafo(self, texto, tamanho=10):
        self.set_font("DejaVu", "", tamanho)
        self.set_text_color(*TEXTO)
        self.multi_cell(0, 5.4, texto, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1.5)

    def topicos(self, itens):
        self.set_text_color(*TEXTO)
        for item in itens:
            self.set_font("DejaVu", "B", 10)
            self.set_text_color(*AZUL)
            self.cell(5, 5.4, "•")
            self.set_font("DejaVu", "", 10)
            self.set_text_color(*TEXTO)
            self.multi_cell(0, 5.4, item, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(1)

    def bloco_numerado(self, numero, titulo, valor, texto, recomendacao=None):
        """Um destaque: selo com o número, título, valor, explicação e recomendação."""
        largura = self.w - self.l_margin - self.r_margin
        altura_estimada = 16 + self._altura_texto(texto, largura - 16, 9.5, 5) + (6 if recomendacao else 0)
        if self.get_y() + altura_estimada > self.h - 22:
            self.add_page()

        y = self.get_y()
        self.set_fill_color(*AZUL)
        self.rect(self.l_margin, y, 9, 9, style="F", round_corners=True, corner_radius=1.5)
        self.set_xy(self.l_margin, y + 1.8)
        self.set_font("DejaVu", "B", 8.5)
        self.set_text_color(255, 255, 255)
        self.cell(9, 5, f"{numero:02d}", align="C")

        self.set_xy(self.l_margin + 13, y)
        self.set_font("DejaVu", "B", 10.5)
        self.set_text_color(*TEXTO)
        self.cell(0, 5, titulo, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(self.l_margin + 13)
        self.set_font("DejaVu", "B", 13)
        self.set_text_color(*AZUL)
        self.cell(0, 7, valor, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_x(self.l_margin + 13)
        self.set_font("DejaVu", "", 9.5)
        self.set_text_color(*TEXTO)
        self.multi_cell(largura - 13, 5, texto, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if recomendacao:
            self.set_x(self.l_margin + 13)
            self.set_font("DejaVu", "B", 9)
            self.set_text_color(*VERDE)
            self.multi_cell(largura - 13, 5, f"→ {recomendacao}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.ln(2)
        self.set_draw_color(*LINHA)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def destaque(self, titulo, linhas):
        """Bloco azul de conclusão."""
        self.ln(2)
        inicio = self.get_y()
        largura = self.w - self.l_margin - self.r_margin

        # mede a altura antes de desenhar o fundo
        altura = 8 + 7 + sum(self._altura_texto(l, largura - 12, 10, 5.4) + 1 for l in linhas) + 4
        if inicio + altura > self.h - 22:
            self.add_page()
            inicio = self.get_y()

        self.set_fill_color(*AZUL)
        self.rect(self.l_margin, inicio, largura, altura, style="F", round_corners=True, corner_radius=3)
        self.set_xy(self.l_margin + 6, inicio + 5)
        self.set_font("DejaVu", "B", 12)
        self.set_text_color(255, 255, 255)
        self.cell(0, 7, titulo, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("DejaVu", "", 10)
        for linha in linhas:
            self.set_x(self.l_margin + 6)
            self.multi_cell(largura - 12, 5.4, linha, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(1)
        self.set_y(inicio + altura + 4)
        self.set_text_color(*TEXTO)

    def cards(self, itens, por_linha=4):
        """Indicadores em cartões: itens = [(rótulo, valor, nota, tom)].

        tom: "positivo", "negativo" ou None (define a cor da nota).
        """
        largura_total = self.w - self.l_margin - self.r_margin
        espaco = 3
        largura = (largura_total - espaco * (por_linha - 1)) / por_linha
        altura = 22

        for inicio in range(0, len(itens), por_linha):
            if self.get_y() + altura > self.h - 22:
                self.add_page()
            y = self.get_y()
            for i, (rotulo, valor, nota, tom) in enumerate(itens[inicio:inicio + por_linha]):
                x = self.l_margin + i * (largura + espaco)
                self.set_fill_color(*FUNDO)
                self.rect(x, y, largura, altura, style="F", round_corners=True, corner_radius=2)

                self.set_xy(x + 3, y + 2.5)
                self.set_font("DejaVu", "", 7.5)
                self.set_text_color(*CINZA)
                self.cell(largura - 6, 4, rotulo)

                self.set_xy(x + 3, y + 7.5)
                self.set_font("DejaVu", "B", 11.5 if len(valor) <= 14 else 9.5)
                self.set_text_color(*AZUL)
                self.cell(largura - 6, 6, valor)

                self.set_xy(x + 3, y + 15)
                self.set_font("DejaVu", "", 7)
                cor = VERDE if tom == "positivo" else LARANJA if tom == "negativo" else CINZA_CLARO
                self.set_text_color(*cor)
                self.cell(largura - 6, 4, nota)
            self.set_y(y + altura + espaco)
        self.ln(1)

    def tabela(self, cabecalho, linhas, larguras=None):
        self.set_font("DejaVu", "", 8.5)
        self.set_draw_color(*LINHA)
        with self.table(
            col_widths=larguras,
            headings_style=_estilo_cabecalho(),
            line_height=6,
            borders_layout="HORIZONTAL_LINES",
            cell_fill_color=(250, 252, 255),
            cell_fill_mode="ROWS",
            text_align="LEFT",
        ) as tabela:
            linha = tabela.row()
            for titulo in cabecalho:
                linha.cell(titulo)
            for valores in linhas:
                linha = tabela.row()
                for valor in valores:
                    linha.cell(str(valor))
        self.ln(3)

    def grafico(self, figura, titulo=None, largura=None):
        """Insere uma figura do matplotlib (e a fecha), com um título opcional.

        Título e gráfico mudam de página juntos: o título nunca fica sozinho
        no fim de uma página.
        """
        buffer = io.BytesIO()
        figura.savefig(buffer, format="png", dpi=200, bbox_inches="tight")
        plt.close(figura)
        buffer.seek(0)

        largura = largura or (self.w - self.l_margin - self.r_margin)
        proporcao = figura.get_figheight() / figura.get_figwidth()
        altura = largura * proporcao + (7 if titulo else 0) + 12  # + espaço da leitura
        if self.get_y() + altura > self.h - 22:
            self.add_page()
        if titulo:
            self.subtitulo(titulo)
        self.image(buffer, x=self.l_margin, w=largura)
        self.ln(3)

    def aviso(self, texto):
        self.set_font("DejaVu", "I", 8.5)
        self.set_text_color(*CINZA)
        self.multi_cell(0, 4.5, texto, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def _altura_texto(self, texto, largura, tamanho, altura_linha):
        self.set_font("DejaVu", "", tamanho)
        linhas = self.multi_cell(largura, altura_linha, texto, dry_run=True, output="LINES")
        return len(linhas) * altura_linha

    def gerar(self):
        return bytes(self.output())


def _estilo_cabecalho():
    from fpdf.fonts import FontFace

    return FontFace(family="DejaVu", emphasis="BOLD", color=AZUL, fill_color=FUNDO)


# ---------- Gráficos ----------

def figura_linhas(series, titulo_eixo, formato_eixo=None):
    """Gráfico de linhas por ano. series = {nome: pandas.Series indexada por ano}."""
    figura, eixo = plt.subplots(figsize=(7.4, 2.9))
    for cor, (nome, serie) in zip(CORES_GRAFICO, series.items()):
        serie = serie.dropna()
        eixo.plot(serie.index, serie.values, marker="o", markersize=3.5,
                  linewidth=2, color=cor, label=nome)

    eixo.set_ylabel(titulo_eixo, fontsize=8, color="#55799F")
    eixo.set_xlabel("Ano", fontsize=8, color="#55799F")
    eixo.tick_params(labelsize=7.5, colors="#55799F")
    anos = sorted({int(a) for s in series.values() for a in s.dropna().index})
    if anos:
        eixo.set_xticks(anos)
    if formato_eixo:
        eixo.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(formato_eixo))
    eixo.grid(axis="y", color="#EAF0F6", linewidth=0.8)
    for lado in ("top", "right"):
        eixo.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        eixo.spines[lado].set_color("#C3D9F2")
    if len(series) > 1:
        # legenda acima da área do gráfico, para não cobrir as linhas
        eixo.legend(fontsize=7.5, frameon=False, loc="lower left",
                    bbox_to_anchor=(0, 1.0), ncol=len(series))
    figura.tight_layout()
    return figura


def descrever_evolucao(nome, serie, formatar):
    """Frase sobre a evolução de uma série anual: início, fim, variação e maior salto."""
    serie = serie.dropna()
    if len(serie) < 2:
        return None

    inicio_ano, fim_ano = int(serie.index[0]), int(serie.index[-1])
    inicio, fim = float(serie.iloc[0]), float(serie.iloc[-1])
    frase = (
        f"{nome} vai de {formatar(inicio)} no Ano {inicio_ano} para {formatar(fim)} "
        f"no Ano {fim_ano}"
    )
    if abs(inicio) > 1e-12 and (inicio > 0) == (fim > 0):
        variacao = (fim - inicio) / abs(inicio) * 100
        frase += f" ({'+' if variacao >= 0 else '−'}{numero_br(abs(variacao), 0)}%)"

    saltos = serie.diff().dropna()
    if not saltos.empty:
        ano_salto = int(saltos.abs().idxmax())
        direcao = "alta" if saltos[ano_salto] > 0 else "queda"
        frase += f"; a maior {direcao} foi entre os Anos {ano_salto - 1} e {ano_salto}"
    return frase + "."


def numero_br(valor, casas=1):
    """1234.5 -> '1.234,5' (para eixos e tabelas)."""
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
