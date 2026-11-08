"""Confere se as bibliotecas do requirements.txt estão instaladas.

A lista vem do próprio requirements.txt, então só existe um lugar para manter.
Rodando este arquivo direto (py dependencias.py), mostra o que falta.
"""
import importlib.util
import re
import sys
from pathlib import Path

REQUIREMENTS = Path(__file__).resolve().parent / "requirements.txt"

# Nome no pip -> nome usado no import, quando os dois são diferentes
NOME_DO_IMPORT = {
    "pillow": "PIL",
    "fpdf2": "fpdf",
}

COMANDO = "py -m pip install -r requirements.txt"


def bibliotecas():
    """Nomes do pip listados no requirements.txt."""
    conteudo = REQUIREMENTS.read_bytes()
    # "pip freeze > requirements.txt" no PowerShell grava em UTF-16
    if conteudo[:2] in (b"\xff\xfe", b"\xfe\xff"):
        texto = conteudo.decode("utf-16")
    else:
        texto = conteudo.decode("utf-8-sig")

    nomes = []
    for linha in texto.splitlines():
        linha = linha.split("#", 1)[0].strip()
        if linha:
            nomes.append(re.split(r"[<>=!~\[ ;]", linha, maxsplit=1)[0].strip())
    return nomes


def faltando():
    """Bibliotecas do requirements.txt que não estão instaladas neste Python."""
    return [
        nome for nome in bibliotecas()
        if importlib.util.find_spec(NOME_DO_IMPORT.get(nome.lower(), nome)) is None
    ]


if __name__ == "__main__":
    ausentes = faltando()
    if ausentes:
        print("Faltam:", ", ".join(ausentes))
        print(f"Instale com (de dentro da pasta dashboard):  {COMANDO}")
        sys.exit(1)
    print(f"Tudo instalado ({len(bibliotecas())} bibliotecas).")
