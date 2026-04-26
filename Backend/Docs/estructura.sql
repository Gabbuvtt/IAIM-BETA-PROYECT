-- 1 crear la tabla principal (Usuarios)

CREATE TABLE usuarios(
    id UUID PRIMARY KEY DEFAULT gen_randomuuid(), --Crea un id unico generado automaticamente
    nombre_completo TEXT NOT NULL, --ESTE TEXTO NO PUEDE ESTAR VACIO
    carnet TEXT UNIQUE NOT NULL, --IDENTIFICACION QUE ES IRREPETIBLE CON UNIQUE
    email TEXT UNIQUE NOT NULL, --CORREO IRREPETIBLE
    password_hash TEXT NOT NULL, --CODIGO DE SEGURIDAD PROTEGIDO
    rol TEXT DEFATUL 'tecnico', --POR DEFECTO ERES TECNICO SI NO RESPONDES NADA
    fecha_creacion TIMESTAMPTZ DEFAULT now()--DEFINE QUE LA FEHCA DE CREACION ES AUTOMATICA SEGUN EL VALOR DEL RELOJ DE LA PROPIA BASE DE DATOS
);

CREATE TABLE tickets(
    id SERIAL PRIMARY KEY,
    asunto TEXT NOT NULL,
    descripcion TEXT,
    prioridad TEXT DEFAULT 'media',
    estado  TEXT DEFAULT 'abierto',

----creamos el link de el ticket a usuarios
    usuario_id UUID REFERENCES usuarios(id),
    fecha_reporte TIMESTAMPTZ DEFAULT now()
);