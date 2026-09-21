-- Renomeia a tabela das sequências salvas do Virtual Piano (antes "aquecimentos").
-- O runner (app/db/migrations.py) executa esta migração de forma idempotente: se o
-- Base.metadata.create_all() já criou piano_sequences, os registros de piano_warmups
-- são copiados antes de a tabela antiga ser removida.
RENAME TABLE piano_warmups TO piano_sequences;
