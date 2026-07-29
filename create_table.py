import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

CREATE_TABLE_USUARIOS = """
CREATE TABLE IF NOT EXISTS usuarios (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    login           VARCHAR NOT NULL UNIQUE,
    status          VARCHAR NOT NULL DEFAULT 'A',
    senha           VARCHAR(12) NOT NULL,
    data_cadastro   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

def main():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "capelania"),
        user=os.getenv("DB_USER", "capelania"),
        password=os.getenv("DB_PASSWORD", "159753"),
    )
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(CREATE_TABLE_USUARIOS)
        print("Tabela 'usuarios' criada com sucesso.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
