import logging
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import make_msgid
from html import escape

import streamlit as st

logger = logging.getLogger(__name__)

# As credenciais ficam em .streamlit/secrets.toml (fora do git), na seção [smtp].
# Veja o passo a passo em .streamlit/secrets.example.toml.
CAMPOS_OBRIGATORIOS = ("servidor", "porta")
SEGURANCAS = ("starttls", "ssl", "nenhuma")
TIMEOUT_SEGUNDOS = 15

AZUL = "#004B85"


class ErroEnvio(RuntimeError):
    """Falha ao enviar e-mail; a mensagem é segura para mostrar ao usuário."""


# ---------- Configuração ----------

def _secao(nome):
    try:
        return dict(st.secrets[nome])
    except Exception:
        return {}


def configuracao_smtp(config=None):
    """Configuração do SMTP pronta para uso, ou None se não estiver configurado.

    `config` permite passar a seção [smtp] diretamente (usado pelo
    testar_email.py, que roda fora do Streamlit).
    """
    config = dict(config) if config is not None else _secao("smtp")

    if not all(config.get(campo) for campo in CAMPOS_OBRIGATORIOS):
        return None

    porta = int(config["porta"])
    # 465 é sempre SSL; nas outras portas o padrão é STARTTLS (Gmail, Outlook: 587)
    seguranca = str(config.get("seguranca") or ("ssl" if porta == 465 else "starttls")).lower()
    if seguranca not in SEGURANCAS:
        seguranca = "starttls"

    # Usuário e senha só são dispensáveis num servidor local de testes
    if seguranca != "nenhuma" and not (config.get("usuario") and config.get("senha")):
        return None

    return {
        "servidor": config["servidor"],
        "porta": porta,
        "seguranca": seguranca,
        "usuario": config.get("usuario", ""),
        # A senha de app do Google é mostrada com espaços; o login não aceita espaços
        "senha": str(config.get("senha", "")).replace(" ", ""),
        "remetente": config.get("remetente") or config.get("usuario") or "nao-responda@cti.local",
    }


def modo_teste():
    """Com [auth] modo_teste = true e sem SMTP, o código aparece na tela.

    Só para desenvolvimento: em produção qualquer pessoa poderia trocar a
    senha de outra sabendo apenas o e-mail dela.
    """
    return bool(_secao("auth").get("modo_teste", False))


# ---------- Envio ----------

def _modelo_html(titulo, paragrafos, destaque=None, observacao=""):
    corpo = "".join(
        f'<p style="margin:0 0 14px;font-size:14px;line-height:1.6;color:#33475B;">{p}</p>'
        for p in paragrafos
    )
    bloco_destaque = ""
    if destaque:
        bloco_destaque = (
            '<div style="margin:6px 0 20px;padding:16px;border-radius:10px;'
            'background:#EEF5FC;text-align:center;font-size:30px;font-weight:700;'
            f'letter-spacing:8px;color:{AZUL};">{escape(destaque)}</div>'
        )
    nota = f"{observacao}<br><br>" if observacao else ""

    return f"""\
<!doctype html>
<html lang="pt-BR">
<body style="margin:0;padding:24px;background:#F4F9FD;font-family:Arial,Helvetica,sans-serif;">
  <div style="max-width:520px;margin:0 auto;background:#FFFFFF;border-radius:14px;overflow:hidden;border:1px solid #DCE8F2;">
    <div style="background:{AZUL};padding:18px 24px;color:#FFFFFF;font-size:18px;font-weight:700;">
      CTI Analytics
    </div>
    <div style="padding:24px;">
      <h1 style="margin:0 0 16px;font-size:20px;color:#102B50;">{titulo}</h1>
      {corpo}
      {bloco_destaque}
      <p style="margin:18px 0 0;font-size:12px;line-height:1.5;color:#8AA4BF;">
        {nota}Este é um e-mail automático da plataforma CTI. Não responda esta mensagem.
      </p>
    </div>
  </div>
</body>
</html>
"""


