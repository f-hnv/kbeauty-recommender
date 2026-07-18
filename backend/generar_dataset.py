"""
Generador de dataset SIMULADO (sintético) para el estudio comparativo
K-Beauty vs Skincare Tradicional.

IMPORTANTE: Estos NO son datos de un estudio real publicado. Son datos
sintéticos construidos con distribuciones estadísticas razonables,
inspiradas en tendencias generales reportadas de forma recurrente en
encuestas de consumidoras (ej. mayor tolerancia percibida y foco en
hidratación/barrera cutánea en K-Beauty; mayor variabilidad de precio
y foco en activos "tratamiento" en marcas occidentales). Sirven como
placeholder para practicar el pipeline de análisis; si el proyecto es
académico formal, se recomienda sustituir esta data por una encuesta
propia o por datos de estudios dermatológicos citables.
"""

import numpy as np
import pandas as pd

np.random.seed(42)  # reproducibilidad

N_POR_GRUPO = 150  # tamaño de muestra simulado por origen

# --- Catálogo de productos base (ejemplo ilustrativo, no exhaustivo) ---
productos_kbeauty = [
    ("COSRX Advanced Snail 96 Mucin Power Essence", "esencia", "mucina de caracol"),
    ("Beauty of Joseon Glow Serum", "serum", "propóleo + niacinamida"),
    ("Skin1004 Madagascar Centella Ampoule", "ampolla", "centella asiática"),
    ("Laneige Water Sleeping Mask", "mascarilla nocturna", "hialuronato + polisacáridos"),
    ("Some By Mi AHA-BHA-PHA 30 Days Miracle Toner", "tónico", "complejo AHA/BHA/PHA"),
    ("Innisfree Green Tea Seed Serum", "serum", "extracto de té verde"),
    ("Etude House SoonJung Calming Serum", "serum", "panthenol + centella"),
    ("Klairs Freshly Juiced Vitamin Drop", "serum", "vitamina C estabilizada"),
]

productos_tradicionales = [
    ("CeraVe Moisturizing Cream", "crema hidratante", "ceramidas"),
    ("The Ordinary Niacinamide 10% + Zinc 1%", "serum", "niacinamida + zinc"),
    ("Neutrogena Rapid Wrinkle Repair", "crema tratamiento", "retinol"),
    ("La Roche-Posay Effaclar Duo", "gel tratamiento", "ácido salicílico + niacinamida"),
    ("Olay Regenerist Micro-Sculpting Cream", "crema", "péptidos + niacinamida"),
    ("Clinique Dramatically Different Moisturizing Lotion", "loción", "glicerina"),
    ("Kiehl's Ultra Facial Cream", "crema hidratante", "escualano + glicerina"),
    ("Paula's Choice BHA Liquid Exfoliant", "exfoliante", "ácido salicílico"),
]

filas = []

def generar_bloque(catalogo, origen, n):
    for i in range(n):
        nombre, categoria, ingrediente = catalogo[i % len(catalogo)]

        if origen == "Coreano":
            satisfaccion = np.clip(np.random.normal(4.3, 0.5), 1, 5)
            mejora_acne = np.clip(np.random.normal(38, 12), 0, 100)
            mejora_manchas = np.clip(np.random.normal(30, 10), 0, 100)
            mejora_textura = np.clip(np.random.normal(52, 10), 0, 100)
            tolerancia_sensible = np.clip(np.random.normal(82, 10), 0, 100)
            precio_usd = np.clip(np.random.normal(18, 7), 4, 60)
        else:  # Tradicional
            satisfaccion = np.clip(np.random.normal(3.9, 0.6), 1, 5)
            mejora_acne = np.clip(np.random.normal(41, 14), 0, 100)
            mejora_manchas = np.clip(np.random.normal(33, 12), 0, 100)
            mejora_textura = np.clip(np.random.normal(44, 12), 0, 100)
            tolerancia_sensible = np.clip(np.random.normal(66, 14), 0, 100)
            precio_usd = np.clip(np.random.normal(24, 10), 5, 90)

        calidad_precio = np.clip(
            (satisfaccion / 5) * 100 - (precio_usd / 2) + np.random.normal(0, 8),
            0, 100
        )

        filas.append({
            "producto_id": f"{origen[:3].upper()}-{i+1:03d}",
            "nombre_producto": nombre,
            "origen": origen,
            "categoria": categoria,
            "ingrediente_clave": ingrediente,
            "precio_usd": round(precio_usd, 2),
            "satisfaccion_1_5": round(satisfaccion, 2),
            "mejora_acne_pct": round(mejora_acne, 1),
            "mejora_manchas_pct": round(mejora_manchas, 1),
            "mejora_textura_pct": round(mejora_textura, 1),
            "tolerancia_piel_sensible_pct": round(tolerancia_sensible, 1),
            "indice_calidad_precio_0_100": round(calidad_precio, 1),
            "tamano_muestra_resenas": int(np.random.randint(80, 2500)),
        })

generar_bloque(productos_kbeauty, "Coreano", N_POR_GRUPO)
generar_bloque(productos_tradicionales, "Tradicional", N_POR_GRUPO)

df = pd.DataFrame(filas)
df.to_csv("skincare_dataset_simulado.csv", index=False, encoding="utf-8")

print("Dataset generado:", df.shape)
print(df.groupby("origen")[
    ["satisfaccion_1_5", "mejora_acne_pct", "mejora_manchas_pct",
     "mejora_textura_pct", "tolerancia_piel_sensible_pct",
     "indice_calidad_precio_0_100", "precio_usd"]
].mean().round(2))
