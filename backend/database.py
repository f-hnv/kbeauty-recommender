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


settings = Settings() 

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
    db.execute(text("SET LOCAL app.current_user_id = :uid"), {"uid": usuario_id})
