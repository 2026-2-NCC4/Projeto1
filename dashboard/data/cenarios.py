import re
import pandas as pd


def numero_cenario(valor):
    """Extrai o identificador numérico do cenário."""
    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    encontrados = re.findall(r"\d+", texto)

    if not encontrados:
        return None

    return int(encontrados[-1])


def ordenar_cenarios(valores):
    """Ordena cenários pelo identificador numérico."""
    unicos = list(dict.fromkeys(
        valor for valor in valores if pd.notna(valor)
    ))

    return sorted(
        unicos,
        key=lambda valor: (
            numero_cenario(valor) is None,
            numero_cenario(valor) or 0,
            str(valor)
        )
    )


def mapear_cenarios(valores):
    """
    Retorna um dicionário:
    identificador original -> rótulo de apresentação.
    """
    ordenados = ordenar_cenarios(valores)

    mapa = {}

    for posicao, identificador in enumerate(ordenados, start=1):
        mapa[identificador] = f"Cenário {posicao}"

    return mapa


def rotulo_cenario(valor, mapa=None):
    """Converte um identificador técnico em rótulo amigável."""
    if pd.isna(valor):
        return "Cenário sem identificação"

    if mapa and valor in mapa:
        return mapa[valor]

    numero = numero_cenario(valor)

    if numero is not None:
        return f"Cenário {numero}"

    return str(valor)