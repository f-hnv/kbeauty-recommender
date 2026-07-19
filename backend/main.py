"""
main.py — v4:
  1) Presupuesto "soft limit": si nadie califica dentro del presupuesto,
     devuelve las opciones mas economicas que sí matchean el perfil,
     en vez de dejar la lista vacía.
  2) Tipo de piel 'grasa' y 'mixta' unificados en 'grasa_mixta'.
  3) Solo paises CL y US (se elimina MX).

Correr:
    uvicorn main:app --reload
"""

import unicodedata
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Skincare Recommendation API",
    description="API de recomendacion K-Beauty vs Tradicional (modo prueba)",
    version="0.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalizar(texto: str) -> str:
    if texto is None:
        return ""
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return sin_tildes.strip().lower()


# --- Tasas de conversion de PRUEBA — solo CL y US por ahora ---
TASAS_CAMBIO = {
    "CL": {"moneda": "CLP", "tasa": 950},
    "US": {"moneda": "USD", "tasa": 1},
}
TASA_DEFAULT = {"moneda": "USD", "tasa": 1}


def convertir_precio(precio_usd: float, pais: str) -> tuple[float, str]:
    info = TASAS_CAMBIO.get(pais.upper(), TASA_DEFAULT)
    precio_convertido = round(precio_usd * info["tasa"], 2)
    return precio_convertido, info["moneda"]


class PerfilRequest(BaseModel):
    tipo_piel: str
    preocupaciones: List[str]
    presupuesto_max_usd: Optional[float] = Field(default=None, ge=0)
    pais: str = "CL"


class ProductoResponse(BaseModel):
    nombre: str
    origen: str
    ingrediente_clave: str
    precio_local: float
    moneda_local: str
    score_match: float
    link_compra: Optional[str] = None


class RecomendacionResponse(BaseModel):
    resultados: List[ProductoResponse]
    mensaje: Optional[str] = None


# --- Catalogo: 'grasa' y 'mixta' ya unificados como 'grasa_mixta' ---
CATALOGO = [
    {
        "nombre": "Skin1004 Madagascar Centella Ampoule",
        "origen": "Coreano",
        "ingrediente_clave": "centella asiatica",
        "tipos_piel": ["grasa_mixta", "sensible"],
        "preocupaciones": ["acne", "rojeces"],
        "precio_usd": 17.0,
        "link_compra": "https://skin1004.com/",
    },
    {
        "nombre": "COSRX Advanced Snail 96 Mucin Power Essence",
        "origen": "Coreano",
        "ingrediente_clave": "mucina de caracol",
        "tipos_piel": ["seca", "normal", "grasa_mixta"],
        "preocupaciones": ["textura_irregular", "deshidratacion"],
        "precio_usd": 19.5,
        "link_compra": "https://www.cosrx.com/",
    },
    {
        "nombre": "Beauty of Joseon Glow Serum",
        "origen": "Coreano",
        "ingrediente_clave": "propoleo + niacinamida",
        "tipos_piel": ["normal", "grasa_mixta", "seca"],
        "preocupaciones": ["manchas", "textura_irregular"],
        "precio_usd": 16.0,
        "link_compra": "https://beautyofjoseon.com/",
    },
    {
        "nombre": "Some By Mi AHA-BHA-PHA 30 Days Miracle Toner",
        "origen": "Coreano",
        "ingrediente_clave": "complejo AHA/BHA/PHA",
        "tipos_piel": ["grasa_mixta"],
        "preocupaciones": ["acne", "textura_irregular"],
        "precio_usd": 22.0,
        "link_compra": "https://somebymi.com/",
    },
    {
        "nombre": "Etude House SoonJung Calming Serum",
        "origen": "Coreano",
        "ingrediente_clave": "panthenol + centella",
        "tipos_piel": ["sensible", "seca"],
        "preocupaciones": ["rojeces", "deshidratacion"],
        "precio_usd": 15.0,
        "link_compra": "https://etudehouse.com/",
    },
    {
        "nombre": "The Ordinary Niacinamide 10% + Zinc 1%",
        "origen": "Tradicional",
        "ingrediente_clave": "niacinamida",
        "tipos_piel": ["grasa_mixta"],
        "preocupaciones": ["acne", "manchas"],
        "precio_usd": 9.0,
        "link_compra": "https://theordinary.com/",
    },
    {
        "nombre": "CeraVe Moisturizing Cream",
        "origen": "Tradicional",
        "ingrediente_clave": "ceramidas",
        "tipos_piel": ["seca", "sensible", "normal"],
        "preocupaciones": ["deshidratacion", "rojeces"],
        "precio_usd": 16.0,
        "link_compra": "https://www.cerave.com/",
    },
]


