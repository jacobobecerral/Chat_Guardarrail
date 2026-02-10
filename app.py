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
        # Ajuste: algunos clientes devuelven lista directa o dict con 'models'
        if isinstance(models_info, dict) and 'models' in models_info:
            available_models = [m['model'] for m in models_info['models']]
        else:
             # Fallback si la estructura es diferente
            available_models = [m['model'] for m in models_info]
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
pii_filter = PIIFilter()

# Capturar entrada
if prompt := st.chat_input("Escribe tu mensaje..."):
    # 1. PII Filtering
    try:
        clean_prompt = pii_filter.anonymize(prompt)
    except Exception as e:
        st.error(f"Error al procesar PII: {e}")
        clean_prompt = prompt

    # 2. Llama Guard Check (Si está activo)
    is_safe = True
    violation_msg = ""
    
    if enable_guard:
        # Validamos el prompt limpio (safe_content)
        with st.spinner("Analizando seguridad..."):
            is_safe, violation_msg = LlamaGuard.check_safety(client, clean_prompt)
    
    if not is_safe:
        st.error(f"⛔ Este mensaje no se puede responder por: **{violation_msg}**")
        st.warning("Por favor, reformula tu pregunta de manera segura.")
        # No añadimos al historial, permitimos reintento inmediato
    else:
        # Si es seguro, procedemos
        
        # 3. Guardar en Session State
        # Guardamos AMBOS: original para mostrar, y clean para enviar
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,        # Visualización
            "safe_content": clean_prompt # Lógica
        })
        
        # Mostrar mensaje usuario inmediatamente
        with st.chat_message("user"):
            st.markdown(prompt)

        # 4. Generar respuesta
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                # Construir payload para el modelo
                # Usamos safe_content si existe, sino content
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
                
                for chunk in stream:
                    content = chunk['message']['content']
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
                
                # Guardar respuesta
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"❌ Error durante la generación: {str(e)}")
