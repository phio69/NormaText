"""
Точка входа в NormaText.
"""

import tkinter as tk
from ui import ModernNormaTextUI
from core import load_document, check_terminology, check_structure, check_numbering, auto_fix_terminology, save_fixed_document
from tkinter import messagebox, filedialog

class NormaTextApp:
    def __init__(self):
        self.root = tk.Tk()
        self.document = None
        self.ui = ModernNormaTextUI(  # ← ИСПОЛЬЗУЕМ НОВЫЙ ИНТЕРФЕЙС
            self.root,
            on_check=self.run_check,
            on_export=self.export_report,
            on_auto_fix=self.auto_fix,
            on_save=self.save_fixed
        )

    def run_check(self, file_path: str, doc_type: str, rules: list):
        try:
            self.document = load_document(file_path)
            if self.document is None:
                messagebox.showerror("Ошибка", "Не удалось загрузить документ")
                return

            errors = []
            if "терминология" in rules:
                errors.extend(check_terminology(self.document))
            if "структура" in rules:
                errors.extend(check_structure(self.document, doc_type))  # Теперь проверяет реквизиты!
            if "нумерация" in rules:
                errors.extend(check_numbering(self.document, doc_type))

            if errors:
                report = "Проверка завершена.\nНайденные ошибки:\n" + "\n".join(errors)
            else:
                report = "Проверка завершена.\nОшибок не найдено!"
            self.ui.update_report(report)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обработать файл:\n{str(e)}")

    def export_report(self):
        text = self.ui.get_report_text()
        if not text or "Проверка завершена." not in text:
            messagebox.showwarning("Внимание", "Нет данных для экспорта!")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("TXT", "*.txt")])
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
                messagebox.showinfo("Успех", f"Отчёт сохранён:\n{path}")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def auto_fix(self):
        """Автоматическое исправление терминологии"""
        if self.document is None:
            messagebox.showwarning("Внимание", "Сначала загрузите документ и выполните проверку!")
            return

        try:
            replacements_count = auto_fix_terminology(self.document)

            if replacements_count > 0:
                messagebox.showinfo(
                    "Успех",
                    f"Выполнено замен: {replacements_count}\n"
                    f"Документ обновлен. Не забудьте сохранить исправленную версию."
                )
                # Обновляем отчет
                self.ui.update_report(f"Автоматическое исправление завершено.\nВыполнено замен: {replacements_count}")
            else:
                messagebox.showinfo("Информация", "Не найдено слов для автоматического исправления")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить автоматическое исправление:\n{str(e)}")

    def save_fixed(self):
        """Сохраняет исправленный документ"""
        if self.document is None:
            messagebox.showwarning("Внимание", "Нет загруженного документа!")
            return

        try:
            # Используем оригинальный путь или предлагаем выбрать
            if hasattr(self, 'current_file_path') and self.current_file_path:
                result = save_fixed_document(self.document, self.current_file_path)
                messagebox.showinfo("Успех", result)
            else:
                # Если путь не известен, предлагаем сохранить как
                path = filedialog.asksaveasfilename(
                    defaultextension=".docx",
                    filetypes=[("Word documents", "*.docx")]
                )
                if path:
                    self.document.save(path)
                    messagebox.showinfo("Успех", f"Документ сохранён: {path}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить документ:\n{str(e)}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = NormaTextApp()
    app.run()