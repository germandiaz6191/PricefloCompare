import re
from difflib import SequenceMatcher
from typing import Tuple


def normalize_text(text: str) -> str:
    """
    Normaliza texto para mejorar la comparación de búsquedas.

    Args:
        text: Texto a normalizar

    Returns:
        Texto normalizado en minúsculas, sin espacios extras
    """
    if not text:
        return ""

    # Convertir a minúsculas
    text = text.lower()

    # Eliminar caracteres especiales pero mantener números y letras
    # Mantener espacios para preservar palabras
    text = re.sub(r'[^\w\s]', ' ', text)

    # Normalizar espacios entre números y unidades (17 Kg -> 17kg)
    text = re.sub(r'(\d+)\s*(kg|l|cm|m|gb|tb|pulgadas|")', r'\1\2', text)

    # Reducir múltiples espacios a uno solo
    text = re.sub(r'\s+', ' ', text)

    # Eliminar espacios al inicio y final
    text = text.strip()

    return text


def calculate_relevance_score(search_term: str, title: str, threshold: int = 60) -> Tuple[int, bool]:
    """
    Calcula un score de relevancia entre 0-100 comparando el término de búsqueda con el título.

    Args:
        search_term: Término buscado por el usuario
        title: Título del producto encontrado
        threshold: Score mínimo para considerar el resultado relevante (default: 60)

    Returns:
        Tupla con (score, is_relevant)
        - score: Puntuación de 0-100
        - is_relevant: True si el score >= threshold
    """
    if not search_term or not title:
        return 0, False

    # Normalizar ambos textos
    search_normalized = normalize_text(search_term)
    title_normalized = normalize_text(title)

    # Si están vacíos después de normalizar
    if not search_normalized or not title_normalized:
        return 0, False

    # Calcular similitud general con SequenceMatcher (0.0 a 1.0)
    similarity_ratio = SequenceMatcher(None, search_normalized, title_normalized).ratio()
    similarity_score = similarity_ratio * 50  # Vale hasta 50 puntos

    # Calcular coincidencia de palabras clave
    search_words = set(search_normalized.split())
    title_words = set(title_normalized.split())

    if not search_words:
        return 0, False

    # Palabras que coinciden
    matching_words = search_words & title_words
    word_match_ratio = len(matching_words) / len(search_words)
    word_match_score = word_match_ratio * 50  # Vale hasta 50 puntos

    # Score total
    total_score = int(similarity_score + word_match_score)

    # Bonus: si todas las palabras clave están presentes, suma 10 puntos
    if word_match_ratio == 1.0:
        total_score = min(100, total_score + 10)

    # Determinar si es relevante
    is_relevant = total_score >= threshold

    return total_score, is_relevant


def extract_key_terms(text: str) -> set:
    """
    Extrae términos clave de un texto (palabras significativas).

    Args:
        text: Texto del cual extraer términos

    Returns:
        Set con las palabras significativas
    """
    # Palabras comunes a ignorar (stop words en español)
    stop_words = {
        'el', 'la', 'de', 'en', 'y', 'a', 'con', 'por', 'para', 'un', 'una',
        'los', 'las', 'del', 'al', 'es', 'su', 'que', 'como', 'más', 'este',
        'esta', 'ese', 'esa'
    }

    normalized = normalize_text(text)
    words = normalized.split()

    # Filtrar stop words y palabras muy cortas
    key_terms = {word for word in words if word not in stop_words and len(word) > 2}

    return key_terms


def format_price(price_str: str) -> str:
    """
    Formatea un string de precio para presentación consistente.

    Args:
        price_str: String con el precio (puede incluir símbolos, espacios, etc.)

    Returns:
        Precio formateado como "$X,XXX,XXX"
    """
    if not price_str:
        return "Precio no disponible"

    # Extraer solo números
    numbers = re.sub(r'[^\d]', '', price_str)

    if not numbers:
        return price_str  # Devolver original si no hay números

    try:
        # Convertir a entero y formatear con separadores de miles
        price_int = int(numbers)
        formatted = f"${price_int:,}"
        return formatted
    except ValueError:
        return price_str
