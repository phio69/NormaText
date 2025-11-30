"""
Графический интерфейс NormaText на tkinter.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import List, Callable


class NormaTextUI:
    def __init__(self, root: tk.Tk, on_check: Callable, on_export: Callable, on_auto_fix: Callable, on_save: Callable):
        self.root = root
        self.root.title("NormaText — Проверка документов по ГОСТ Р 7.0.97-2016")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.file_path = ""
        self.on_check = on_check
        self.on_export = on_export
        self.on_auto_fix = on_auto_fix
        self.on_save = on_save

        self._create_widgets()

    def _create_widgets(self):
        # Загрузка файла
        upload_frame = ttk.LabelFrame(self.root, text="1. Загрузка документа", padding=10)
        upload_frame.pack(fill="x", padx=10, pady=5)
        self.file_label = ttk.Label(upload_frame, text="Файл не выбран")
        self.file_label.pack(side="left", padx=(0, 10))
        ttk.Button(upload_frame, text="Загрузить .docx-файл", command=self._load_file).pack(side="left")

        # Настройки
        settings_frame = ttk.LabelFrame(self.root, text="2. Настройки проверки", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(settings_frame, text="Тип документа:").grid(row=0, column=0, sticky="w")
        self.doc_type = tk.StringVar(value="приказ")
        doc_combo = ttk.Combobox(settings_frame, textvariable=self.doc_type,
                                 values=["приказ", "отчёт", "служебная записка"],
                                 state="readonly", width=25)
        doc_combo.grid(row=0, column=1, sticky="w", padx=(10, 0))

        ttk.Label(settings_frame, text="Категории:").grid(row=1, column=0, sticky="nw", pady=(10, 0))
        self.check_vars = {
            "структура": tk.BooleanVar(value=True),
            "терминология": tk.BooleanVar(value=True),
            "нумерация": tk.BooleanVar(value=True)
        }
        check_frame = ttk.Frame(settings_frame)
        check_frame.grid(row=1, column=1, sticky="w", pady=(10, 0))
        for i, (name, var) in enumerate(self.check_vars.items()):
            ttk.Checkbutton(check_frame, text=name.capitalize(), variable=var).grid(row=i, sticky="w")

        # Кнопка проверки
        run_frame = ttk.Frame(self.root)
        run_frame.pack(fill="x", padx=10, pady=10)
        ttk.Button(run_frame, text="Начать проверку", command=self._run_check).pack(side="right")

        # Отчёт
        report_frame = ttk.LabelFrame(self.root, text="3. Результаты проверки", padding=10)
        report_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.report_text = scrolledtext.ScrolledText(report_frame, wrap=tk.WORD, state="disabled", font=("Arial", 10))
        self.report_text.pack(fill="both", expand=True)

        # Кнопки действий
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(action_frame, text="Исправить автоматически", command=self.on_auto_fix).pack(side="left",
                                                                                                padx=(0, 5))
        ttk.Button(action_frame, text="Сохранить исправленный документ", command=self.on_save).pack(side="left",
                                                                                                    padx=(0, 5))
        ttk.Button(action_frame, text="Экспортировать отчёт в TXT", command=self.on_export).pack(side="left")

    def _load_file(self):
        path = filedialog.askopenfilename(title="Выберите .docx", filetypes=[("Word", "*.docx")])
        if path:
            self.file_path = path
            self.file_label.config(text=f"Загружен: {path.split('/')[-1]}")

    def _run_check(self):
        if not self.file_path:
            messagebox.showwarning("Внимание", "Сначала загрузите документ!")
            return
        selected = [k for k, v in self.check_vars.items() if v.get()]
        if not selected:
            messagebox.showwarning("Внимание", "Выберите категории проверки!")
            return
        self.on_check(self.file_path, self.doc_type.get(), selected)

    def update_report(self, text: str):
        self.report_text.config(state="normal")
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, text)
        self.report_text.config(state="disabled")

    def get_report_text(self) -> str:
        return self.report_text.get(1.0, tk.END).strip()