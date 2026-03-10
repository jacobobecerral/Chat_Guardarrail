# Chat Seguro: Local e Hibrido

Interfaz de chat profesional construida con Streamlit para interactuar con modelos de Ollama de forma segura. El sistema permite conexiones locales y remotas, integrando multiples capas de proteccion de datos.

## Requisitos Previos

1. Ollama: Instalado y en ejecucion.
2. uv: Gestor de paquetes avanzado para Python.

```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Instalacion y Configuracion

### 1. Inicializar Dependencias
El proyecto utiliza uv para la gestion de dependencias y el entorno virtual.

```bash
uv init
uv add streamlit ollama python-dotenv
```

### 2. Variables de Entorno
Cree un archivo .env en la raiz del proyecto para configurar el acceso al servidor remoto:

```env
PROFESSOR_HOST=10.10.99.77
```

## Funciones de Seguridad y Privacidad

El sistema implementa una arquitectura de seguridad por capas para proteger la informacion sensible:

1. Filtro PII mediante Regex:
   - Deteccion de correos electronicos.
   - Validacion de tarjetas de credito.
   - Validacion de IBAN (Espana).
   - Identificacion de DNI y NIE.
   - Seguridad Social (NSS).

2. Anonimizacion de Nombres con LLM:
   - Utiliza el modelo gemma3:270m para identificar nombres de personas privadas.
   - Sustitucion dinamica por nombres ficticios para proteger la identidad.
   - De-anonimizacion automatica en la respuesta para mantener la coherencia.
   - Exclusion inteligente de figuras publicas y celebridades.

3. Llama Guard 3:
   - Verificacion de seguridad del contenido mediante el modelo llama-guard3.
   - Clasificacion de riesgos en multiples categorias (odio, violencia, privacidad, etc.).
   - Bloqueo preventivo de contenido peligroso.

## Caracteristicas Adicionales

- Conexion Hibrida: Selector de servidor entre maquina local y servidor remoto.
- Interfaz Profesional: Diseno limpio con Streamlit, soporte para historial de chat y limpieza de mensajes.
- Deteccion Dinamica: La lista de modelos se sincroniza automaticamente con el servidor seleccionado.

## Ejecucion

Inicie la aplicacion con el siguiente comando:

```bash
uv run streamlit run app.py
```

Optimizado para entornos educativos y desarrollo seguro de Inteligencia Artificial.
