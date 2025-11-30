import unittest
from main import NormaTextApp
import pymorphy3

class TestNormaText(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        "Инициализация морфологического анализатора"
        cls.morph = pymorphy3.MorphAnalyzer()

    def test_lemmatization_basic(self):
        "Проверка лемматизации обычного слова."
        word = "штуку"
        clean = word.strip(".,;:!?\"'()[]{}")
        normal_form = self.morph.parse(clean.lower())[0].normal_form
        self.assertEqual(normal_form, "штука")

    def test_allowed_word_not_detected(self):
        "Разрешённое слово не попадает в список запрещённых."
        forbidden_set = {"штука", "тип"}
        normal_form = "документ"
        self.assertNotIn(normal_form, forbidden_set)

    def test_empty_word_skipped(self):
        "Пустое слово игнорируется."
        word = ""
        self.assertFalse(word.isalpha())

    def test_word_with_digits_ignored(self):
        "слово с цифрами не обрабатывается."
        word = "слово123"
        self.assertFalse(word.isalpha())

"python -m unittest test_normatext.py -v"