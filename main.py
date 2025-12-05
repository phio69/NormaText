"""
Точка входа в NormaText.
"""

import tkinter as tk
from ui import ModernNormaTextUI
from core import load_document, check_terminology, check_structure, check_numbering, auto_fix_terminology, save_fixed_document
from tkinter import messagebox, filedialog
import datetime


class NormaTextApp:
    def __init__(self):

        # Создание главного окна приложения
        self.root = tk.Tk()

        # Текущий загруженный документ и путь к нему
        self.document = None
        self.current_file_path = None

        # Списки для хранения ошибок на разных этапах работы
        self.original_errors = []  #
        self.current_errors = []  #
        self.fixed_errors = []

        # Создание пользовательского интерфейсас передачей callback-функций
        self.ui = ModernNormaTextUI(
            self.root,
            on_check=self.run_check,
            on_export=self.export_report,
            on_auto_fix=self.auto_fix,
            on_save=self.save_fixed
        )

    def run_check(self, file_path: str, doc_type: str, rules: list):
        try:
            # Загрузка документа через ядро системы
            self.document = load_document(file_path)
            self.current_file_path = file_path

            if self.document is None:
                messagebox.showerror("Ошибка", "Не удалось загрузить документ")
                return

            errors = []

            # Последовательный запуск выбранных пользователем проверок
            if "терминология" in rules:
                errors.extend(check_terminology(self.document))
            if "структура" in rules:
                errors.extend(check_structure(self.document, doc_type))
            if "нумерация" in rules:
                errors.extend(check_numbering(self.document, doc_type))

            # Сохранение результатов проверки в атрибутах класса
            self.original_errors = errors.copy()
            self.current_errors = errors.copy()
            self.fixed_errors = []

            # Передаем список ошибок в UI
            self.ui.update_report(errors)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обработать файл:\n{str(e)}")

    def auto_fix(self):
        """Автоматическое исправление терминологии"""
        if self.document is None:
            messagebox.showwarning("Внимание", "Сначала загрузите документ и выполните проверку!")
            return

        try:
            # 1. Вызов функции автоматического исправления из ядра системы
            replacements_count = auto_fix_terminology(self.document)

            if replacements_count > 0:
                # 2. Разделение ошибок на исправленные и оставшиеся
                fixed_errors = []
                remaining_errors = []

                for error in self.current_errors:
                    if "Недопустимое слово" in error:
                        fixed_errors.append(error)
                    else:
                        remaining_errors.append(error)

                # 3. Обновление состояния ошибок
                self.fixed_errors = fixed_errors
                self.current_errors = remaining_errors

                # 4. Обновление интерфейса с оставшимися ошибками
                self.ui.update_report(remaining_errors)

                messagebox.showinfo(
                    "Успех",
                    f"Исправлено ошибок терминологии: {len(fixed_errors)}\n"
                    f"Осталось других ошибок: {len(remaining_errors)}"
                )
            else:
                messagebox.showinfo("Информация", "Не найдено слов для автоматического исправления")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить автоматическое исправление:\n{str(e)}")

    def export_report(self):
        """Экспортирует отчет в TXT"""
        # Формирование структурированного текстового отчета
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_lines = [
            "=" * 60,
            "ОТЧЕТ О ПРОВЕРКЕ ДОКУМЕНТА",
            "=" * 60,
            f"Дата и время: {timestamp}",
            f"Документ: {self.current_file_path if self.current_file_path else 'Не указан'}",
            "",
            "ТЕКУЩИЕ ОШИБКИ:"
        ]

        # Добавление текущих ошибок в отчет
        if self.current_errors:
            for error in self.current_errors:
                report_lines.append(f"• {error}")
        else:
            report_lines.append("Ошибок не найдено")

        # Добавление раздела с исправленными ошибками (если они есть)
        if hasattr(self, 'fixed_errors') and self.fixed_errors:
            report_lines.extend([
                "",
                "=" * 60,
                "ИСПРАВЛЕННЫЕ ОШИБКИ (автоматически):",
                "=" * 60,
                "Проверьте правильность склонения исправленных слов:",
                ""
            ])

            for i, error in enumerate(self.fixed_errors, 1):
                report_lines.append(f"{i}. {error}")

            report_lines.extend([
                "",
                "ПРИМЕЧАНИЕ: Автоматическое исправление может требовать",
                "дополнительной ручной проверки контекста.",
                "=" * 60
            ])

        report_text = "\n".join(report_lines)

        # Диалог сохранения файла
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
            initialfile="отчет_ошибок.txt"
        )

        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(report_text)
                messagebox.showinfo("Успех", f"Отчёт сохранён:\n{path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

    def save_fixed(self):
        if self.document is None:
            messagebox.showwarning("Внимание", "Нет загруженного документа!")
            return

        try:
            # Сценарий 1: Автоматическое сохранение с суффиксом
            if self.current_file_path:
                # Разделение пути на имя и расширение
                path_parts = self.current_file_path.rsplit('.', 1)
                # Формирование нового пути с суффиксом
                new_path = f"{path_parts[0]}_исправленный.docx"

                # Вызов функции сохранения
                result = save_fixed_document(self.document, new_path)
                messagebox.showinfo("Успех", result)

            # Сценарий 2: интерактивный выбор места сохранения
            else:
                # Открытие диалогового окна выбора файла
                path = filedialog.asksaveasfilename(
                    defaultextension=".docx",
                    filetypes=[("Документы Word", "*.docx"), ("Все файлы", "*.*")]
                )
                # Если пользователь выбрал путь
                if path:
                    # Непосредственное сохранение файла
                    self.document.save(path)
                    messagebox.showinfo("Успех", f"Документ сохранён:\n{path}")

        except Exception as e:
            # Обработка возможных ошибок во время сохранения
            messagebox.showerror("Ошибка", f"Не удалось сохранить документ:\n{str(e)}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = NormaTextApp()
    app.run()