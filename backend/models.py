"""
models.py — Modelos ORM de SQLAlchemy, mapeados 1:1 a schema_bd_v2.sql.
"""

from sqlalchemy import Column, String, Numeric, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func

from database import Base


class Producto(Base):
    __tablename__ = "productos"

    producto_id = Column(String(20), primary_key=True)
    nombre_producto = Column(String(150), nullable=False)
    origen = Column(String(20), nullable=False)
    categoria_paso = Column(String(20), nullable=False)  # limpiador/tonico/serum/crema_hidratante
    ingrediente_clave = Column(String(100), nullable=False)
    ingredientes_full = Column(Text)

    tipos_piel = Column(ARRAY(String(20)), nullable=False)
    preocupaciones = Column(ARRAY(String(30)), nullable=False)
    razon_tipo_piel = Column(Text, nullable=False)
    link_compra = Column(Text, nullable=False)

    satisfaccion_promedio = Column(Numeric(3, 2))
    mejora_acne_pct = Column(Numeric(5, 2))
    mejora_manchas_pct = Column(Numeric(5, 2))
    mejora_textura_pct = Column(Numeric(5, 2))
    tolerancia_piel_sensible_pct = Column(Numeric(5, 2))

    precio_usd = Column(Numeric(8, 2), nullable=False)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, server_default=func.now())
    actualizado_en = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<Producto {self.producto_id} - {self.nombre_producto}>"
