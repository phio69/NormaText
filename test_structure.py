"""
Модульные тесты для проверки структуры документа (пункт «структура» в NormaText).
Тестируются функции: check_required_fields, check_formatting,
check_paragraphs_structure, check_lists_formatting, check_fonts_and_sizes.
"""

import unittest
from unittest.mock import Mock, MagicMock
from core import (
    check_required_fields,
    check_formatting,
    check_paragraphs_structure,
    check_lists_formatting,
    check_fonts_and_sizes
)


class TestStructureFunctions(unittest.TestCase):

    def test_check_required_fields_приказ_успех(self):
        # Подделываем документ с текстом, содержащим "приказ"
        doc = Mock()
        doc.paragraphs = [Mock(text="Приказ №123")]
        errors = check_required_fields(doc, "приказ")
        self.assertEqual(errors, [])

    def test_check_required_fields_приказ_неудача(self):
        # Документ не содержит слова "приказ"
        doc = Mock()
        doc.paragraphs = [Mock(text="Служебная записка")]
        errors = check_required_fields(doc, "приказ")
        self.assertIn("• Отсутствует обязательный реквизит: 'приказ'", errors)

    def test_check_required_fields_отчёт_успех(self):
        doc = Mock()
        doc.paragraphs = [Mock(text="Отчёт по практике"), Mock(text="Реферат"), Mock(text="Заключение"), Mock(text="Список использованных источников")]
        errors = check_required_fields(doc, "отчёт")
        self.assertEqual(errors, [])

    def test_check_required_fields_служебная_записка_успех(self):
        doc = Mock()
        doc.paragraphs = [Mock(text="Служебная записка от 01.12.2025")]
        errors = check_required_fields(doc, "служебная записка")
        self.assertEqual(errors, [])

    def test_check_formatting_выравнивание_ширина(self):
        # alignment=3 — по ширине (допустимо)
        paragraph = Mock()
        paragraph.text = "Обычный текст."
        paragraph.alignment = 3
        doc = Mock()
        doc.paragraphs = [paragraph]
        errors = check_formatting(doc)
        self.assertEqual(errors, [])

    def test_check_formatting_выравнивание_центр_ошибка(self):
        # alignment=1 — по центру (запрещено)
        paragraph = Mock()
        paragraph.text = "Текст по центру"
        paragraph.alignment = 1
        doc = Mock()
        doc.paragraphs = [paragraph]
        errors = check_formatting(doc)
        self.assertIn("• Стр. 1: Рекомендуется выравнивание по ширине или левому краю", errors)

    def test_check_formatting_capslock_ошибка(self):
        paragraph = Mock()
        paragraph.text = "ЭТОТ АБЗАЦ НАПИСАН ПОЛНОСТЬЮ ЗАГЛАВНЫМИ БУКВАМИ И ОН ОЧЕНЬ ДЛИННЫЙ"
        doc = Mock()
        doc.paragraphs = [paragraph]
        errors = check_formatting(doc)
        self.assertIn("• Стр. 1: Избегайте написания всего текста в верхнем регистре", errors)

    def test_check_paragraphs_structure_слишком_длинный_абзац(self):
        long_text = "A" * 600  # >500 символов
        paragraph = Mock()
        paragraph.text = long_text
        doc = Mock()
        doc.paragraphs = [paragraph]
        errors = check_paragraphs_structure(doc)
        self.assertIn("• Стр. 1: Абзац слишком длинный (разбейте на несколько)", errors)

    def test_check_lists_formatting_маркированный_пустой(self):
        paragraph = Mock()
        paragraph.text = "• "
        doc = Mock()
        doc.paragraphs = [paragraph]
        errors = check_lists_formatting(doc)
        self.assertIn("• Стр. 1: Пустой элемент списка", errors)

    def test_check_lists_formatting_нумерованный_пустой(self):
        paragraph = Mock()
        paragraph.text = "1. "
        doc = Mock()
        doc.paragraphs = [paragraph]
        errors = check_lists_formatting(doc)
        self.assertIn("• Стр. 1: Пустой элемент нумерованного списка", errors)

    def test_check_fonts_and_sizes_шрифт_неверный(self):
        # Создаём мок-абзац с неправильным шрифтом
        run = Mock()
        run.text = "Текст"
        run.font.name = "Arial"
        run.font.size = None  # размер не проверяем в этом тесте

        paragraph = Mock()
        paragraph.text = "Текст"
        paragraph.runs = [run]
        paragraph.style.name = "Normal"

        doc = Mock()
        doc.paragraphs = [paragraph]

        errors = check_fonts_and_sizes(doc)
        self.assertIn("• Обнаружены нерекомендуемые шрифты: Arial (ГОСТ: Times New Roman)", errors)

    def test_check_fonts_and_sizes_размер_текста_слишком_мал(self):
        run = Mock()
        run.text = "Текст"
        run.font.name = "Times New Roman"
        # Эмулируем размер как объект с pt
        size_obj = Mock()
        size_obj.pt = 10  # <12 — ошибка
        run.font.size = size_obj

        paragraph = Mock()
        paragraph.text = "Текст"
        paragraph.runs = [run]
        paragraph.style.name = "Normal"

        doc = Mock()
        doc.paragraphs = [paragraph]

        errors = check_fonts_and_sizes(doc)
        self.assertIn("• Несоответствие размеров шрифта: текст: 10.0pt (требуется 12-14pt)", errors)

    def test_check_fonts_and_sizes_размер_заголовка_слишком_большой(self):
        run = Mock()
        run.text = "Заголовок"
        run.font.name = "Times New Roman"
        size_obj = Mock()
        size_obj.pt = 18  # >16 — ошибка для заголовка
        run.font.size = size_obj

        paragraph = Mock()
        paragraph.text = "Заголовок"
        paragraph.runs = [run]
        paragraph.style.name = "Heading 1"  # важный момент: заголовок

        doc = Mock()
        doc.paragraphs = [paragraph]

        errors = check_fonts_and_sizes(doc)
        self.assertIn("• Несоответствие размеров шрифта: заголовок: 18.0pt (требуется 14-16pt)", errors)


if __name__ == "__main__":
    unittest.main()