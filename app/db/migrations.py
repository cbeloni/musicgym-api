from __future__ import annotations

from pathlib import Path

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "sql" / "migrations"


def _ensure_migrations_table(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(255) PRIMARY KEY,
                    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )


def _fetch_applied_versions(engine: Engine) -> set[str]:
    with engine.begin() as connection:
        rows = connection.execute(text("SELECT version FROM schema_migrations")).fetchall()
    return {row[0] for row in rows}


def run_migrations(engine: Engine) -> list[str]:
    _ensure_migrations_table(engine)

    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not migration_files:
        return []

    applied_versions = _fetch_applied_versions(engine)
    executed_versions: list[str] = []

    for migration_file in migration_files:
        version = migration_file.stem
        if version in applied_versions:
            continue

        sql = migration_file.read_text(encoding="utf-8").strip()
        if not sql:
            continue

        with engine.begin() as connection:
            # Base.metadata.create_all() runs before migrations. Therefore the
            # rhythm table may already exist even when migration 008 is not
            # registered in schema_migrations yet.
            if version == "008_create_drum_machine_rhythms" and inspect(connection).has_table("drum_machine_rhythms"):
                connection.execute(
                    text("INSERT INTO schema_migrations (version) VALUES (:version)"),
                    {"version": version},
                )
                executed_versions.append(version)
                continue
            # A migração 010 renomeia a tabela das sequências do Virtual Piano.
            # Como o create_all() roda antes, a tabela nova pode já existir
            # (vazia): nesse caso os registros são copiados antes de a tabela
            # antiga ser removida.
            if version == "010_rename_piano_warmups_to_piano_sequences":
                inspector = inspect(connection)
                has_old = inspector.has_table("piano_warmups")
                has_new = inspector.has_table("piano_sequences")
                if has_old and not has_new:
                    connection.execute(text("RENAME TABLE piano_warmups TO piano_sequences"))
                elif has_old and has_new:
                    if connection.execute(text("SELECT COUNT(*) FROM piano_sequences")).scalar() == 0:
                        connection.execute(
                            text(
                                "INSERT INTO piano_sequences "
                                "(id, name, sequence, created_by_id, created_at, updated_at) "
                                "SELECT id, name, sequence, created_by_id, created_at, updated_at "
                                "FROM piano_warmups"
                            )
                        )
                    connection.execute(text("DROP TABLE piano_warmups"))
                connection.execute(
                    text("INSERT INTO schema_migrations (version) VALUES (:version)"),
                    {"version": version},
                )
                executed_versions.append(version)
                continue
            for statement in [part.strip() for part in sql.split(";") if part.strip()]:
                connection.execute(text(statement))
            connection.execute(
                text("INSERT INTO schema_migrations (version) VALUES (:version)"),
                {"version": version},
            )

        executed_versions.append(version)

    return executed_versions
