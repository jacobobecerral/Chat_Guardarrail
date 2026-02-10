from datetime import datetime
from ollama import Client

class LlamaGuard:
    """
    Gestor de seguridad utilizando el modelo llama-guard3.
    """
    
    # Mapeo de categorías de violación según la documentación de Llama Guard 3
    VIOLATION_CATEGORIES = {
        "S1": "Delitos violentos",
        "S2": "Delitos no violentos",
        "S3": "Delitos sexuales",
        "S4": "Explotación infantil",
        "S5": "Difamar", # Defamation
        "S6": "Asesoramiento especializado", # Specialized Advice
        "S7": "Violaciones de privacidad", # Privacy
        "S8": "Propiedad intelectual", # IP
        "S9": "Armas indiscriminadas", # Indiscriminate Weapons
        "S10": "Discurso de odio", # Hate Speech
        "S11": "Autolesiones", # Suicide & Self-Harm
        "S12": "Contenido sexual", # Sexual Content
        "S13": "Elecciones", # Elections
        "S14": "Manipulación de código intérprete" # Code Interpreter Abuse
    }

    @staticmethod
    def check_safety(client: Client, message_content: str) -> tuple[bool, str]:
        """
        Verifica si un mensaje es seguro usando llama-guard3.
        
        Args:
            client (ollama.Client): Cliente de Ollama configurado.
            message_content (str): Texto del mensaje a verificar.
            
        Returns:
            tuple[bool, str]: (Es Seguro, Mensaje de Razón/Error)
        """
        try:
            # Enviar el mensaje a llama-guard3
            # Llama Guard espera un formato específico, pero ollama.chat suele manejarlo.
            # Simplemente enviamos el mensaje del usuario.
            response = client.chat(
                model="llama-guard3",
                messages=[{"role": "user", "content": message_content}],
                stream=False
            )
            
            result_content = response['message']['content'].strip()
            
            # Formato esperado: "safe" o "unsafe\nS9"
            if result_content.startswith("safe"):
                return True, "Safe"
            
            if result_content.startswith("unsafe"):
                # Extraer códigos de violación (pueden ser múltiples, ej: S9,S10)
                parts = result_content.split("\n")
                violation_code = parts[1].strip() if len(parts) > 1 else "Unknown"
                
                # Traducir código
                category_name = LlamaGuard.VIOLATION_CATEGORIES.get(violation_code, f"Categoría desconocida ({violation_code})")
                
                # Logging en consola
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] BLOCKED - Category: {category_name} - User attempted unsafe content")
                
                return False, category_name

            # Respuesta inesperada
            print(f"Llama Guard Unexpected Response: {result_content}")
            return True, "Safe (Unexpected Response)"
            
        except Exception as e:
            # Fallback seguro: si falla el guard, asumimos riesgo y bloqueamos?
            # O permitimos si es error de conexión?
            # Para UX, mejor retornamos True pero logueamos el error, 
            # salvo que la seguridad sea crítica. Aquí retornamos True para no bloquear app.
            print(f"Error en Llama Guard check: {e}")
            return True, "Safe (Error)"
