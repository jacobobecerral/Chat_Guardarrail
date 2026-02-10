import re

class PIIFilter:
    """
    Filtro de Información Personal Identificable (PII).
    Detecta y reemplaza datos sensibles en el texto de entrada.
    """
    
    def __init__(self):
        # Lista de patrones (regex, reemplazo)
        # Nota: Se han eliminado los anclajes ^ y $ para permitir búsqueda en texto libre.
        # Se añaden \b (word boundaires) para evitar falsos positivos en números largos.
        self.patterns = [
            # 1. Emails (Prioridad alta para evitar conflictos con otros puntos/caracteres)
            # Validación estricta (RFC 5322 simplificada para capturar, según solicitud)
            (
                r"[a-zA-Z0-9.\!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*",
                "[EMAIL]"
            ),
            
            # 2. Tarjetas de Crédito
            # Validación por tipo (Visa, MC, Amex, Discover)
            (
                r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b",
                "[TARJETA_CREDITO]"
            ),
            # Validación simple (13-19 dígitos) - Con cuidado de no solapar
            (
                r"\b[0-9]{13,19}\b",
                "[TARJETA_CREDITO]"
            ),

            # 3. IBAN (España)
            # Con espacios
            (
                r"\bES\d{2}\s?\d{4}\s?\d{4}\s?\d{2}\s?\d{10}\b",
                "[IBAN]"
            ),
            # Sin espacios (aunque la regex anterior con \s? cubre ambos, se mantiene por especificidad)
            (
                r"\bES\d{22}\b",
                "[IBAN]"
            ),

            # 4. DNI / NIE
            # DNI Básico + Letra (incluye validación de formato básico 8 num + letra)
            (
                r"\b[0-9]{8}[A-Z]\b",
                "[DNI]"
            ),
            # NIE
            (
                r"\b[XYZ][0-9]{7}[A-Z]\b",
                "[NIE]"
            ),

            # 5. Seguridad Social (NSS)
            # Con espacios
            (
                r"\b[0-9]{2}\s?[0-9]{10}\b",
                "[NSS]"
            ),
            # Sin espacios (12 dígitos) - Cuidado: esto también hace match con tarjetas de 12 (si existen/falsos positivos) 
            # o números aleatorios. Se coloca al final.
            (
                r"\b[0-9]{12}\b",
                "[NSS]"
            )
        ]

    def anonymize(self, text: str) -> str:
        """
        Reemplaza ocurrencias de PII en el texto con sus etiquetas correspondientes.
        
        Args:
            text (str): Texto original.
            
        Returns:
            str: Texto sanitizado.
        """
        if not text:
            return ""
            
        sanitized_text = text
        for pattern, replacement in self.patterns:
            # flags=re.IGNORECASE para casos como 'es' en IBAN si fuera necesario, 
            # pero el estándar suele ser mayúsculas. DNI letra suele ser mayúscula.
            # Mantenemos case-sensitive default salvo para parts que lo requieran.
            sanitized_text = re.sub(pattern, replacement, sanitized_text)
            
        return sanitized_text

# Instancia global (opcional) o para pruebas
if __name__ == "__main__":
    # Tests rápidos
    filtro = PIIFilter()
    test_text = "Hola, mi DNI es 12345678Z y mi cuenta ES12 1234 1234 12 1234567890. Correo: test@example.com"
    print(f"Original: {test_text}")
    print(f"Filtrado: {filtro.anonymize(test_text)}")
