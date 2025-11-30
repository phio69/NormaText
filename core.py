"""
Ядро логики NormaText: работа с документом, проверка по ГОСТ, лемматизация.
"""

from docx import Document
import pymorphy3
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class Heading:
    """Класс для представления заголовка"""
    level: int           # Уровень (1, 2, 3...)
    text: str           # Текст заголовка
    paragraph_index: int # Номер абзаца в документе
    number: str         # Номер (например, "1", "1.1", "2.3.1")

# Инициализация морфологического анализатора (один раз для всего приложения)
_morph = pymorphy3.MorphAnalyzer()

# Словарь запрещённых слов (в начальной форме)
FORBIDDEN_WORDS = {
    "штука", "типа", "короче", "ну тип", "как бы", "просто", "вообще", "очень",
    "крутой", "прикольный", "нифига", "блин", "чё", "надо", "дело", "общий",
    "факт", "имхо", "походу", "зачем", "чтоб", "ага", "угу", "аг", "сам",
    "конечно", "честно", "говорить", "вот", "именно", "так", "надо", "ничего",
    "фигня", "бардак", "завал", "халява", "лажа", "прикол", "треш", "огонь",
    "кажется", "думать", "мнение", "всё", "равно", "любой", "случай", "там",
    "этот", "самый", "вроде", "быть", "наверно", "примерно", "некоторый", "разный",
    "всякий", "чел", "народ", "ребята", "чувак", "пацан", "девчонка", "хотеть",
    "жестко", "кайф", "ништяк", "отпад", "жесть", "бомбить", "зашквар", "лол",
    "кек", "ржака", "мем", "сарказм", "ирония", "понимать", "идти", "прочее",
    "такой", "вообще", "собственно", "фактически", "самый", "дело", "сути", "принцип"
}

def load_document(file_path):
    """Загружает .docx-документ."""
    return Document(file_path)

def check_terminology(document):
    """Проверяет документ на наличие запрещённых слов."""
    errors = []
    all_lines = [(i + 1, p.text) for i, p in enumerate(document.paragraphs) if p.text.strip()]

    for line_num, text in all_lines:
        words = text.split()
        for word in words:
            clean = word.strip(".,;:!?\"'()[]{}—–-")
            if not clean or not clean.isalpha():
                continue
            try:
                normal_form = _morph.parse(clean.lower())[0].normal_form
                if normal_form in FORBIDDEN_WORDS:
                    errors.append(
                        f"• Стр. {line_num}: Недопустимое слово «{clean}» (основа: «{normal_form}»)"
                    )
            except Exception:
                continue
    return errors

def check_structure(document, doc_type="приказ"):
    """Проверяет структуру (упрощённо)."""
    errors = []
    text_sample = " ".join(p.text for p in document.paragraphs[:5])
    if doc_type == "приказ" and "утверждаю" not in text_sample.lower():
        errors.append("• Стр. 1: Отсутствует реквизит «Утверждаю»")
    return errors


def extract_headings(document) -> List[Heading]:
    """
    Извлекает заголовки из документа на основе стилей.
    Строго по ГОСТу - точка после номера НЕ допускается.
    """
    headings = []

    for i, paragraph in enumerate(document.paragraphs):
        if not paragraph.text.strip():
            continue

        # Определяем уровень заголовка по стилю
        level = None
        if paragraph.style.name.startswith('Heading'):
            try:
                level = int(paragraph.style.name.split()[-1])
            except (ValueError, IndexError):
                continue

        if level is not None:
            text = paragraph.text.strip()

            # Строгий парсинг по ГОСТу - номер и текст разделяются пробелом
            # Формат: "1 Текст" или "1.1 Текст" (без точки после номера)
            parts = text.split(' ', 1)
            if len(parts) > 1:
                potential_number = parts[0]

                # Проверяем, что это номер в правильном формате (без точки в конце)
                if _is_valid_number_format(potential_number, level):
                    number = potential_number
                    remaining_text = parts[1]
                else:
                    # Если номер с точкой в конце - это ошибка
                    number = ""
                    remaining_text = text
            else:
                # Нет пробела после номера или номер отсутствует
                number = ""
                remaining_text = text

            headings.append(Heading(
                level=level,
                text=remaining_text.strip(),
                paragraph_index=i,
                number=number
            ))

    return headings

def _is_valid_number_format(number: str, level: int) -> bool:
    """
    Проверяет корректность формата номера по ГОСТ.

    Согласно ГОСТ Р 7.0.97-2016:
    - Номер состоит из цифр, разделенных точками
    - Точка после номера НЕ ставится
    - Количество частей должно соответствовать уровню
    """
    # Убираем возможные пробелы в начале/конце
    number = number.strip()

    parts = number.split('.')

    # Уровень должен соответствовать количеству частей
    if len(parts) != level:
        return False

    # Все части должны быть числами
    try:
        for part in parts:
            int(part)
    except ValueError:
        return False

    return True


def _check_sequence(heading: Heading, current_numbers: dict, index: int, all_headings: List[Heading]) -> Optional[str]:
    """Упрощенная и надежная проверка последовательности."""
    parts = [int(p) for p in heading.number.split('.')]
    level = heading.level

    # Проверяем только текущий уровень
    current_num = parts[level - 1]

    if level not in current_numbers:
        # Новый уровень - должен начинаться с 1
        if current_num != 1:
            return f"• Стр. {heading.paragraph_index + 1}: Первый номер на уровне {level} должен быть 1, а не {current_num}"
        current_numbers[level] = current_num
    else:
        # Проверяем последовательность
        expected = current_numbers[level] + 1
        if current_num != expected:
            return f"• Стр. {heading.paragraph_index + 1}: Ожидался номер {expected}, а не {current_num} на уровне {level}"
        current_numbers[level] = current_num

    # Сбрасываем более глубокие уровни
    for l in list(current_numbers.keys()):
        if l > level:
            del current_numbers[l]

    return None

def check_numbering(document, doc_type: str = "приказ") -> List[str]:
    """
    Проверяет правильность нумерации разделов документа.

    Args:
        document: Загруженный документ python-docx

    Returns:
        List[str]: Список ошибок нумерации
    """
    errors = []
    headings = extract_headings(document)

    if not headings:
        return ["• Документ не содержит заголовков с нумерацией"]

    # Словарь для отслеживания текущих номеров на каждом уровне
    current_numbers = {}

    for i, heading in enumerate(headings):
        level = heading.level

        # Проверяем формат номера
        if heading.number:
            if not _is_valid_number_format(heading.number, level):
                errors.append(
                    f"• Стр. {heading.paragraph_index + 1}: "
                    f"Неверный формат номера '{heading.number}' для уровня {level}"
                )
                continue

            # Проверяем последовательность
            error_msg = _check_sequence(heading, current_numbers, i, headings)
            if error_msg:
                errors.append(error_msg)
        else:
            errors.append(
                f"• Стр. {heading.paragraph_index + 1}: "
                f"Заголовок уровня {level} не содержит номера"
            )

    return errors