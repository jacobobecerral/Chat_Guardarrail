import os
import streamlit as st
from dotenv import load_dotenv
from ollama import Client

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

    # Detección dinámica de modelos
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
        st.warning(f"⚠️ No se pudo obtener la lista de modelos de {server_option}. Usando lista por defecto.")
        # Logging del error en consola para depuración
        print(f"Error listando modelos: {e}")

    # Lista por defecto si falla la detección o no hay modelos
    if not available_models:
        available_models = ["gemma3:latest", "llama3", "mistral"]

    selected_model = st.selectbox(
        "🧠 Selecciona un modelo:",
        available_models,
        index=0
    )
    # Líneas eliminadas por limpieza y unificación de lógica de error


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
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capturar entrada
# Capturar entrada
from pii_manager import PIIFilter

# Instanciar filtro (fuera del loop para eficiencia, idealmente al inicio, pero aquí funciona)
pii_filter = PIIFilter()

if prompt := st.chat_input("Escribe tu mensaje..."):
    # 1. Filtrar mensaje (Seguridad: Lo que llega al LLM y al historial debe estar limpio)
    try:
        clean_prompt = pii_filter.anonymize(prompt)
    except Exception as e:
        st.error(f"Error al procesar el texto: {e}")
        clean_prompt = prompt # Fallback seguro o bloquear? Mejor fallback para no romper UX, advirtiendo.

    # Guardar y mostrar mensaje usuario (Ya filtrado)
    st.session_state.messages.append({"role": "user", "content": clean_prompt})
    with st.chat_message("user"):
        st.markdown(clean_prompt) # Muestra [DNI] etc. al usuario, confirmando seguridad.

    # Generar respuesta
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Streaming usando el cliente configurado
            stream = client.chat(
                model=selected_model,
                messages=st.session_state.messages,
                stream=True
            )
            
            for chunk in stream:
                content = chunk['message']['content']
                full_response += content
                response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"❌ Error durante la generación: {str(e)}")