def score_producto(producto: dict, tipo_piel: str, preocupaciones: List[str]) -> float:
    score = 0.0
    if tipo_piel in producto["tipos_piel"]:
        score += 5.0
    coincidencias = set(preocupaciones) & set(producto["preocupaciones"])
    score += 3.0 * len(coincidencias)
    return score


@app.get("/")
def health_check():
    return {"status": "ok", "servicio": "skincare-recommendation-api"}


@app.post("/recomendar", response_model=RecomendacionResponse)
def recomendar_productos(perfil: PerfilRequest):
    if not perfil.preocupaciones:
        raise HTTPException(
            status_code=400,
            detail="Debes indicar al menos una preocupacion de piel.",
        )

    tipo_piel_norm = normalizar(perfil.tipo_piel)
    preocupaciones_norm = [normalizar(p) for p in perfil.preocupaciones]

    # --- 1. Match por perfil (tipo de piel + preocupaciones), SIN mirar presupuesto ---
    candidatos_perfil = []
    for producto in CATALOGO:
        score = score_producto(producto, tipo_piel_norm, preocupaciones_norm)
        if score > 0:
            candidatos_perfil.append((producto, score))

    if not candidatos_perfil:
        return RecomendacionResponse(
            resultados=[],
            mensaje="No se encontraron productos que coincidan con tu tipo de piel o preocupaciones.",
        )

    # --- 2. Presupuesto: soft limit con fallback a las opciones mas economicas ---
    mensaje = None
    if perfil.presupuesto_max_usd is not None:
        dentro_presupuesto = [
            (p, s) for p, s in candidatos_perfil if p["precio_usd"] <= perfil.presupuesto_max_usd
        ]
        if dentro_presupuesto:
            candidatos = sorted(dentro_presupuesto, key=lambda x: x[1], reverse=True)
        else:
            # Nadie que matchea el perfil entra en el presupuesto ->
            # ofrecemos las mas economicas que SI matchean el perfil.
            candidatos = sorted(candidatos_perfil, key=lambda x: x[0]["precio_usd"])[:3]
            mensaje = (
                "El presupuesto ingresado es muy bajo, pero estas son las "
                "opciones mas economicas recomendadas para tu tipo de piel."
            )
    else:
        candidatos = sorted(candidatos_perfil, key=lambda x: x[1], reverse=True)

    # --- 3. Conversion de moneda y armado de respuesta ---
    resultados = []
    for producto, score in candidatos[:3]:
        precio_local, moneda_local = convertir_precio(producto["precio_usd"], perfil.pais)
        resultados.append(ProductoResponse(
            nombre=producto["nombre"],
            origen=producto["origen"],
            ingrediente_clave=producto["ingrediente_clave"],
            precio_local=precio_local,
            moneda_local=moneda_local,
            score_match=round(score, 2),
            link_compra=producto["link_compra"],
        ))

    return RecomendacionResponse(resultados=resultados, mensaje=mensaje)


# Ejemplos para /docs:
# 1) Presupuesto muy bajo pero perfil valido -> fallback con mensaje:
# {"tipo_piel":"grasa_mixta","preocupaciones":["acne"],"presupuesto_max_usd":1,"pais":"CL"}
#
# 2) Sin presupuesto, pais US:
# {"tipo_piel":"grasa_mixta","preocupaciones":["acne","rojeces"],"pais":"US"}
