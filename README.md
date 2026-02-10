# 🦙 Ollama Chat: Local & Híbrido

Interfaz de chat profesional construida con **Streamlit** para interactuar con modelos de **Ollama**. Soporta conexión **Local** y **Remota** (Profesor).

## 🚀 Requisitos Previos

1.  **Ollama**: Instalado localmente.
2.  **uv**: Gestor de paquetes.
    ```bash
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

## 🛠️ Instalación y Configuración

### 1. Inicializar y Configurar Dependencias
El proyecto usa `uv` para gestionar todo.

```bash
uv init
uv add streamlit ollama python-dotenv
```

### 2. Configuración de Seguridad (.env)
Crea un archivo `.env` en la raíz del proyecto (ya incluido en la configuración inicial):

```env
PROFESSOR_HOST=10.10.99.77
```
*Este archivo es ignorado por git para seguridad.*

## ▶️ Ejecución

Inicia la aplicación:

```bash
uv run streamlit run app.py
```

## ✨ Características Nuevas

*   **🔌 Conexión Híbrida**: Selecciona en la barra lateral entre tu máquina local y el servidor del profesor.
*   **🛡️ Seguridad**: Variables de entorno gestionadas con `.env`.
*   **🎨 UI Mejorada**: Tema oscuro configurado por defecto y elementos innecesarios ocultos.
*   **🧠 Dinámico**: La lista de modelos se actualiza según el servidor al que te conectes.

---
*Optimizado para entornos educativos de IA.*
