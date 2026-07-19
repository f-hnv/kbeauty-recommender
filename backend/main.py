import unicodedata
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db, settings
from models import Producto

app = FastAPI(
    title="Skincare Routine API",
    description="Genera una rutina de skincare completa segun el perfil del usuario",
    version="0.6.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

PASOS_RUTINA = ["limpiador", "tonico", "serum", "crema_hidratante"]

NOMBRE_PASO = {
    "limpiador": "Limpiador",
    "tonico": "Tónico",
    "serum": "Serum",
    "crema_hidratante": "Crema Hidratante",
}

# Funcion GENERICA de cada paso (no depende del producto elegido)
FUNCION_PASO = {
    "limpiador": "Elimina impurezas, exceso de sebo y residuos de protector solar/maquillaje sin resecar la piel, dejandola lista para el resto de la rutina.",
    "tonico": "Reequilibra el pH de la piel despues de la limpieza y ayuda a que los siguientes productos se absorban mejor.",
    "serum": "Aporta una concentracion alta de ingredientes activos enfocados en una preocupacion especifica (acne, manchas, hidratacion, etc).",
    "crema_hidratante": "Sella la hidratacion de los pasos anteriores y refuerza la barrera cutanea, reduciendo la perdida de agua a lo largo del dia.",
}

TASAS_CAMBIO = {
    "CL": {"moneda": "CLP", "tasa": 950},
    "US": {"moneda": "USD", "tasa": 1},
}
TASA_DEFAULT = {"moneda": "USD", "tasa": 1}


def normalizar(texto: str) -> str:
    if texto is None:
        return ""
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sin_tildes.strip().lower()


def convertir_precio(precio_usd: float, pais: str) -> tuple[float, str]:
    info = TASAS_CAMBIO.get(pais.upper(), TASA_DEFAULT)
    return round(float(precio_usd) * info["tasa"], 2), info["moneda"]


class PerfilRequest(BaseModel):
    tipo_piel: str
    preocupaciones: List[str] = []
    presupuesto_max_usd: Optional[float] = Field(default=None, ge=0)
    pais: str = "CL"


class PasoRutinaResponse(BaseModel):
    paso: str                    # "Limpiador", "Tónico", ...
    funcion_paso: str            # que hace este paso en general
    nombre_producto: str
    origen: str
    razon_recomendacion: str     # por que ESTE producto para ESTE tipo de piel
    precio_local: float
    moneda_local: str
    link_compra: Optional[str] = None


class RutinaResponse(BaseModel):
    rutina: List[PasoRutinaResponse]
    mensaje: Optional[str] = None


def _score(producto: Producto, preocupaciones_norm: List[str]) -> float:
    coincidencias = set(preocupaciones_norm) & set(producto.preocupaciones or [])
    return 3.0 * len(coincidencias)


@app.get("/")
def health_check():
    return {"status": "ok", "servicio": "skincare-routine-api"}


@app.post("/recomendar", response_model=RutinaResponse)
def recomendar_rutina(perfil: PerfilRequest, db: Session = Depends(get_db)):
    tipo_piel_norm = normalizar(perfil.tipo_piel)
    preocupaciones_norm = [normalizar(p) for p in perfil.preocupaciones]

    rutina = []
    hubo_fallback_presupuesto = False

    for paso in PASOS_RUTINA:
        # Traemos de la BD todos los productos de este paso; el filtro
        # de tipo de piel se hace en Python porque el catalogo es chico
        # y evita depender de sintaxis especifica de arrays de Postgres.
        productos_paso = db.query(Producto).filter(
            Producto.categoria_paso == paso,
            Producto.activo == True,  # noqa: E712
        ).all()

        candidatos = [
            p for p in productos_paso if tipo_piel_norm in (p.tipos_piel or [])
        ]

        if not candidatos:
            # No hay ningun producto de este paso para ese tipo de piel.
            # No debería pasar con el catalogo de prueba, pero si el
            # catalogo real queda incompleto, es mejor omitir el paso
            # que romper toda la rutina.
            continue

        # Filtro de presupuesto POR PASO (soft limit, mismo criterio
        # que ya usamos antes: si nadie entra, cae al mas barato).
        elegido = None
        if perfil.presupuesto_max_usd is not None:
            dentro = [p for p in candidatos if float(p.precio_usd) <= perfil.presupuesto_max_usd]
            if dentro:
                elegido = max(dentro, key=lambda p: _score(p, preocupaciones_norm))
            else:
                elegido = min(candidatos, key=lambda p: float(p.precio_usd))
                hubo_fallback_presupuesto = True
        else:
            elegido = max(candidatos, key=lambda p: _score(p, preocupaciones_norm))

        precio_local, moneda_local = convertir_precio(elegido.precio_usd, perfil.pais)

        rutina.append(PasoRutinaResponse(
            paso=NOMBRE_PASO[paso],
            funcion_paso=FUNCION_PASO[paso],
            nombre_producto=elegido.nombre_producto,
            origen=elegido.origen,
            razon_recomendacion=elegido.razon_tipo_piel,
            precio_local=precio_local,
            moneda_local=moneda_local,
            link_compra=elegido.link_compra,
        ))

    if not rutina:
        raise HTTPException(
            status_code=404,
            detail="No se pudo armar una rutina para ese tipo de piel con el catalogo actual.",
        )

    mensaje = None
    if hubo_fallback_presupuesto:
        mensaje = (
            "El presupuesto ingresado no alcanzaba para algunos pasos con mejor "
            "match; se eligieron las alternativas mas economicas para completar la rutina."
        )

    return RutinaResponse(rutina=rutina, mensaje=mensaje)


# Ejemplo de request:
# {"tipo_piel": "grasa_mixta", "preocupaciones": ["acne"], "pais": "CL"}
