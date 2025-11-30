"""
Точка входа в NormaText.
"""

import tkinter as tk
from ui import NormaTextUI
from core import load_document, check_terminology, check_structure, check_numbering
from tkinter import messagebox, filedialog

class NormaTextApp:
    def __init__(self):
        self.root = tk.Tk()
        self.document = None
        self.ui = NormaTextUI(
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
                errors.extend(check_structure(self.document, doc_type))
            if "нумерация" in rules:
                # ПЕРЕДАЕМ doc_type в check_numbering
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
        messagebox.showinfo("Информация", "Автоматическое исправление пока не реализовано.")

    def save_fixed(self):
        if self.document is None:
            messagebox.showwarning("Внимание", "Нет загруженного документа!")
            return
        messagebox.showinfo("Информация", "Сохранение исправленного документа пока не реализовано.")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = NormaTextApp()
    app.run()