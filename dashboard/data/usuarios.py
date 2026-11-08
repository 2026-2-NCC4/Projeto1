import hashlib
import hmac
import re
import secrets
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path


CAMINHO_BANCO = Path(__file__).resolve().parent / "usuarios.db"

ALGORITMO = "pbkdf2_sha256"
ITERACOES = 600_000

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


VALIDADE_CODIGO_MINUTOS = 15
MAX_TENTATIVAS_CODIGO = 5
INTERVALO_REENVIO_SEGUNDOS = 60

VALIDADE_SESSAO_DIAS = 30


class ErroCadastro(ValueError):
    pass


@contextmanager
def _conectar():
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

            conexao.execute("""
                CREATE TABLE IF NOT EXISTS redefinicoes_senha (
                    email TEXT PRIMARY KEY COLLATE NOCASE,
                    codigo_hash TEXT NOT NULL,
                    criado_em REAL NOT NULL,
                    expira_em REAL NOT NULL,
                    tentativas INTEGER NOT NULL DEFAULT 0
                )
            """)

            conexao.execute("""
                CREATE TABLE IF NOT EXISTS preferencias (
                    usuario_id INTEGER PRIMARY KEY,
                    pagina_inicial TEXT,
                    menu_recolhido INTEGER NOT NULL DEFAULT 0
                )
            """)
            conexao.execute("""
                CREATE TABLE IF NOT EXISTS sessoes_persistentes (
                    token_hash TEXT PRIMARY KEY,
                    usuario_id INTEGER NOT NULL,
                    expira_em REAL NOT NULL
                )
            """)
            yield conexao
    finally:
        conexao.close()


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


_HASH_FICTICIO = gerar_hash(secrets.token_hex(16))


def normalizar_email(email):
    return email.strip().lower()


def validar_cadastro(nome, email, senha, confirmar):
    if not all([nome.strip(), email.strip(), senha, confirmar]):
        raise ErroCadastro("Preencha todos os campos.")

    if len(nome.strip()) < 3:
        raise ErroCadastro("Informe seu nome completo.")

    if not EMAIL_REGEX.match(normalizar_email(email)):
        raise ErroCadastro("Informe um e-mail válido.")

    validar_senha(senha, confirmar)


def validar_senha(senha, confirmar):
    if not senha or not confirmar:
        raise ErroCadastro("Preencha a senha e a confirmação.")

    if len(senha) < 8:
        raise ErroCadastro("A senha deve ter pelo menos 8 caracteres.")

    if not (re.search(r"[A-Za-z]", senha) and re.search(r"\d", senha)):
        raise ErroCadastro("A senha deve conter letras e números.")

    if senha != confirmar:
        raise ErroCadastro("As senhas não coincidem.")


def cadastrar_usuario(nome, email, senha, confirmar):
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


def _hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def criar_sessao_persistente(usuario_id):
    token = secrets.token_urlsafe(32)
    agora = time.time()

    with _conectar() as conexao:
        conexao.execute(
            "DELETE FROM sessoes_persistentes WHERE expira_em < ?", (agora,)
        )
        conexao.execute(
            "INSERT INTO sessoes_persistentes (token_hash, usuario_id, expira_em) "
            "VALUES (?, ?, ?)",
            (_hash_token(token), usuario_id, agora + VALIDADE_SESSAO_DIAS * 86400),
        )

    return token


def usuario_por_token(token):
    if not token:
        return None

    with _conectar() as conexao:
        linha = conexao.execute(
            "SELECT u.id, u.nome, u.email FROM sessoes_persistentes s "
            "JOIN usuarios u ON u.id = s.usuario_id "
            "WHERE s.token_hash = ? AND s.expira_em > ?",
            (_hash_token(token), time.time()),
        ).fetchone()

    if linha is None:
        return None

    return {"id": linha["id"], "nome": linha["nome"], "email": linha["email"]}


def encerrar_sessao_persistente(token):
    if not token:
        return

    with _conectar() as conexao:
        conexao.execute(
            "DELETE FROM sessoes_persistentes WHERE token_hash = ?",
            (_hash_token(token),),
        )


def gerar_codigo_redefinicao(email):
    email = normalizar_email(email)
    agora = time.time()

    with _conectar() as conexao:
        usuario = conexao.execute(
            "SELECT nome FROM usuarios WHERE email = ?", (email,)
        ).fetchone()

        if usuario is None:
            return None

        anterior = conexao.execute(
            "SELECT criado_em FROM redefinicoes_senha WHERE email = ?", (email,)
        ).fetchone()

        if anterior and agora - anterior["criado_em"] < INTERVALO_REENVIO_SEGUNDOS:
            return None

        codigo = f"{secrets.randbelow(10 ** 6):06d}"
        conexao.execute(
            """
            INSERT OR REPLACE INTO redefinicoes_senha
                (email, codigo_hash, criado_em, expira_em, tentativas)
            VALUES (?, ?, ?, ?, 0)
            """,
            (email, gerar_hash(codigo), agora, agora + VALIDADE_CODIGO_MINUTOS * 60),
        )

    return usuario["nome"], codigo