def _enviar(destino, assunto, texto, html, config=None):
    config = configuracao_smtp(config)

    if config is None:
        raise ErroEnvio("O envio de e-mail não está configurado.")

    mensagem = EmailMessage()
    mensagem["Subject"] = assunto
    mensagem["From"] = config["remetente"]
    mensagem["To"] = destino
    mensagem["Message-ID"] = make_msgid(domain="cti.local")
    mensagem.set_content(texto)
    mensagem.add_alternative(html, subtype="html")

    contexto = ssl.create_default_context()

    try:
        if config["seguranca"] == "ssl":
            conexao = smtplib.SMTP_SSL(
                config["servidor"], config["porta"], timeout=TIMEOUT_SEGUNDOS, context=contexto
            )
        else:
            conexao = smtplib.SMTP(config["servidor"], config["porta"], timeout=TIMEOUT_SEGUNDOS)

        with conexao as smtp:
            if config["seguranca"] == "starttls":
                smtp.starttls(context=contexto)
            if config["usuario"]:
                smtp.login(config["usuario"], config["senha"])
            smtp.send_message(mensagem)

    except smtplib.SMTPAuthenticationError as erro:
        # Detalhe técnico só no terminal; o usuário recebe uma mensagem simples
        logger.error(
            "SMTP recusou o login de %s: %s. Confira o usuário e a senha de app.",
            config["usuario"], erro,
        )
        raise ErroEnvio("Não foi possível enviar o e-mail agora.") from erro
    except (smtplib.SMTPException, OSError) as erro:
        logger.error(
            "Falha ao enviar e-mail por %s:%s: %s", config["servidor"], config["porta"], erro
        )
        raise ErroEnvio("Não foi possível enviar o e-mail agora.") from erro


def enviar_codigo_redefinicao(destino, nome, codigo, validade_minutos, config=None):
    """Envia o código de redefinição. Levanta ErroEnvio se falhar."""
    texto = (
        f"Olá, {nome}!\n\n"
        f"Seu código para redefinir a senha na plataforma CTI é: {codigo}\n\n"
        f"Ele vale por {validade_minutos} minutos e só pode ser usado uma vez.\n"
        "Se você não pediu a redefinição, ignore este e-mail: sua senha continua a mesma.\n"
    )
    html = _modelo_html(
        "Código para redefinir sua senha",
        [
            f"Olá, {escape(nome)}!",
            "Use o código abaixo na tela de redefinição de senha da plataforma CTI.",
        ],
        destaque=codigo,
        observacao=(
            f"O código vale por {validade_minutos} minutos e só pode ser usado uma vez. "
            "Se você não pediu a redefinição, ignore este e-mail: sua senha continua a mesma."
        ),
    )
    _enviar(destino, "CTI | Código para redefinir sua senha", texto, html, config)


def enviar_aviso_senha_alterada(destino, nome, config=None):
    """Avisa que a senha mudou. Levanta ErroEnvio se falhar."""
    texto = (
        f"Olá, {nome}!\n\n"
        "A senha da sua conta na plataforma CTI acabou de ser alterada.\n\n"
        "Se foi você, está tudo certo. Se não foi, use “Esqueceu sua senha?” na tela "
        "de entrada para criar uma nova senha agora mesmo.\n"
    )
    html = _modelo_html(
        "Sua senha foi alterada",
        [
            f"Olá, {escape(nome)}!",
            "A senha da sua conta na plataforma CTI acabou de ser alterada.",
            "Se foi você, está tudo certo. Se não foi, use <b>“Esqueceu sua senha?”</b> "
            "na tela de entrada para criar uma nova senha agora mesmo.",
        ],
    )
    _enviar(destino, "CTI | Sua senha foi alterada", texto, html, config)


def avisar_senha_alterada(destino, nome):
    """Versão que nunca falha: o aviso é um extra, não pode travar a troca de senha."""
    if configuracao_smtp() is None:
        return
    try:
        enviar_aviso_senha_alterada(destino, nome)
    except ErroEnvio:
        pass  # já registrado no log
