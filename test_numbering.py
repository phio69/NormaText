"""
Модульные тесты для проверки пункта «Нумерация» в NormaText.
"""

import unittest
from unittest.mock import Mock
from core import extract_headings, _is_valid_number_format, _check_sequence, Heading


class TestNumberingFunctions(unittest.TestCase):

    def test__is_valid_number_format_допустимый_номер(self):
        """Проверка допустимых форматов номеров: функция возвращает True для корректных номеров по ГОСТ (без точки в конце)."""
        self.assertTrue(_is_valid_number_format("1", 1))
        self.assertTrue(_is_valid_number_format("1.1", 2))
        self.assertTrue(_is_valid_number_format("2.3.1", 3))
        self.assertTrue(_is_valid_number_format("10.15.7.2", 4))

    def test__is_valid_number_format_недопустимый_формат(self):
        """Проверка недопустимых форматов: функция возвращает False при наличии точки в конце, нечисловых символов или несоответствии уровня."""
        self.assertFalse(_is_valid_number_format("1.", 1))
        self.assertFalse(_is_valid_number_format("2.1.", 2))
        self.assertFalse(_is_valid_number_format("1.2", 1))
        self.assertFalse(_is_valid_number_format("5", 2))
        self.assertFalse(_is_valid_number_format("1.a", 2))
        self.assertFalse(_is_valid_number_format("I.II", 2))

    def test_extract_headings_корректная_нумерация(self):
        """Извлечение заголовков с правильной нумерацией: номер и текст корректно разделяются по первому пробелу."""
        p1 = Mock()
        p1.text = "1 Введение"
        p1.style.name = "Heading 1"

        p2 = Mock()
        p2.text = "2.1 Подраздел"
        p2.style.name = "Heading 2"

        doc = Mock()
        doc.paragraphs = [p1, p2]

        headings = extract_headings(doc)

        self.assertEqual(len(headings), 2)
        self.assertEqual(headings[0].number, "1")
        self.assertEqual(headings[0].text, "Введение")
        self.assertEqual(headings[1].number, "2.1")
        self.assertEqual(headings[1].text, "Подраздел")

    def test_extract_headings_некорректный_формат(self):
        """Извлечение заголовков без номера или с точкой: в обоих случаях поле number остаётся пустым."""
        p1 = Mock()
        p1.text = "Введение"  # номер отсутствует
        p1.style.name = "Heading 1"

        p2 = Mock()
        p2.text = "1. Введение с точкой"  # точка после номера — ошибка по ГОСТ
        p2.style.name = "Heading 1"

        doc = Mock()
        doc.paragraphs = [p1, p2]

        headings = extract_headings(doc)

        self.assertEqual(len(headings), 2)
        self.assertEqual(headings[0].number, "")
        self.assertEqual(headings[1].number, "")

    def test__check_sequence_корректная_последовательность(self):
        """Проверка корректной иерархической последовательности: 1 → 1.1 → 1.2 → 2 не вызывает ошибок."""
        current_numbers = {}
        h1 = Heading(level=1, text="Введение", paragraph_index=0, number="1")
        h2 = Heading(level=2, text="Теория", paragraph_index=1, number="1.1")
        h3 = Heading(level=2, text="Практика", paragraph_index=2, number="1.2")
        h4 = Heading(level=1, text="Заключение", paragraph_index=3, number="2")

        errors = []
        for h in [h1, h2, h3, h4]:
            err = _check_sequence(h, current_numbers, 0, [])
            if err:
                errors.append(err)

        self.assertEqual(errors, [])

    def test__check_sequence_первый_не_единица(self):
        """Первый заголовок уровня 1 не равен «1»: возвращается сообщение об ошибке."""
        current_numbers = {}
        h = Heading(level=1, text="Начало", paragraph_index=0, number="2")
        err = _check_sequence(h, current_numbers, 0, [])
        self.assertIn("Первый номер на уровне 1 должен быть 1, а не 2", err)

    def test__check_sequence_пропущенный_номер(self):
        """Пропущен номер в последовательности: после 1 сразу идёт 3 — ожидается ошибка с номером 2."""
        current_numbers = {1: 1}
        h = Heading(level=1, text="Третий", paragraph_index=1, number="3")
        err = _check_sequence(h, current_numbers, 1, [])
        self.assertIn("Ожидался номер 2, а не 3 на уровне 1", err)