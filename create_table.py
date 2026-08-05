import asyncio

from database import conectar

CREATE_TABLE_USUARIOS = """
CREATE TABLE IF NOT EXISTS usuarios (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    login           VARCHAR(20) NOT NULL UNIQUE,
    status          VARCHAR NOT NULL DEFAULT 'A',
    senha           VARCHAR(80) NOT NULL,
    admin           BOOLEAN NOT NULL DEFAULT FALSE,
    data_cadastro   TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
);

COMMENT ON COLUMN usuarios.senha IS 'Hash bcrypt da senha (60 caracteres). Nunca armazenar a senha em texto puro.';
COMMENT ON COLUMN usuarios.admin IS 'Identifica se o usuário é administrador.';
"""

CREATE_TABLE_VISITAS = """
CREATE TABLE IF NOT EXISTS visitas (
    id                      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario              INTEGER NOT NULL REFERENCES usuarios(id),
    nome_visitado           VARCHAR(60) NOT NULL,
    data_visita             TIMESTAMP NOT NULL,
    descricao               VARCHAR(300) NOT NULL,
    visitar_novamente       BOOLEAN NOT NULL DEFAULT FALSE,
    proxima_visita          TIMESTAMP,
    motivo_proxima_visita   VARCHAR(300),
    mostrar_app             BOOLEAN NOT NULL DEFAULT TRUE,
    telefone                VARCHAR(11) NOT NULL,
    endereco                VARCHAR NOT NULL,
    status                  VARCHAR NOT NULL DEFAULT 'A',
    data_cadastro           TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo')
);

COMMENT ON COLUMN visitas.nome_visitado IS 'Nome da pessoa que recebeu a visita de um membro do Ministério de Capelania.';
COMMENT ON COLUMN visitas.descricao IS 'Descrição do que foi conversado durante a visita.';
COMMENT ON COLUMN visitas.visitar_novamente IS 'Identifica se será necessário uma nova visita para essa pessoa.';
COMMENT ON COLUMN visitas.proxima_visita IS 'Data em que a próxima visita deve acontecer.';
COMMENT ON COLUMN visitas.motivo_proxima_visita IS 'Motivo pelo qual a próxima visita deve acontecer.';
COMMENT ON COLUMN visitas.mostrar_app IS 'Identifica se essa visita deve ser mostrada no aplicativo.';
COMMENT ON COLUMN visitas.telefone IS 'Telefone da pessoa que recebeu a visita.';
COMMENT ON COLUMN visitas.endereco IS 'Endereço da pessoa que recebeu a visita.';
COMMENT ON COLUMN visitas.status IS 'Status da visita.';
"""

# Garante a coluna 'status' em bancos criados antes dela existir, já que
# CREATE TABLE IF NOT EXISTS não altera tabelas já existentes.
ADD_COLUMN_STATUS_USUARIOS = """
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS status VARCHAR NOT NULL DEFAULT 'A';
"""

ADD_COLUMN_STATUS_VISITAS = """
ALTER TABLE visitas ADD COLUMN IF NOT EXISTS status VARCHAR NOT NULL DEFAULT 'A';
"""

# Garante a coluna 'admin' em bancos criados antes dela existir, já que
# CREATE TABLE IF NOT EXISTS não altera tabelas já existentes.
ADD_COLUMN_ADMIN_USUARIOS = """
ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS admin BOOLEAN NOT NULL DEFAULT FALSE;
COMMENT ON COLUMN usuarios.admin IS 'Identifica se o usuário é administrador.';
"""

async def main():
    conn = await conectar()
    try:
        await conn.execute(CREATE_TABLE_USUARIOS)
        print("Tabela 'usuarios' criada com sucesso.")
        await conn.execute(CREATE_TABLE_VISITAS)
        print("Tabela 'visitas' criada com sucesso.")
        await conn.execute(ADD_COLUMN_STATUS_USUARIOS)
        await conn.execute(ADD_COLUMN_STATUS_VISITAS)
        print("Coluna 'status' garantida em 'usuarios' e 'visitas'.")
        await conn.execute(ADD_COLUMN_ADMIN_USUARIOS)
        print("Coluna 'admin' garantida em 'usuarios'.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
