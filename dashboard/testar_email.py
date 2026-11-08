"""Testa o envio de e-mail da recuperação de senha, sem abrir o app.

Uso (de dentro da pasta dashboard):
    py testar_email.py seu.email@exemplo.com

Lê a seção [smtp] de .streamlit/secrets.toml e envia um código de exemplo
para o endereço informado. Se der erro, mostra o motivo técnico.
"""
import logging
import sys
import tomllib
from pathlib import Path

from data.envio_email import ErroEnvio, configuracao_smtp, enviar_codigo_redefinicao

SECRETS = Path(__file__).resolve().parent / ".streamlit" / "secrets.toml"


def main():
    if len(sys.argv) != 2:
        print("Uso: py testar_email.py seu.email@exemplo.com")
        return 2

    destino = sys.argv[1]

    if not SECRETS.is_file():
        print(f"Arquivo não encontrado: {SECRETS}")
        print("Copie .streamlit/secrets.example.toml para .streamlit/secrets.toml e preencha.")
        return 1

    try:
        config = tomllib.loads(SECRETS.read_text(encoding="utf-8")).get("smtp", {})
    except tomllib.TOMLDecodeError as erro:
        print(f"O secrets.toml tem um erro de formato: {erro}")
        print("Confira as aspas: textos ficam entre aspas, a porta não (porta = 587).")
        return 1

    pronto = configuracao_smtp(config)

    if pronto is None:
        print("A seção [smtp] está incompleta: preencha servidor, porta, usuario e senha.")
        return 1

    print(
        f"Enviando para {destino} via {pronto['servidor']}:{pronto['porta']} "
        f"({pronto['seguranca']}) como {pronto['usuario'] or 'sem login'}..."
    )

    # Mostra no terminal o motivo técnico de uma eventual falha
    logging.basicConfig(level=logging.ERROR, format="  motivo: %(message)s")

    try:
        enviar_codigo_redefinicao(destino, "Teste", "123456", 15, config=config)
    except ErroEnvio:
        print("Falhou. Veja o motivo acima.")
        return 1

    print("Enviado! Confira a caixa de entrada (e o spam).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
