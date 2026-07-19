-- =========================================================
-- Datos de PRUEBA (simulados) para la tabla productos
-- Cobertura garantizada: cada categoria_paso tiene al menos un
-- producto para cada tipo de piel (grasa, mixta, grasa_mixta,
-- seca, sensible, normal).
-- =========================================================

-- ---------- LIMPIADOR ----------
INSERT INTO productos (
    producto_id, nombre_producto, origen, categoria_paso, ingrediente_clave,
    tipos_piel, preocupaciones, razon_tipo_piel, link_compra, precio_usd
) VALUES
('LIM-001', 'COSRX Low pH Good Morning Gel Cleanser', 'Coreano', 'limpiador',
 'acido tea-cocoyl glutamato',
 ARRAY['grasa','mixta','grasa_mixta','normal'], ARRAY['acne','textura_irregular'],
 'Gel de limpieza con pH balanceado (~5.5) que remueve el exceso de sebo sin resecar ni alterar la barrera cutanea, ideal para piel grasa o mixta propensa a brotes.',
 'https://www.cosrx.com/',
 11.0),

('LIM-002', 'Purito Deep Sea Water Cleansing Foam', 'Coreano', 'limpiador',
 'agua marina profunda + centella asiatica',
 ARRAY['seca','sensible','normal'], ARRAY['deshidratacion','rojeces'],
 'Espuma suave enriquecida con minerales marinos que limpia sin dejar sensacion de tirantez, apta para piel seca o sensible que se irrita facil.',
 'https://www.purito.com/',
 15.0),

('LIM-003', 'CeraVe Hydrating Facial Cleanser', 'Tradicional', 'limpiador',
 'ceramidas + acido hialuronico',
 ARRAY['seca','sensible','normal'], ARRAY['deshidratacion'],
 'Formula sin sulfatos con ceramidas que limpia respetando la barrera lipidica, recomendada para piel seca o sensible en tratamiento.',
 'https://www.cerave.com/',
 12.0);

-- ---------- TONICO ----------
INSERT INTO productos (
    producto_id, nombre_producto, origen, categoria_paso, ingrediente_clave,
    tipos_piel, preocupaciones, razon_tipo_piel, link_compra, precio_usd
) VALUES
('TON-001', 'Some By Mi AHA-BHA-PHA 30 Days Miracle Toner', 'Coreano', 'tonico',
 'complejo AHA/BHA/PHA',
 ARRAY['grasa','mixta','grasa_mixta'], ARRAY['acne','textura_irregular'],
 'Combina 3 tipos de exfoliantes quimicos que ayudan a destapar poros y controlar la produccion de sebo en piel grasa o mixta.',
 'https://somebymi.com/',
 22.0),

('TON-002', 'Klairs Supple Preparation Toner', 'Coreano', 'tonico',
 'extracto de centella + aminoacidos',
 ARRAY['seca','sensible','normal'], ARRAY['deshidratacion','rojeces'],
 'Tonico hidratante y calmante, sin alcohol ni fragancia agresiva, formulado para preparar piel seca o sensible antes del serum.',
 'https://klairscosmetics.com/',
 19.0);

-- ---------- SERUM ----------
INSERT INTO productos (
    producto_id, nombre_producto, origen, categoria_paso, ingrediente_clave,
    tipos_piel, preocupaciones, razon_tipo_piel, link_compra, precio_usd
) VALUES
('SER-001', 'Skin1004 Madagascar Centella Ampoule', 'Coreano', 'serum',
 'centella asiatica (extracto 100%)',
 ARRAY['grasa','mixta','grasa_mixta','sensible'], ARRAY['acne','rojeces'],
 'Alta concentracion de centella asiatica que calma la inflamacion asociada al acne sin obstruir los poros, apta tambien para piel sensible reactiva.',
 'https://skin1004.com/',
 17.0),

('SER-002', 'Beauty of Joseon Glow Serum', 'Coreano', 'serum',
 'propoleo + niacinamida',
 ARRAY['normal','mixta','seca'], ARRAY['manchas','textura_irregular'],
 'La niacinamida ayuda a unificar el tono y el propoleo aporta un efecto calmante, con una textura ligera que hidrata sin sensacion grasa.',
 'https://beautyofjoseon.com/',
 16.0),

('SER-003', 'The Ordinary Niacinamide 10% + Zinc 1%', 'Tradicional', 'serum',
 'niacinamida + zinc',
 ARRAY['grasa','mixta','grasa_mixta'], ARRAY['acne','manchas'],
 'El zinc ayuda a regular la produccion de sebo y la niacinamida reduce la apariencia de poros, ideal como tratamiento dirigido en piel grasa o mixta.',
 'https://theordinary.com/',
 9.0);

-- ---------- CREMA HIDRATANTE ----------
INSERT INTO productos (
    producto_id, nombre_producto, origen, categoria_paso, ingrediente_clave,
    tipos_piel, preocupaciones, razon_tipo_piel, link_compra, precio_usd
) VALUES
('CRE-001', 'CeraVe Moisturizing Cream', 'Tradicional', 'crema_hidratante',
 'ceramidas + glicerina',
 ARRAY['seca','sensible','normal'], ARRAY['deshidratacion','rojeces'],
 'Formula rica en ceramidas que repara la barrera cutanea y retiene humedad por mas tiempo, adecuada para piel seca o sensible con tendencia a la irritacion.',
 'https://www.cerave.com/',
 16.0),

('CRE-002', 'COSRX Oil-Free Ultra-Moisturizing Lotion', 'Coreano', 'crema_hidratante',
 'birch sap (savia de abedul)',
 ARRAY['grasa','mixta','grasa_mixta','normal'], ARRAY['acne','textura_irregular'],
 'Locion ligera y libre de aceite que hidrata sin dejar sensacion pesada ni obstruir poros, pensada especificamente para piel grasa o mixta.',
 'https://www.cosrx.com/',
 15.5);
