import os
import streamlit as st
from dotenv import load_dotenv
from ollama import Client
from pii_manager import PIIFilter
from llama_guard import LlamaGuard

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="Ollama Chat Híbrido",
    page_icon="🛡️",
    layout="centered"
)

# Título y descripción
st.title("🛡️ Chat Seguro: Local & Remoto")
st.caption("Conéctate a tu LLM local o al servidor del profesor de forma segura.")

# --- Configuración Sidebar ---

with st.sidebar:
    st.header("🔌 Configuración de Conexión")
    
    # Selector de Servidor
    server_option = st.radio(
        "Selecciona el Servidor:",
        ("Mi Máquina (Local)", "Máquina Profesor (Remoto)"),
        index=0
    )
    
    # Definir host basado en la selección
    if server_option == "Mi Máquina (Local)":
        ollama_host = "http://127.0.0.1:11434"
    else:
        ollama_host = os.getenv("PROFESSOR_HOST")
        if not ollama_host:
            st.error("⚠️ No se encontró la IP del profesor en el archivo .env")
            st.stop()

    # Instanciar cliente con el host seleccionado
    client = Client(host=ollama_host)
    
    st.success(f"Conectado a: **{server_option}**")
    st.markdown("---")

    # Detección dinámica de modelos con Fallback
    available_models = []
    try:
        models_info = client.list()
        
        # Normalizar la lista de modelos
        # Caso 1: Objeto ListResponse con atributo 'models'
        if hasattr(models_info, 'models'):
            raw_models = models_info.models
        # Caso 2: Diccionario con clave 'models'
        elif isinstance(models_info, dict) and 'models' in models_info:
            raw_models = models_info['models']
        # Caso 3: Es la lista directa
        else:
            raw_models = models_info

        # Extraer nombres
        for m in raw_models:
            # Si es objeto con atributo model
            if hasattr(m, 'model'):
                available_models.append(m.model)
            # Si es diccionario
            elif isinstance(m, dict):
                available_models.append(m['model'])
            # Si es string (raro, pero posible en versiones viejas mockeadas)
            elif isinstance(m, str):
                available_models.append(m)
                
    except Exception as e:
        # Silenciar warning intrusivo
        print(f"Warning: No se pudieron listar modelos de {server_option}: {e}")

    # Lista por defecto si falla la detección o no hay modelos
    # Aseguramos que gemma3:latest esté
    if not available_models:
        available_models = ["gemma3:latest", "llama3", "mistral"]

    selected_model = st.selectbox(
        "🧠 Selecciona un modelo:",
        available_models,
        index=0
    )
    
    st.markdown("---")
    
    # Toggle Llama Guard
    enable_guard = st.toggle("🛡️ Activar Llama Guard", value=True)
    if enable_guard:
        st.info("Filtro de seguridad activo (llama-guard3)")

    st.markdown("---")
    
    # Botón para limpiar historial
    if st.button("🧹 Limpiar Historial", type="primary"):
        st.session_state.messages = []
        st.rerun()

# --- Lógica del Chat ---

# Inicializar historial
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes
# UX Improvement: Mostrar 'content' (lo que escribió el usuario)
# El 'safe_content' se usa internamente para el modelo
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Instanciar filtro PII
# Instanciar filtros
from name_filter import NameFilter

if "name_filter" not in st.session_state:
    st.session_state.name_filter = NameFilter()

pii_filter = PIIFilter()

# Capturar entrada
if prompt := st.chat_input("Escribe tu mensaje..."):
    # 1. PII Regex (DNI, Email, Tarjetas...)
    try:
        regex_clean_prompt = pii_filter.anonymize(prompt)
    except Exception as e:
        st.error(f"Error al procesar Regex PII: {e}")
        regex_clean_prompt = prompt

    # 2. Filtrado de Nombres (Gemma3:270m)
    try:
        # Usamos el cliente para llamar a gemma3:270m
        full_clean_prompt = st.session_state.name_filter.anonymize(client, regex_clean_prompt)
    except Exception as e:
        print(f"Error en filtro de nombres: {e}")
        full_clean_prompt = regex_clean_prompt

    # 3. Llama Guard Check
    is_safe = True
    violation_msg = ""
    
    if enable_guard:
        with st.spinner("Analizando seguridad..."):
            is_safe, violation_msg = LlamaGuard.check_safety(client, full_clean_prompt)
    
    if not is_safe:
        st.error(f"⛔ Este mensaje no se puede responder por: **{violation_msg}**")
        st.warning("Por favor, reformula tu pregunta de manera segura.")
    else:
        # 4. Guardar en Session State e Imprimir
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,            # Visualización (Original)
            "safe_content": full_clean_prompt # Para el modelo (Ficticios + [DNI])
        })
        
        with st.chat_message("user"):
            st.markdown(prompt)

        # 5. Generar respuesta
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response_safe = "" 
            
            try:
                # Construir payload seguro
                messages_payload = [
                    {
                        "role": m["role"], 
                        "content": m.get("safe_content", m["content"])
                    } for m in st.session_state.messages
                ]

                stream = client.chat(
                    model=selected_model,
                    messages=messages_payload,
                    stream=True
                )
                
                # Streaming (Muestra lo que genera el modelo -> Nombres Ficticios)
                for chunk in stream:
                    content = chunk['message']['content']
                    full_response_safe += content
                    response_placeholder.markdown(full_response_safe + "▌")
                
                # Des-anonimizar
                final_response_real = st.session_state.name_filter.deanonymize(full_response_safe)
                
                # Actualizar el placeholder con la versión real
                response_placeholder.markdown(final_response_real)
                
                # Guardar respuesta
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": final_response_real,      # Real (Juan)
                    "safe_content": full_response_safe   # Ficticio (Hugo)
                })
                
            except Exception as e:
                st.error(f"❌ Error durante la generación: {str(e)}")
