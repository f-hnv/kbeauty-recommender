-- =========================================================
-- Esquema de Base de Datos — App de Recomendación de Skincare
-- Compatible con PostgreSQL (recomendado por soporte nativo de
-- arrays y JSONB, muy útiles aquí)
-- =========================================================

CREATE TABLE productos (
    producto_id         VARCHAR(20) PRIMARY KEY,
    nombre_producto     VARCHAR(150) NOT NULL,
    origen              VARCHAR(20) NOT NULL CHECK (origen IN ('Coreano', 'Tradicional')),
    categoria           VARCHAR(50) NOT NULL,            -- ej. 'serum', 'tonico', 'crema'
    ingrediente_clave   VARCHAR(100) NOT NULL,
    ingredientes_full   TEXT,                            -- lista INCI completa (opcional)

    -- Filtros de recomendación
    tipos_piel          VARCHAR(20)[] NOT NULL,          -- ej. {'grasa','mixta'}
    preocupaciones      VARCHAR(30)[] NOT NULL,          -- ej. {'acne','rojeces'}

    -- Métricas del estudio (Fase 1) — permiten justificar el ranking
    satisfaccion_promedio       NUMERIC(3,2),
    mejora_acne_pct             NUMERIC(5,2),
    mejora_manchas_pct          NUMERIC(5,2),
    mejora_textura_pct          NUMERIC(5,2),
    tolerancia_piel_sensible_pct NUMERIC(5,2),

    precio_usd          NUMERIC(8,2) NOT NULL,
    activo              BOOLEAN DEFAULT TRUE,
    creado_en           TIMESTAMP DEFAULT NOW(),
    actualizado_en       TIMESTAMP DEFAULT NOW()
);

-- Links de compra regionalizados: 1 producto -> N países/tiendas
CREATE TABLE links_compra (
    id              SERIAL PRIMARY KEY,
    producto_id     VARCHAR(20) REFERENCES productos(producto_id) ON DELETE CASCADE,
    pais_codigo     VARCHAR(2) NOT NULL,        -- ISO 3166-1 alpha-2, ej. 'CL', 'MX', 'US'
    tienda          VARCHAR(80) NOT NULL,       -- ej. 'Sephora', 'YesStyle', 'Falabella'
    url              TEXT NOT NULL,
    moneda          VARCHAR(3) DEFAULT 'USD',
    precio_local    NUMERIC(10,2),
    disponible      BOOLEAN DEFAULT TRUE,
    UNIQUE (producto_id, pais_codigo, tienda)
);

-- Historial de perfiles/recomendaciones (para reentrenar el modelo luego)
CREATE TABLE perfiles_usuario (
    id                  SERIAL PRIMARY KEY,
    usuario_id          UUID,                    -- si hay login
    tipo_piel           VARCHAR(20) NOT NULL,
    preocupaciones      VARCHAR(30)[] NOT NULL,
    presupuesto_max_usd NUMERIC(8,2),
    pais_codigo         VARCHAR(2),
    creado_en           TIMESTAMP DEFAULT NOW()
);

CREATE TABLE recomendaciones_generadas (
    id              SERIAL PRIMARY KEY,
    perfil_id       INTEGER REFERENCES perfiles_usuario(id),
    producto_id     VARCHAR(20) REFERENCES productos(producto_id),
    score_match     NUMERIC(5,2),
    fue_clickeado   BOOLEAN DEFAULT FALSE,   -- señal de feedback implícito
    fue_comprado    BOOLEAN DEFAULT FALSE,   -- señal fuerte para futuro modelo de ML
    generado_en     TIMESTAMP DEFAULT NOW()
);

-- Índices para acelerar el filtrado del recomendador
CREATE INDEX idx_productos_tipos_piel ON productos USING GIN (tipos_piel);
CREATE INDEX idx_productos_preocupaciones ON productos USING GIN (preocupaciones);
CREATE INDEX idx_links_compra_pais ON links_compra (pais_codigo);
