import smtplib
from email.message import EmailMessage

import streamlit as st

# As credenciais ficam em .streamlit/secrets.toml (fora do git), na seção [smtp].
# Veja o modelo em .streamlit/secrets.example.toml.
CAMPOS_OBRIGATORIOS = ("servidor", "porta", "usuario", "senha")


def configuracao_smtp():
    """Devolve a seção [smtp] dos secrets, ou None se o envio não estiver configurado."""
    try:
        config = dict(st.secrets["smtp"])
    except Exception:
        return None

    if not all(config.get(campo) for campo in CAMPOS_OBRIGATORIOS):
        return None

    return config


def enviar_codigo_redefinicao(destino, nome, codigo, validade_minutos):
    """Envia o código por e-mail. Levanta exceção se o envio falhar."""
    config = configuracao_smtp()

    if config is None:
        raise RuntimeError("Envio de e-mail não configurado.")

    mensagem = EmailMessage()
    mensagem["Subject"] = "CTI | Código para redefinir sua senha"
    mensagem["From"] = config.get("remetente") or config["usuario"]
    mensagem["To"] = destino
    mensagem.set_content(
        f"Olá, {nome}!\n\n"
        f"Seu código para redefinir a senha na plataforma CTI é: {codigo}\n\n"
        f"Ele vale por {validade_minutos} minutos. "
        "Se você não pediu a redefinição, ignore este e-mail; "
        "sua senha continua a mesma.\n"
    )

    with smtplib.SMTP(config["servidor"], int(config["porta"]), timeout=15) as smtp:
        smtp.starttls()
        smtp.login(config["usuario"], config["senha"])
        smtp.send_message(mensagem)
