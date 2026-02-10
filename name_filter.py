import random
import json
import re
from ollama import Client

class NameFilter:
    """
    Filtro de nombres utilizando un LLM pequeño (gemma3:270m) para detección
    y sustitución por nombres ficticios.
    """

    # Pool de nombres ficticios proporcionado
    FICTITIOUS_NAMES = [ 
        "Hugo García", "Mateo Rodríguez", "Martín González", "Lucas Fernández", "Leo López", "Daniel Martínez", "Alejandro Sánchez", "Manuel Pérez", "Pablo Gómez", "Álvaro Martín", "Adrián Jiménez", "Enzo Ruiz", "Mario Hernández", "Diego Díaz", "David Moreno", "Oliver Muñoz", "Marcos Álvarez", "Thiago Romero", "Marco Alonso", "Izan Gutiérrez", "Javier Navarro", "Bruno Torres", "Miguel Domínguez", "Antonio Vázquez", "Gonzalo Ramos", "Liam Gil", "Gael Ramírez", "Marc Serrano", "Carlos Blanco", "Juan Molina", "Ángel Morales", "Dylan Suárez", "Nicolás Ortega", "José Delgado", "Sergio Castro", "Gabriel Ortiz", "Luca Rubio", "Jorge Marín", "Darío Sanz", "Íker Núñez", "Samuel Iglesias", "Eric Medina", "Adam Garrido", "Héctor Cortés", "Francisco Castillo", "Rodrigo Santos", "Jesús Lozano", "Pau Guerrero", "Andrés Cano", "Saúl Prieto", "Lucía Méndez", "Sofía Cruz", "Martina Calvo", "María Gallego", "Julia Vidal", "Paula León", "Valeria Herrera", "Emma Márquez", "Daniela Peña", "Carla Flores", "Alma Cabrera", "Olivia Campos", "Sara Vega", "Carmen Fuentes", "Mía Carrasco", "Valentina Diez", "Alba Reyes", "Noa Caballero", "Chloe Nieto", "Claudia Aguilar", "Jimena Pascual", "Lola Santana", "Vega Herrero", "Abril Montero", "Mia Lorenzo", "Vera Hidalgo", "Elena Giménez", "Candela Ibáñez", "Aitana Ferrer", "Manuela Durán", "Triana Santiago", "Rocío Benítez", "Lara Vargas", "Alejandra Mora", "Inés Vicente", "Zoe Arias", "Carlota Carmona", "Blanca Crespo", "Marina Roman", "Laura Pastor", "Ana Soto", "Alicia Saez", "Clara Velasco", "Adriana Moya", "Irene Soler", "Emily Parra", "Gala Esteban", "Julieta Bravo", "Celia Gallardo", "Elsa Rojas", "Amanda Pardo", "Natalia Merino", "Ariadna Franco", "Amalia Espinosa", "Aurora Lara", "Violeta Rivas", "Andrea Silva", "Isabel Rivera", "Miriam Maldonado", "Luna Quintero", "Mara Robles", "Lia Arenas", "Berta Beltrán", "Nora Galán", "Eva Velez", "Elias Jurado", "Gorka Plaza", "Xavier Palacios", "Joan Núñez", "Pedro Marin", "Santiago Roldán", "Matías Valero", "Axel Báez", "Ian Benavides", "Felipe Guerra", "Tomás Cordero", "Biel Quintana", "Rubén Salinas", "Cristian Conde", "Aitor Guillén", "Erik Toledo", "Pol Avila", "Guillermo Pacheco", "Francisco Javier Alarcón", "Rafael Velázquez", "Alberto Aranda", "Luis Tapia", "Fernando Polo", "Raúl Carrillo", "Iván Villanueva", "Isaac Martí", "Félix Barrera", "César Calderón", "Alonso Sierra", "Víctor Perea", "Joel Clemente", "Roberto Soriano", "Jaime Montes", "Eduardo Orozco", "Ricardo Menéndez", "Oscar Acosta", "Emilio Esteban", "Mariano Rey", "Arturo Bernal", "Simón Cárdenas", "Victoria Robles", "Carolina Rosales", "Marta Salas", "Beatriz Andrade", "Nerea Contreras", "Patricia Escudero", "Lorena Bermúdez", "Cristina Macías", "Esther Galdón", "Diana Aguirre", "Raquel Varela", "Rosa Palomino", "Teresa Cuenca", "Silvia Fajardo", "Mónica Lemus", "Pilar Barroso", "Sandra Hurtado", "Yolanda Villegas", "Sonia Millán", "Lidia Castaño", "Margarita Zamora", "Rafaela Tamayo", "Consuelo Osorio", "Antonia Lagos", "Pepa Burgos", "Josefina Sepúlveda", "Luz Tejada", "Verónica Guevara", "Begoña Becerra", "Fátima Ballesteros", "Elisa Carreras", "Nuria Gámez", "Virginia Paredes", "Estela Cañas", "Adela Ledesma", "Gloria Cordero", "Esperanza Bustos", "Amparo Godoy", "Juana Trujillo", "Belén Pino", "Rosario Olivares", "Milagros Zapata", "Soledad Navarrete", "Cayetana Barajas", "Leire Cuervo", "Macarena Lago", "Estefanía Cornejo", "Iris Sanabria", "Maite Arcos", "Noelia Cerda", "Arlet Galindo", "Dafne Echeverría", "Ona Mota", "Cloe Quirós", "Jana Pineda", "Nahia Olmos", "Iria Casado", "Lina Farias", "Mabel Frías", "Renata Tello", "Teo Valladares", "Max Gamboa", "Caleb Arreola", "Nico Montalvo", "Luka Barrios", "Rayan Cisneros", "Jon Ochoa", "Ariel Murillo", "Milan Oviedo", "Dante Davila"
    ]

    def __init__(self):
        # Mapeos persistentes durante la vida de la instancia
        self.real_to_fake = {}
        self.fake_to_real = {}

    def get_names_from_llm(self, client: Client, text: str) -> list[str]:
        """Usa Gemma3:270m para extraer nombres particulares."""
        print(f"\n--- [NameFilter] Analizando texto: '{text[:50]}...' ---")
        prompt = f"""### ROL
Eres un agente de seguridad de datos. Tu objetivo es detectar nombres de personas particulares (no famosas) para proteger su identidad.

### INSTRUCCIONES DE FORMATO
1. Si encuentras uno o más nombres de particulares, devuélvelos SIEMPRE dentro de una lista con este formato: ["Nombre 1", "Nombre 2"]
2. Si NO encuentras nombres de particulares, responde únicamente: []
3. NO incluyas explicaciones ni texto adicional.

### CRITERIO DE FILTRADO
- EXCLUIR: Personajes históricos, artistas famosos, políticos o figuras públicas conocidas (ej. Cristóbal Colón, Shakira, Steve Jobs).
- INCLUIR: Nombres de personas comunes, usuarios o familiares mencionados en el texto.

### EJEMPLOS
- Texto: "Soy Lucas y quiero saber de Cervantes." -> Salida: ["Lucas"]
- Texto: "Hablame de Marie Curie." -> Salida: []
- Texto: "Mi nombre es Ana López y mi tío se llama Pedro Martínez." -> Salida: ["Ana López", ["Pedro Martínez"]
- Texto: "Dime algo sobre Cristiano Ronaldo y mi amigo Juanito." -> Salida: ["Juanito"]

### TEXTO A PROCESAR:
"{text}"

### RESULTADO:
"""
        try:
            response = client.chat(
                model="gemma3:270m", # Asegurarse de tener este modelo
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.0}, # Determinista
                stream=False
            )
            content = response['message']['content'].strip()
            print(f"--- [NameFilter] Respuesta Raw LLM: {content}")
            
            # Intentar parsear JSON
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                json_str = match.group(0)
                json_str = json_str.replace("'", '"')
                names = json.loads(json_str)
                flat_names = []
                def flatten(lst):
                    for item in lst:
                        if isinstance(item, list):
                            flatten(item)
                        elif isinstance(item, str):
                            flat_names.append(item)
                flatten(names)
                print(f"--- [NameFilter] Nombres extraídos: {flat_names}")
                return flat_names
            print("--- [NameFilter] No se encontró lista JSON en respuesta.")
            return []
            
        except Exception as e:
            print(f"--- [NameFilter] Error detectando nombres: {e}")
            return []

    def anonymize(self, client: Client, text: str) -> str:
        """Sustituye nombres reales por ficticios."""
        names = self.get_names_from_llm(client, text)
        anonymized_text = text
        
        for name in names:
            name = name.strip()
            if not name: continue
            
            # Asignar ficticio si no tiene
            if name not in self.real_to_fake:
                fake_name = random.choice(self.FICTITIOUS_NAMES)
                while fake_name in self.fake_to_real:
                    fake_name = random.choice(self.FICTITIOUS_NAMES)
                    
                self.real_to_fake[name] = fake_name
                self.fake_to_real[fake_name] = name
                print(f"--- [NameFilter] Mapeo Nuevo: '{name}' -> '{fake_name}'")
            else:
                 print(f"--- [NameFilter] Mapeo Existente: '{name}' -> '{self.real_to_fake[name]}'")
            
            # Reemplazar en el texto
            pattern = re.compile(re.escape(name), re.IGNORECASE)
            anonymized_text = pattern.sub(self.real_to_fake[name], anonymized_text)
            
        print(f"--- [NameFilter] Texto Anonimizado: '{anonymized_text[:50]}...'")
        return anonymized_text

    def deanonymize(self, text: str) -> str:
        """Restablece los nombres reales."""
        deanonymized_text = text
        for fake, real in self.fake_to_real.items():
            pattern = re.compile(re.escape(fake), re.IGNORECASE)
            # Solo log si hay reemplazo para no ensuciar
            if pattern.search(deanonymized_text):
                print(f"--- [NameFilter] Restaurando: '{fake}' -> '{real}'")
            deanonymized_text = pattern.sub(real, deanonymized_text)
        return deanonymized_text
