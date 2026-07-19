-- =========================================================
-- Esquema de Base de Datos — App de Recomendación de Skincare
-- v2: incluye categoria_paso para armar RUTINAS completas
--     (Limpiador -> Tonico -> Serum -> Crema Hidratante)
-- Compatible con PostgreSQL
-- =========================================================

DROP TABLE IF EXISTS recomendaciones_generadas;
DROP TABLE IF EXISTS perfiles_usuario;
DROP TABLE IF EXISTS links_compra;
DROP TABLE IF EXISTS productos;

CREATE TABLE productos (
    producto_id         VARCHAR(20) PRIMARY KEY,
    nombre_producto     VARCHAR(150) NOT NULL,
    origen              VARCHAR(20) NOT NULL CHECK (origen IN ('Coreano', 'Tradicional')),

    -- NUEVO: a que paso de la rutina pertenece este producto
    categoria_paso       VARCHAR(20) NOT NULL CHECK (
        categoria_paso IN ('limpiador', 'tonico', 'serum', 'crema_hidratante')
    ),

    ingrediente_clave   VARCHAR(100) NOT NULL,
    ingredientes_full   TEXT,

    -- Filtros de recomendacion
    tipos_piel          VARCHAR(20)[] NOT NULL,
    preocupaciones      VARCHAR(30)[] NOT NULL,

    -- NUEVO: por que se recomienda este producto para ese tipo de piel
    razon_tipo_piel     TEXT NOT NULL,
    link_compra         TEXT NOT NULL,   -- link de compra directo (v1 simple; ver nota en main.py)

    -- Metricas del estudio (Fase 1)
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

CREATE TABLE links_compra (
    id              SERIAL PRIMARY KEY,
    producto_id     VARCHAR(20) REFERENCES productos(producto_id) ON DELETE CASCADE,
    pais_codigo     VARCHAR(2) NOT NULL,
    tienda          VARCHAR(80) NOT NULL,
    url              TEXT NOT NULL,
    moneda          VARCHAR(3) DEFAULT 'USD',
    precio_local    NUMERIC(10,2),
    disponible      BOOLEAN DEFAULT TRUE,
    UNIQUE (producto_id, pais_codigo, tienda)
);

CREATE TABLE perfiles_usuario (
    id                  SERIAL PRIMARY KEY,
    usuario_id          UUID,
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
    fue_clickeado   BOOLEAN DEFAULT FALSE,
    fue_comprado    BOOLEAN DEFAULT FALSE,
    generado_en     TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_productos_tipos_piel ON productos USING GIN (tipos_piel);
CREATE INDEX idx_productos_preocupaciones ON productos USING GIN (preocupaciones);
CREATE INDEX idx_productos_categoria_paso ON productos (categoria_paso);
CREATE INDEX idx_links_compra_pais ON links_compra (pais_codigo);

-- =========================================================
-- SEGURIDAD: Row Level Security (RLS)
-- =========================================================
-- Aplica solo a tablas con datos de USUARIOS (no al catalogo de
-- productos, que es publico por naturaleza). El objetivo: un usuario
-- solo puede ver/modificar sus propios perfiles y recomendaciones.
--
-- Como la app todavia no tiene login real, el "usuario" hoy es un
-- identificador anonimo (UUID) que el frontend genera y guarda en el
-- navegador. El backend lo recibe y lo fija como variable de sesion
-- de Postgres antes de cada consulta (ver database.py -> set_current_user()).
-- Cuando se agregue login real, ese UUID pasa a ser el id del usuario
-- autenticado, sin tener que tocar las policies.

ALTER TABLE perfiles_usuario ENABLE ROW LEVEL SECURITY;
ALTER TABLE recomendaciones_generadas ENABLE ROW LEVEL SECURITY;

-- IMPORTANTE: RLS NO aplica a roles superusuario ni a quien sea
-- propietario de la tabla. Por eso la app debe conectarse con un rol
-- de aplicacion (app_user), nunca con el superusuario 'postgres'.
DROP ROLE IF EXISTS app_user;
CREATE ROLE app_user LOGIN PASSWORD :'app_user_password';

GRANT SELECT ON productos TO app_user;
GRANT SELECT ON links_compra TO app_user;
GRANT SELECT, INSERT, UPDATE ON perfiles_usuario TO app_user;
GRANT SELECT, INSERT, UPDATE ON recomendaciones_generadas TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Policy: un usuario solo ve/edita perfiles cuyo usuario_id coincide
-- con el que el backend fijo en la sesion actual.
CREATE POLICY perfiles_propios ON perfiles_usuario
    USING (usuario_id = current_setting('app.current_user_id', true)::uuid)
    WITH CHECK (usuario_id = current_setting('app.current_user_id', true)::uuid);

-- Policy: idem para recomendaciones, via el perfil al que pertenecen.
CREATE POLICY recomendaciones_propias ON recomendaciones_generadas
    USING (
        perfil_id IN (
            SELECT id FROM perfiles_usuario
            WHERE usuario_id = current_setting('app.current_user_id', true)::uuid
        )
    )
    WITH CHECK (
        perfil_id IN (
            SELECT id FROM perfiles_usuario
            WHERE usuario_id = current_setting('app.current_user_id', true)::uuid
        )
    );
