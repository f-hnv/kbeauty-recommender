"""
Análisis estadístico y visualizaciones: K-Beauty vs Skincare Tradicional.
Pensado para correr en Google Colab o localmente (usa matplotlib + seaborn,
igual stack que tu dashboard anterior en Plotly Dash — aquí en versión
estática, fácil de exportar a PNG para un informe).
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

sns.set_theme(style="whitegrid", palette="Set2")

df = pd.read_csv("skincare_dataset_simulado.csv")

# -----------------------------------------------------------------------
# 1. PRUEBA ESTADÍSTICA: ¿la diferencia de satisfacción es significativa?
# -----------------------------------------------------------------------
grupo_kr = df[df["origen"] == "Coreano"]["satisfaccion_1_5"]
grupo_trad = df[df["origen"] == "Tradicional"]["satisfaccion_1_5"]
t_stat, p_value = stats.ttest_ind(grupo_kr, grupo_trad, equal_var=False)
print(f"T-test satisfacción -> t={t_stat:.3f}, p-value={p_value:.4f}")

# -----------------------------------------------------------------------
# 2. GRÁFICO 1 — Barras agrupadas: % mejora por afección y origen
#    Eje X: afección (acné, manchas, textura) | Eje Y: % mejora promedio
#    Por qué: comparación directa de magnitudes entre categorías, ideal
#    para 3 métricas paralelas.
# -----------------------------------------------------------------------
mejora_long = df.melt(
    id_vars="origen",
    value_vars=["mejora_acne_pct", "mejora_manchas_pct", "mejora_textura_pct"],
    var_name="afeccion", value_name="pct_mejora"
)
mejora_long["afeccion"] = mejora_long["afeccion"].map({
    "mejora_acne_pct": "Acné",
    "mejora_manchas_pct": "Manchas",
    "mejora_textura_pct": "Textura"
})

plt.figure(figsize=(8, 5))
sns.barplot(data=mejora_long, x="afeccion", y="pct_mejora", hue="origen", errorbar="sd")
plt.title("Mejora promedio por afección: Coreano vs Tradicional")
plt.xlabel("Afección tratada")
plt.ylabel("% de mejora reportada")
plt.tight_layout()
plt.savefig("01_barras_mejora_por_afeccion.png", dpi=150)
plt.close()

# -----------------------------------------------------------------------
# 3. GRÁFICO 2 — Boxplot: tolerancia en piel sensible por origen
#    Eje X: origen | Eje Y: % tolerancia
#    Por qué: el boxplot muestra mediana + dispersión + outliers, más
#    honesto que una sola barra de promedio cuando se argumenta
#    "tolerancia superior".
# -----------------------------------------------------------------------
plt.figure(figsize=(6, 5))
sns.boxplot(data=df, x="origen", y="tolerancia_piel_sensible_pct")
plt.title("Tolerancia en piel sensible por origen del producto")
plt.xlabel("Origen")
plt.ylabel("% de tolerancia reportada")
plt.tight_layout()
plt.savefig("02_boxplot_tolerancia_sensible.png", dpi=150)
plt.close()

# -----------------------------------------------------------------------
# 4. GRÁFICO 3 — Dispersión: precio vs satisfacción (relación calidad-precio)
#    Eje X: precio_usd | Eje Y: satisfaccion_1_5 | color: origen
#    Por qué: revela si pagar más realmente compra más satisfacción,
#    y si algún grupo domina en la esquina "alta satisfacción / bajo precio".
# -----------------------------------------------------------------------
plt.figure(figsize=(7, 5))
sns.scatterplot(
    data=df, x="precio_usd", y="satisfaccion_1_5", hue="origen",
    size="tamano_muestra_resenas", sizes=(20, 150), alpha=0.7
)
plt.title("Relación precio vs. satisfacción (tamaño = nº de reseñas)")
plt.xlabel("Precio (USD)")
plt.ylabel("Satisfacción (1-5)")
plt.tight_layout()
plt.savefig("03_dispersion_precio_satisfaccion.png", dpi=150)
plt.close()

# -----------------------------------------------------------------------
# 5. GRÁFICO 4 — Torta: participación de ingredientes clave dentro de K-Beauty
#    Por qué: la torta se justifica SOLO aquí porque es composición de un
#    todo (qué % de los productos coreanos usa cada ingrediente estrella).
#    Evitar torta para comparar Coreano vs Tradicional (ahí barras es mejor).
# -----------------------------------------------------------------------
conteo_ing = df[df["origen"] == "Coreano"]["ingrediente_clave"].value_counts()
plt.figure(figsize=(6, 6))
plt.pie(conteo_ing.values, labels=conteo_ing.index, autopct="%1.0f%%", startangle=90)
plt.title("Distribución de ingredientes clave en productos coreanos (muestra)")
plt.tight_layout()
plt.savefig("04_torta_ingredientes_kbeauty.png", dpi=150)
plt.close()

# -----------------------------------------------------------------------
# 6. GRÁFICO 5 — Radar/Heatmap resumen (índice comparativo global)
#    Eje X: métrica | Eje Y: origen | valor: color
#    Por qué: da una vista "de un vistazo" para la diapositiva final.
# -----------------------------------------------------------------------
resumen = df.groupby("origen")[[
    "satisfaccion_1_5", "mejora_acne_pct", "mejora_manchas_pct",
    "mejora_textura_pct", "tolerancia_piel_sensible_pct",
    "indice_calidad_precio_0_100"
]].mean().round(1)

plt.figure(figsize=(8, 3))
sns.heatmap(resumen, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={"label": "valor promedio"})
plt.title("Resumen comparativo de métricas clave")
plt.tight_layout()
plt.savefig("05_heatmap_resumen.png", dpi=150)
plt.close()

resumen.to_csv("tabla_resumen_comparativo.csv")
print("\nTabla resumen:\n", resumen)
print("\nGráficos guardados como PNG en el directorio actual.")
