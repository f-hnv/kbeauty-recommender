"""
database.py — Conexión a PostgreSQL. Cero credenciales hardcodeadas:
todo se lee desde variables de entorno (via un archivo .env local que
NUNCA se sube a git — ver .env.example).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session


class Settings(BaseSettings):
    database_url: str
    allowed_origins: str = "http://localhost:5500,http://127.0.0.1:5500"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


settings = Settings()  # lee DATABASE_URL / ALLOWED_ORIGINS desde .env o el entorno

engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency de FastAPI: una sesion por request, se cierra siempre al final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def set_current_user(db: Session, usuario_id: str) -> None:
    """
    Fija el usuario "actual" para esta sesion de Postgres, requerido por
    las policies de RLS en perfiles_usuario / recomendaciones_generadas
    (ver schema_bd.sql). Debe llamarse ANTES de leer/escribir esas tablas.

    Nota: hoy la app todavia no tiene login real, asi que usuario_id es
    un UUID anonimo generado en el frontend (ver index.html). El dia que
    haya autenticacion real, aca simplemente se pasa el id del usuario
    autenticado — las policies de RLS no cambian.
    """
    db.execute(text("SET LOCAL app.current_user_id = :uid"), {"uid": usuario_id})
