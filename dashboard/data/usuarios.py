import hashlib
import hmac
import re
import secrets
import sqlite3
from contextlib import contextmanager
from pathlib import Path

# Banco local com os usuários cadastrados (não versionado no git)
CAMINHO_BANCO = Path(__file__).resolve().parent / "usuarios.db"

ALGORITMO = "pbkdf2_sha256"
ITERACOES = 600_000

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ErroCadastro(ValueError):
    """Erro de validação com mensagem pronta para exibir ao usuário."""


@contextmanager
def _conectar():
    """Abre o banco, confirma a transação no final e sempre fecha a conexão."""
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row

    try:
        with conexao:
            conexao.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    senha_hash TEXT NOT NULL,
                    criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            yield conexao
    finally:
        conexao.close()


# ---------- Senhas ----------

def gerar_hash(senha):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, ITERACOES)
    return f"{ALGORITMO}${ITERACOES}${salt.hex()}${digest.hex()}"


def verificar_senha(senha, senha_hash):
    try:
        algoritmo, iteracoes, salt, esperado = senha_hash.split("$")
    except ValueError:
        return False

    if algoritmo != ALGORITMO:
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        bytes.fromhex(salt),
        int(iteracoes),
    )
    return hmac.compare_digest(digest.hex(), esperado)


# Usado para gastar o mesmo tempo quando o e-mail não existe,
# evitando revelar quais e-mails estão cadastrados.
_HASH_FICTICIO = gerar_hash(secrets.token_hex(16))


# ---------- Validação ----------

def normalizar_email(email):
    return email.strip().lower()


def validar_cadastro(nome, email, senha, confirmar):
    if not all([nome.strip(), email.strip(), senha, confirmar]):
        raise ErroCadastro("Preencha todos os campos.")

    if len(nome.strip()) < 3:
        raise ErroCadastro("Informe seu nome completo.")

    if not EMAIL_REGEX.match(normalizar_email(email)):
        raise ErroCadastro("Informe um e-mail válido.")

    if len(senha) < 8:
        raise ErroCadastro("A senha deve ter pelo menos 8 caracteres.")

    if not (re.search(r"[A-Za-z]", senha) and re.search(r"\d", senha)):
        raise ErroCadastro("A senha deve conter letras e números.")

    if senha != confirmar:
        raise ErroCadastro("As senhas não coincidem.")


# ---------- Operações ----------

def cadastrar_usuario(nome, email, senha, confirmar):
    """Cria o usuário e devolve seus dados públicos (id, nome, email)."""
    validar_cadastro(nome, email, senha, confirmar)

    nome = nome.strip()
    email = normalizar_email(email)

    try:
        with _conectar() as conexao:
            cursor = conexao.execute(
                "INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)",
                (nome, email, gerar_hash(senha)),
            )
    except sqlite3.IntegrityError:
        raise ErroCadastro("Já existe uma conta com este e-mail.") from None

    return {"id": cursor.lastrowid, "nome": nome, "email": email}


def autenticar(email, senha):
    """Devolve os dados públicos do usuário, ou None se as credenciais forem inválidas."""
    with _conectar() as conexao:
        linha = conexao.execute(
            "SELECT id, nome, email, senha_hash FROM usuarios WHERE email = ?",
            (normalizar_email(email),),
        ).fetchone()

    if linha is None:
        verificar_senha(senha, _HASH_FICTICIO)
        return None

    if not verificar_senha(senha, linha["senha_hash"]):
        return None

    return {"id": linha["id"], "nome": linha["nome"], "email": linha["email"]}