def cancelar_codigo_redefinicao(email):
    """Apaga o código pendente (ex.: o e-mail não pôde ser enviado).

    Sem isso, o intervalo mínimo entre pedidos bloquearia uma nova tentativa
    logo em seguida, e a pessoa ficaria esperando um e-mail que nunca saiu.
    """
    with _conectar() as conexao:
        conexao.execute(
            "DELETE FROM redefinicoes_senha WHERE email = ?", (normalizar_email(email),)
        )


def redefinir_senha(email, codigo, senha, confirmar):
    """Troca a senha se o código for válido e devolve (id, nome, email)."""
    email = normalizar_email(email)
    codigo = codigo.strip()

    if not codigo:
        raise ErroCadastro("Informe o código recebido por e-mail.")

    validar_senha(senha, confirmar)

    with _conectar() as conexao:
        pedido = conexao.execute(
            "SELECT codigo_hash, expira_em, tentativas FROM redefinicoes_senha WHERE email = ?",
            (email,),
        ).fetchone()

        if pedido is None or time.time() > pedido["expira_em"]:
            raise ErroCadastro("Código inválido ou expirado. Solicite um novo código.")

        if not verificar_senha(codigo, pedido["codigo_hash"]):
            tentativas = pedido["tentativas"] + 1

            if tentativas >= MAX_TENTATIVAS_CODIGO:
                conexao.execute("DELETE FROM redefinicoes_senha WHERE email = ?", (email,))
                conexao.commit()
                raise ErroCadastro("Muitas tentativas com código errado. Solicite um novo código.")

            conexao.execute(
                "UPDATE redefinicoes_senha SET tentativas = ? WHERE email = ?",
                (tentativas, email),
            )
            conexao.commit()
            raise ErroCadastro("Código incorreto.")

        conexao.execute(
            "UPDATE usuarios SET senha_hash = ? WHERE email = ?",
            (gerar_hash(senha), email),
        )
        conexao.execute(
            "DELETE FROM sessoes_persistentes WHERE usuario_id IN "
            "(SELECT id FROM usuarios WHERE email = ?)",
            (email,),
        )
        conexao.execute("DELETE FROM redefinicoes_senha WHERE email = ?", (email,))
        usuario = conexao.execute(
            "SELECT id, nome, email FROM usuarios WHERE email = ?", (email,)
        ).fetchone()

    # Dados públicos, para o aviso de "senha alterada" por e-mail
    return dict(usuario)


def obter_usuario(usuario_id):
    with _conectar() as conexao:
        linha = conexao.execute(
            "SELECT id, nome, email, criado_em FROM usuarios WHERE id = ?",
            (usuario_id,),
        ).fetchone()

    return dict(linha) if linha else None


def atualizar_nome(usuario_id, nome):
    nome = nome.strip()

    if len(nome) < 3:
        raise ErroCadastro("Informe seu nome completo.")

    with _conectar() as conexao:
        conexao.execute("UPDATE usuarios SET nome = ? WHERE id = ?", (nome, usuario_id))

    return nome


def _confere_senha_atual(conexao, usuario_id, senha):
    linha = conexao.execute(
        "SELECT senha_hash FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()

    if linha is None or not verificar_senha(senha, linha["senha_hash"]):
        raise ErroCadastro("Senha atual incorreta.")


def alterar_senha(usuario_id, senha_atual, nova, confirmar):
    if not senha_atual:
        raise ErroCadastro("Informe a senha atual.")

    validar_senha(nova, confirmar)

    if nova == senha_atual:
        raise ErroCadastro("A nova senha deve ser diferente da atual.")

    with _conectar() as conexao:
        _confere_senha_atual(conexao, usuario_id, senha_atual)
        conexao.execute(
            "UPDATE usuarios SET senha_hash = ? WHERE id = ?",
            (gerar_hash(nova), usuario_id),
        )
        conexao.execute(
            "DELETE FROM sessoes_persistentes WHERE usuario_id = ?", (usuario_id,)
        )


def excluir_conta(usuario_id, senha):
    if not senha:
        raise ErroCadastro("Informe sua senha para confirmar.")

    with _conectar() as conexao:
        _confere_senha_atual(conexao, usuario_id, senha)
        email = conexao.execute(
            "SELECT email FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()["email"]

        conexao.execute("DELETE FROM preferencias WHERE usuario_id = ?", (usuario_id,))
        conexao.execute("DELETE FROM sessoes_persistentes WHERE usuario_id = ?", (usuario_id,))
        conexao.execute("DELETE FROM redefinicoes_senha WHERE email = ?", (email,))
        conexao.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))


def obter_preferencias(usuario_id):
    with _conectar() as conexao:
        linha = conexao.execute(
            "SELECT pagina_inicial, menu_recolhido FROM preferencias WHERE usuario_id = ?",
            (usuario_id,),
        ).fetchone()

    if linha is None:
        return {"pagina_inicial": None, "menu_recolhido": False}

    return {
        "pagina_inicial": linha["pagina_inicial"],
        "menu_recolhido": bool(linha["menu_recolhido"]),
    }


def salvar_preferencias(usuario_id, pagina_inicial, menu_recolhido):
    with _conectar() as conexao:
        conexao.execute(
            """
            INSERT OR REPLACE INTO preferencias (usuario_id, pagina_inicial, menu_recolhido)
            VALUES (?, ?, ?)
            """,
            (usuario_id, pagina_inicial, int(menu_recolhido)),
        )