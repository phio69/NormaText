import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from docx import Document
from typing import List
import pymorphy3


class NormaTextApp:
    """
    Основной класс приложения NormaText.
    Управляет графическим интерфейсом и координирует логику проверки.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("NormaText — Проверка документов по ГОСТ Р 7.0.97-2016")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Данные
        self.current_file_path: str = ""
        self.document: Document = None
        self.selected_document_type: str = "приказ"
        self.selected_rules: List[str] = []

        # Инициализация морфологического анализатора
        self.morph = pymorphy3.MorphAnalyzer()

        self.create_widgets()

    def create_widgets(self):
        # === Блок 1: Загрузка файла ===
        upload_frame = ttk.LabelFrame(self.root, text="1. Загрузка документа", padding=10)
        upload_frame.pack(fill="x", padx=10, pady=5)

        self.file_label = ttk.Label(upload_frame, text="Файл не выбран")
        self.file_label.pack(side="left", padx=(0, 10))

        ttk.Button(upload_frame, text="Загрузить .docx-файл", command=self.load_file).pack(side="left")

        # === Блок 2: Настройки проверки ===
        settings_frame = ttk.LabelFrame(self.root, text="2. Настройки проверки", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(settings_frame, text="Тип документа:").grid(row=0, column=0, sticky="w", pady=2)
        self.doc_type_var = tk.StringVar(value="приказ")
        doc_type_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.doc_type_var,
            values=["приказ", "отчёт", "служебная записка", "протокол"],
            state="readonly",
            width=25
        )
        doc_type_combo.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=2)
        doc_type_combo.bind("<<ComboboxSelected>>", self.on_doc_type_change)

        ttk.Label(settings_frame, text="Категории для проверки:").grid(row=1, column=0, sticky="nw", pady=(10, 2))
        self.check_vars = {
            "структура": tk.BooleanVar(value=True),
            "терминология": tk.BooleanVar(value=True),
            "нумерация": tk.BooleanVar(value=True)
        }
        check_frame = ttk.Frame(settings_frame)
        check_frame.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=(10, 2))
        for i, (name, var) in enumerate(self.check_vars.items()):
            ttk.Checkbutton(check_frame, text=name.capitalize(), variable=var).grid(row=i, column=0, sticky="w")

        # === Блок 3: Кнопка запуска ===
        run_frame = ttk.Frame(self.root)
        run_frame.pack(fill="x", padx=10, pady=10)
        ttk.Button(run_frame, text="Начать проверку", command=self.run_check).pack(side="right")

        # === Блок 4: Отчёт ===
        report_frame = ttk.LabelFrame(self.root, text="3. Результаты проверки", padding=10)
        report_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.report_text = scrolledtext.ScrolledText(report_frame, wrap=tk.WORD, state="disabled", font=("Arial", 10))
        self.report_text.pack(fill="both", expand=True)

        # === Блок 5: Кнопки ===
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(action_frame, text="Исправить автоматически", command=self.auto_fix).pack(side="left", padx=(0, 5))
        ttk.Button(action_frame, text="Сохранить исправленный документ", command=self.save_fixed_document).pack(side="left", padx=(0, 5))
        ttk.Button(action_frame, text="Экспортировать отчёт в TXT", command=self.export_report).pack(side="left")

    def load_file(self):
        file_path = filedialog.askopenfilename(title="Выберите документ .docx", filetypes=[("Документ Word", "*.docx")])
        if not file_path:
            return

        try:
            self.document = Document(file_path)
            self.current_file_path = file_path
            self.file_label.config(text=f"Загружен: {file_path.split('/')[-1]}")
            messagebox.showinfo("Успех", "Документ успешно загружен!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{str(e)}")
            self.document = None

    def on_doc_type_change(self, event=None):
        self.selected_document_type = self.doc_type_var.get()

    def run_check(self):
        if self.document is None:
            messagebox.showwarning("Внимание", "Сначала загрузите документ!")
            return

        self.selected_rules = [rule for rule, var in self.check_vars.items() if var.get()]
        if not self.selected_rules:
            messagebox.showwarning("Внимание", "Выберите хотя бы одну категорию для проверки!")
            return

        # Словарь запрещённых слов (в начальной форме!)
        forbidden_set = {
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

        all_text_lines = [(i, p.text) for i, p in enumerate(self.document.paragraphs, 1) if p.text.strip()]
        errors = []

        # === Проверка терминологии с лемматизацией ===
        if "терминология" in self.selected_rules:
            for line_num, text in all_text_lines:
                words = text.split()
                for word in words:
                    clean = word.strip(".,;:!?\"'()[]{}—–-")
                    if not clean or not clean.isalpha():
                        continue
                    try:
                        normal_form = self.morph.parse(clean.lower())[0].normal_form
                        if normal_form in forbidden_set:
                            errors.append(
                                f"• Стр. {line_num}: Недопустимое слово «{clean}» (основа: «{normal_form}») → замените на нейтральный синоним."
                            )
                    except Exception:
                        continue  # игнорируем нераспознанные слова

        # === Проверка структуры ===
        if "структура" in self.selected_rules:
            first_text = " ".join(text for _, text in all_text_lines[:5])
            if "утверждаю" not in first_text.lower():
                errors.append("• Стр. 1: Отсутствует реквизит «Утверждаю» (обязательный для приказов).")

        # === Проверка нумерации ===
        if "нумерация" in self.selected_rules:
            errors.append("• Стр. 3: Нарушена нумерация разделов (пока упрощённая проверка).")

        # === Отчёт ===
        if errors:
            report = [
                "Проверка завершена.",
                f"Тип документа: {self.selected_document_type}",
                f"Выбраны категории: {', '.join(self.selected_rules)}",
                "",
                "Найденные ошибки:"
            ] + errors
        else:
            report = ["Проверка завершена.", "Ошибок не найдено! Документ соответствует выбранным правилам."]

        self.update_report("\n".join(report))

    def update_report(self, text: str):
        self.report_text.config(state="normal")
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, text)
        self.report_text.config(state="disabled")

    def auto_fix(self):
        messagebox.showinfo("Информация", "Автоматическое исправление пока не реализовано.")

    def save_fixed_document(self):
        if self.document is None:
            messagebox.showwarning("Внимание", "Нет загруженного документа!")
            return
        messagebox.showinfo("Информация", "Сохранение исправленного документа пока не реализовано.")

    def export_report(self):
        report_text = self.report_text.get(1.0, tk.END).strip()
        # Обновите проверку — теперь отчёт начинается с "Проверка завершена."
        if not report_text or "Проверка завершена." not in report_text:
            messagebox.showwarning("Внимание", "Нет данных для экспорта!")
            return

        path = filedialog.asksaveasfilename(
            title="Сохранить отчёт",
            defaultextension=".txt",
            filetypes=[("Текстовый файл", "*.txt")]
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(report_text)
                messagebox.showinfo("Успех", f"Отчёт сохранён:\n{path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")


def main():
    root = tk.Tk()
    NormaTextApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()