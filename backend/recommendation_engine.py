from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TipoPiel(str, Enum):
    GRASA = "grasa"
    SECA = "seca"
    MIXTA = "mixta"
    SENSIBLE = "sensible"
    NORMAL = "normal"


class Preocupacion(str, Enum):
    ACNE = "acne"
    MANCHAS = "manchas"
    ARRUGAS = "arrugas"
    DESHIDRATACION = "deshidratacion"
    ROJECES = "rojeces"
    TEXTURA_IRREGULAR = "textura_irregular"


@dataclass
class PerfilUsuario:
    tipo_piel: TipoPiel
    preocupaciones: list  # lista de Preocupacion
    presupuesto_max_usd: Optional[float] = None
    pais: str = "CL"  # para regionalizar links de compra
    prefiere_origen: Optional[str] = None  # "Coreano" | "Tradicional" | None


@dataclass
class Producto:
    producto_id: str
    nombre: str
    origen: str
    categoria: str
    ingrediente_clave: str
    tipos_piel_recomendados: list
    preocupaciones_que_trata: list
    precio_usd: float
    links_compra: dict = field(default_factory=dict) 


# --- Catálogo mínimo de ejemplo (en producción esto viene de la BD) ---
CATALOGO_EJEMPLO = [
    Producto(
        producto_id="COR-003",
        nombre="Skin1004 Madagascar Centella Ampoule",
        origen="Coreano",
        categoria="ampolla",
        ingrediente_clave="centella asiatica",
        tipos_piel_recomendados=[TipoPiel.GRASA, TipoPiel.MIXTA, TipoPiel.SENSIBLE],
        preocupaciones_que_trata=[Preocupacion.ACNE, Preocupacion.ROJECES],
        precio_usd=17.0,
        links_compra={"CL": "https://tienda-ejemplo.cl/producto/centella-ampoule",
                      "MX": "https://tienda-ejemplo.mx/producto/centella-ampoule"},
    ),
    Producto(
        producto_id="COR-005",
        nombre="Some By Mi AHA-BHA-PHA Toner",
        origen="Coreano",
        categoria="tonico",
        ingrediente_clave="AHA/BHA/PHA",
        tipos_piel_recomendados=[TipoPiel.GRASA, TipoPiel.MIXTA],
        preocupaciones_que_trata=[Preocupacion.ACNE, Preocupacion.TEXTURA_IRREGULAR],
        precio_usd=22.0,
        links_compra={"CL": "https://tienda-ejemplo.cl/producto/aha-bha-toner"},
    ),
    Producto(
        producto_id="TRA-002",
        nombre="The Ordinary Niacinamide 10% + Zinc 1%",
        origen="Tradicional",
        categoria="serum",
        ingrediente_clave="niacinamida",
        tipos_piel_recomendados=[TipoPiel.GRASA, TipoPiel.MIXTA],
        preocupaciones_que_trata=[Preocupacion.ACNE, Preocupacion.MANCHAS],
        precio_usd=9.0,
        links_compra={"CL": "https://tienda-ejemplo.cl/producto/niacinamide-ordinary"},
    ),
    Producto(
        producto_id="TRA-001",
        nombre="CeraVe Moisturizing Cream",
        origen="Tradicional",
        categoria="crema hidratante",
        ingrediente_clave="ceramidas",
        tipos_piel_recomendados=[TipoPiel.SECA, TipoPiel.SENSIBLE, TipoPiel.NORMAL],
        preocupaciones_que_trata=[Preocupacion.DESHIDRATACION, Preocupacion.ROJECES],
        precio_usd=16.0,
        links_compra={"CL": "https://tienda-ejemplo.cl/producto/cerave-crema"},
    ),
]


def _score_producto(producto: Producto, perfil: PerfilUsuario) -> float:
    """
    Scoring ponderado y transparente. Cada regla suma puntos;
    esta función es el punto de extensión para reemplazar por un
    modelo de ML entrenado (ver docstring del módulo).
    """
    score = 0.0

    # Match de tipo de piel (peso alto: es el filtro más restrictivo)
    if perfil.tipo_piel in producto.tipos_piel_recomendados:
        score += 5.0

    # Match de preocupaciones (suma por cada coincidencia)
    coincidencias = set(perfil.preocupaciones) & set(producto.preocupaciones_que_trata)
    score += 3.0 * len(coincidencias)

    # Preferencia de origen (si el usuario la indicó)
    if perfil.prefiere_origen and producto.origen == perfil.prefiere_origen:
        score += 1.5

    # Filtro de presupuesto (penalización fuerte si excede, no descarte duro
    # para no dejar el catálogo vacío en perfiles muy acotados)
    if perfil.presupuesto_max_usd is not None:
        if producto.precio_usd > perfil.presupuesto_max_usd:
            score -= 4.0

    return score


def recomendar(perfil: PerfilUsuario, catalogo: list = None, top_n: int = 3) -> list:
    catalogo = catalogo if catalogo is not None else CATALOGO_EJEMPLO

    candidatos = [(p, _score_producto(p, perfil)) for p in catalogo]
    candidatos = [c for c in candidatos if c[1] > 0]  # descarta sin ningún match
    candidatos.sort(key=lambda x: x[1], reverse=True)

    resultados = []
    for producto, score in candidatos[:top_n]:
        resultados.append({
            "producto_id": producto.producto_id,
            "nombre": producto.nombre,
            "origen": producto.origen,
            "ingrediente_clave": producto.ingrediente_clave,
            "precio_usd": producto.precio_usd,
            "score_match": round(score, 2),
            "link_compra": producto.links_compra.get(
                perfil.pais, producto.links_compra.get("CL")
            ),
        })
    return resultados


if __name__ == "__main__":
    # Ejemplo: "piel grasa/mixta con tendencia acneica" (el caso del enunciado)
    perfil_demo = PerfilUsuario(
        tipo_piel=TipoPiel.MIXTA,
        preocupaciones=[Preocupacion.ACNE, Preocupacion.ROJECES],
        presupuesto_max_usd=25.0,
        pais="CL",
    )

    recomendaciones = recomendar(perfil_demo)
    for r in recomendaciones:
        print(r)
