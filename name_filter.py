# Importación de librerías necesarias
import random  # Para elegir nombres ficticios al azar
import json    # Para procesar la respuesta estructurada del LLM
import re      # Para usar expresiones regulares (búsqueda y reemplazo de texto)
from ollama import Client # Para comunicarnos con el servidor de Ollama

class NameFilter:
    """
    Filtro de nombres utilizando un LLM pequeño (gemma3:270m) para detección
    y sustitución por nombres ficticios.
    """

    # Pool (lista) de nombres ficticios proporcionado.
    # De aquí se extraerán los nombres de reemplazo para proteger la identidad real.
    FICTITIOUS_NAMES = [ 
        "Hugo García", "Mateo Rodríguez", "Martín González", "Leo López", "Daniel Martínez", "Alejandro Sánchez", "Manuel Pérez", "Pablo Gómez", "Álvaro Martín", "Adrián Jiménez", "Enzo Ruiz", "Mario Hernández", "Diego Díaz", "David Moreno", "Oliver Muñoz", "Marcos Álvarez", "Thiago Romero", "Marco Alonso", "Izan Gutiérrez", "Javier Navarro", "Bruno Torres", "Miguel Domínguez", "Antonio Vázquez", "Gonzalo Ramos", "Liam Gil", "Gael Ramírez", "Marc Serrano", "Carlos Blanco", "Juan Molina", "Ángel Morales", "Dylan Suárez", "Nicolás Ortega", "José Delgado", "Sergio Castro", "Gabriel Ortiz", "Luca Rubio", "Jorge Marín", "Darío Sanz", "Íker Núñez", "Samuel Iglesias", "Eric Medina", "Adam Garrido", "Héctor Cortés", "Francisco Castillo", "Rodrigo Santos", "Jesús Lozano", "Pau Guerrero", "Andrés Cano", "Saúl Prieto", "Lucía Méndez", "Sofía Cruz", "Martina Calvo", "María Gallego", "Julia Vidal", "Paula León", "Valeria Herrera", "Emma Márquez", "Daniela Peña", "Carla Flores", "Alma Cabrera", "Olivia Campos", "Sara Vega", "Carmen Fuentes", "Mía Carrasco", "Valentina Diez", "Alba Reyes", "Noa Caballero", "Chloe Nieto", "Claudia Aguilar", "Jimena Pascual", "Lola Santana", "Vega Herrero", "Abril Montero", "Mia Lorenzo", "Vera Hidalgo", "Elena Giménez", "Candela Ibáñez", "Aitana Ferrer", "Manuela Durán", "Triana Santiago", "Rocío Benítez", "Lara Vargas", "Alejandra Mora", "Inés Vicente", "Zoe Arias", "Carlota Carmona", "Blanca Crespo", "Marina Roman", "Laura Pastor", "Ana Soto", "Alicia Saez", "Clara Velasco", "Adriana Moya", "Irene Soler", "Emily Parra", "Gala Esteban", "Julieta Bravo", "Celia Gallardo", "Elsa Rojas", "Amanda Pardo", "Natalia Merino", "Ariadna Franco", "Amalia Espinosa", "Aurora Lara", "Violeta Rivas", "Andrea Silva", "Isabel Rivera", "Miriam Maldonado", "Luna Quintero", "Mara Robles", "Lia Arenas", "Berta Beltrán", "Nora Galán", "Eva Velez", "Elias Jurado", "Gorka Plaza", "Xavier Palacios", "Joan Núñez", "Pedro Marin", "Santiago Roldán", "Matías Valero", "Axel Báez", "Ian Benavides", "Felipe Guerra", "Tomás Cordero", "Biel Quintana", "Rubén Salinas", "Cristian Conde", "Aitor Guillén", "Erik Toledo", "Pol Avila", "Guillermo Pacheco", "Francisco Javier Alarcón", "Rafael Velázquez", "Alberto Aranda", "Luis Tapia", "Fernando Polo", "Raúl Carrillo", "Iván Villanueva", "Isaac Martí", "Félix Barrera", "César Calderón", "Alonso Sierra", "Víctor Perea", "Joel Clemente", "Roberto Soriano", "Jaime Montes", "Eduardo Orozco", "Ricardo Menéndez", "Oscar Acosta", "Emilio Esteban", "Mariano Rey", "Arturo Bernal", "Simón Cárdenas", "Victoria Robles", "Carolina Rosales", "Marta Salas", "Beatriz Andrade", "Nerea Contreras", "Patricia Escudero", "Lorena Bermúdez", "Cristina Macías", "Esther Galdón", "Diana Aguirre", "Raquel Varela", "Rosa Palomino", "Teresa Cuenca", "Silvia Fajardo", "Mónica Lemus", "Pilar Barroso", "Sandra Hurtado", "Yolanda Villegas", "Sonia Millán", "Lidia Castaño", "Margarita Zamora", "Rafaela Tamayo", "Consuelo Osorio", "Antonia Lagos", "Pepa Burgos", "Josefina Sepúlveda", "Luz Tejada", "Verónica Guevara", "Begoña Becerra", "Fátima Ballesteros", "Elisa Carreras", "Nuria Gámez", "Virginia Paredes", "Estela Cañas", "Adela Ledesma", "Gloria Cordero", "Esperanza Bustos", "Amparo Godoy", "Juana Trujillo", "Belén Pino", "Rosario Olivares", "Milagros Zapata", "Soledad Navarrete", "Cayetana Barajas", "Leire Cuervo", "Macarena Lago", "Estefanía Cornejo", "Iris Sanabria", "Maite Arcos", "Noelia Cerda", "Arlet Galindo", "Dafne Echeverría", "Ona Mota", "Cloe Quirós", "Jana Pineda", "Nahia Olmos", "Iria Casado", "Lina Farias", "Mabel Frías", "Renata Tello", "Teo Valladares", "Max Gamboa", "Caleb Arreola", "Nico Montalvo", "Luka Barrios", "Rayan Cisneros", "Jon Ochoa", "Ariel Murillo", "Milan Oviedo", "Dante Davila"
    ]

    def __init__(self):
        # Mapeos persistentes durante la vida de la instancia.
        # Son cruciales para mantener la coherencia en una conversación larga.
        self.real_to_fake = {} # Diccionario: Nombre Real -> Nombre Ficticio
        self.fake_to_real = {} # Diccionario: Nombre Ficticio -> Nombre Real

    def get_names_from_llm(self, client: Client, text: str) -> list[str]:
        """Usa Gemma3:270m para extraer nombres particulares."""
        # Log por consola para ver qué texto está analizando (solo los primeros 50 caracteres)
        print(f"\n--- [NameFilter] Analizando texto: '{text[:50]}...' ---")
        
        # Prompt diseñado con la técnica Few-Shot (dar ejemplos) para forzar al LLM
        # a devolver exclusivamente un JSON con los nombres extraídos.
        prompt = f"""### INSTRUCCIÓN
Eres un sistema experto en detección de PII (Información Personal Identificable). 
Tu ÚNICA tarea es extraer nombres de personas privadas (ciudadanos comunes) del texto proporcionado abajo.

### REGLAS ESTRICTAS
1. **IGNORA** cualquier nombre de celebridad, personaje histórico, político o figura pública (ej: Messi, Shakira, Cervantes).
2. **EXTRAE** solo nombres de personas normales/privadas mencionadas.
3. Devuelve los nombres EXACTAMENTE como aparecen en el texto.
4. Tu respuesta debe ser SOLAMENTE una lista JSON válida. Sin explicaciones.
5. Si no hay nombres privados, devuelve: []

### EJEMPLOS FEW-SHOT (Solo para guiarte, no los copies)
Input: "Soy Lucas y quiero saber de Cervantes."
Output: ["Lucas"]

Input: "Hablame de Marie Curie."
Output: []

Input: "Mi nombre es Ana López y mi tío se llama Pedro Martínez."
Output: ["Ana López", "Pedro Martínez"]

Input: "Dime algo sobre Cristiano Ronaldo y mi amigo Juanito."
Output: ["Juanito"]

### TEXTO A PROCESAR (Analiza esto):
<<<
{text}
>>>

### JSON DE SALIDA:
"""
        try:
            # Petición al LLM local para que identifique los nombres
            response = client.chat(
                model="gemma3:270m", # Asegurarse de tener este modelo instalado localmente
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.0}, # Determinista: 0.0 evita que el modelo alucine o sea creativo
                stream=False # Queremos la respuesta completa de golpe, no en streaming
            )
            content = response['message']['content'].strip()
            print(f"--- [NameFilter] Respuesta Raw LLM: {content}")
            
            # Intentar parsear JSON mediante expresiones regulares
            # Esto captura todo lo que esté entre corchetes [...] por si el LLM añade texto extra
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                json_str = match.group(0)
                # Reemplazar comillas simples por dobles para que el JSON sea válido
                json_str = json_str.replace("'", '"')
                names = json.loads(json_str) # Convertir el string JSON a una lista de Python
                
                flat_names = []
                # Función recursiva auxiliar para aplanar la lista 
                # (en caso de que el modelo devuelva listas anidadas como [["Ana"], ["Juan"]])
                def flatten(lst):
                    for item in lst:
                        if isinstance(item, list):
                            flatten(item)
                        elif isinstance(item, str):
                            flat_names.append(item)
                
                # Ejecutamos la función auxiliar
                flatten(names)
                print(f"--- [NameFilter] Nombres extraídos: {flat_names}")
                return flat_names
            
            # Si la expresión regular no encuentra un JSON válido
            print("--- [NameFilter] No se encontró lista JSON en respuesta.")
            return []
            
        except Exception as e:
            # Si el modelo falla o hay un error de conexión, se captura para no crashear la app
            print(f"--- [NameFilter] Error detectando nombres: {e}")
            return []

    def anonymize(self, client: Client, text: str) -> str:
        """Sustituye nombres reales por ficticios."""
        # 1. Obtener los nombres detectados por el modelo
        names = self.get_names_from_llm(client, text)
        anonymized_text = text
        
        # 2. Iterar sobre cada nombre detectado para reemplazarlo
        for name in names:
            name = name.strip()
            if not name: continue # Saltar si el string está vacío
            
            # Asignar ficticio si no tiene uno previamente asignado en esta sesión
            if name not in self.real_to_fake:
                # Elegir uno al azar de la lista predefinida
                fake_name = random.choice(self.FICTITIOUS_NAMES)
                
                # Bucle de seguridad para evitar colisiones (asegurar que el nombre ficticio 
                # no se esté usando ya para otra persona real en esta misma sesión)
                while fake_name in self.fake_to_real:
                    fake_name = random.choice(self.FICTITIOUS_NAMES)
                    
                # Guardar el mapeo en ambas direcciones
                self.real_to_fake[name] = fake_name
                self.fake_to_real[fake_name] = name
                print(f"--- [NameFilter] Mapeo Nuevo: '{name}' -> '{fake_name}'")
            else:
                 # Si ya existe, simplemente informamos por consola
                 print(f"--- [NameFilter] Mapeo Existente: '{name}' -> '{self.real_to_fake[name]}'")
            
            # Reemplazar en el texto original usando expresiones regulares
            # re.escape asegura que si el nombre tiene caracteres especiales, no rompan la regex
            # re.IGNORECASE hace que no distinga entre mayúsculas y minúsculas al buscar
            pattern = re.compile(re.escape(name), re.IGNORECASE)
            anonymized_text = pattern.sub(self.real_to_fake[name], anonymized_text)
            
        print(f"--- [NameFilter] Texto Anonimizado: '{anonymized_text[:50]}...'")
        return anonymized_text

    def deanonymize(self, text: str) -> str:
        """Restablece los nombres reales."""
        deanonymized_text = text
        
        # Iterar sobre el diccionario inverso (Nombre Ficticio -> Nombre Real)
        for fake, real in self.fake_to_real.items():
            pattern = re.compile(re.escape(fake), re.IGNORECASE)
            
            # Solo hace log (print) si realmente encuentra y reemplaza el nombre ficticio
            # en el texto generado por la IA, para mantener la consola limpia
            if pattern.search(deanonymized_text):
                print(f"--- [NameFilter] Restaurando: '{fake}' -> '{real}'")
            
            # Efectúa el reemplazo del nombre inventado por el original del usuario
            deanonymized_text = pattern.sub(real, deanonymized_text)
            
        return deanonymized_text