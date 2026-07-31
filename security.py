import bcrypt

# O algoritmo bcrypt so processa os primeiros 72 bytes da senha.
TAMANHO_MAXIMO_SENHA = 72


def gerar_hash_senha(senha: str) -> str:
    """Gera o hash bcrypt da senha para ser gravado no banco."""

    senha_bytes = senha.encode("utf-8")
    if len(senha_bytes) > TAMANHO_MAXIMO_SENHA:
        raise ValueError(
            f"A senha deve ter no máximo {TAMANHO_MAXIMO_SENHA} caracteres."
        )

    return bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """Confere se a senha informada corresponde ao hash gravado no banco."""

    try:
        return bcrypt.checkpw(
            senha.encode("utf-8"),
            hash_armazenado.encode("utf-8"),
        )
    except ValueError:
        # Hash invalido ou gravado antes da criptografia (senha em texto puro).
        return False
