"""
Современный графический интерфейс NormaText с трехэтапным процессом
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import List, Callable, Optional
from pathlib import Path

class ModernNormaTextUI:
    def __init__(self, root: tk.Tk, on_check: Callable, on_export: Callable, on_auto_fix: Callable, on_save: Callable):
        self.root = root
        self.root.title("NormaText")
        self.root.geometry("1200x700")
        self.root.configure(bg="#F8F7F5")
        self.root.resizable(False, False)

        # Цветовая схема из дизайн-системы
        self.colors = {
            "background_light": "#F8F7F5",
            "background_blue": "#4A7BFF",
            "text_white": "#FFFFFF",
            "text_dark": "#1C1C1E",
            "card_bg": "#FFFFFF",
            "border_blue": "#4A7BFF"
        }

        self.file_path = ""
        self.selected_rules = []
        self.doc_type = "приказ"

        self.on_check = on_check
        self.on_export = on_export
        self.on_auto_fix = on_auto_fix
        self.on_save = on_save

        # Создаем контейнер для всех экранов
        self.container = tk.Frame(self.root, bg=self.colors["background_light"])
        self.container.pack(fill="both", expand=True)

        self.current_screen = None
        self._create_screen1()  # Начинаем с первого экрана

    def _create_screen1(self):
        """Первый экран - загрузка файла"""
        if self.current_screen:
            self.current_screen.destroy()

        self.current_screen = tk.Frame(self.container, bg=self.colors["background_light"])
        self.current_screen.pack(fill="both", expand=True)

        # Боковая панель - синяя на всю высоту
        sidebar = tk.Frame(self.current_screen, bg=self.colors["background_blue"], width=350)
        sidebar.pack(side="left", fill="both", expand=False)
        sidebar.pack_propagate(False)

        # Заголовок в боковой панели
        title_label = tk.Label(sidebar, text="NormaText", font=("Inter", 36, "bold"),
                               bg=self.colors["background_blue"], fg=self.colors["text_white"])
        title_label.pack(pady=(80, 30), padx=40, anchor="w")

        # Описание в боковой панели
        description_text = (
            "Это простой, бесплатный и полностью автономный инструмент, "
            "который помогает привести документы в соответствие с требованиями ГОСТ. "
            "Загрузите docx-файл, получите отчёт об ошибках в терминологии, структуре "
            "или нумерации — и исправьте их за пару кликов."
        )
        description_label = tk.Label(sidebar, text=description_text, font=("Inter", 18),
                                     bg=self.colors["background_blue"], fg=self.colors["text_white"],
                                     wraplength=270, justify="left")
        description_label.pack(pady=20, padx=40, anchor="w")

        # Основная область - белая на всю высоту
        main_area = tk.Frame(self.current_screen, bg=self.colors["background_light"])
        main_area.pack(side="left", fill="both", expand=True)

        # Контент в основной области
        content_frame = tk.Frame(main_area, bg=self.colors["background_light"])
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Функция для создания круглых прямоугольников
        def round_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
            points = [x1 + radius, y1,
                      x2 - radius, y1,
                      x2, y1,
                      x2, y1 + radius,
                      x2, y2 - radius,
                      x2, y2,
                      x2 - radius, y2,
                      x1 + radius, y2,
                      x1, y2,
                      x1, y2 - radius,
                      x1, y1 + radius,
                      x1, y1]
            return canvas.create_polygon(points, smooth=True, **kwargs)

        # Кнопка загрузки файла через Canvas
        upload_frame = tk.Frame(content_frame, bg=self.colors["background_light"])
        upload_frame.pack(pady=(0, 20))

        upload_canvas = tk.Canvas(upload_frame, width=350, height=70,
                                  bg=self.colors["background_light"], highlightthickness=0)
        upload_canvas.pack()

        # Рисуем кнопку загрузки
        upload_bg = round_rectangle(upload_canvas, 0, 0, 350, 70, radius=18,
                                    fill="#E5E8EF", outline="#E5E8EF")
        upload_text = upload_canvas.create_text(175, 35, text="Загрузите docx-файл",
                                                fill=self.colors["background_blue"],
                                                font=("Inter", 24))

        def on_upload_click(event):
            self._load_file_step1()

        def on_upload_enter(event):
            upload_canvas.configure(cursor="hand2")
            upload_canvas.itemconfig(upload_bg, fill="#E5E8EF")

        def on_upload_leave(event):
            upload_canvas.configure(cursor="")
            upload_canvas.itemconfig(upload_bg, fill="#E5E8EF")

        upload_canvas.bind("<Button-1>", on_upload_click)
        upload_canvas.bind("<Enter>", on_upload_enter)
        upload_canvas.bind("<Leave>", on_upload_leave)

        # Информация о выбранном файле
        self.file_info = tk.Label(content_frame, text="", font=("Inter", 10),
                                  bg=self.colors["background_light"], fg=self.colors["text_dark"])
        self.file_info.pack(pady=(0, 20))

        # Кнопка Далее через Canvas
        self.next_frame = tk.Frame(content_frame, bg=self.colors["background_light"])
        self.next_frame.pack()

        self.next_canvas = tk.Canvas(self.next_frame, width=150, height=46,
                                     bg=self.colors["background_light"], highlightthickness=0)
        self.next_canvas.pack()

        # Функция для отрисовки кнопки Далее
        def draw_next_button(enabled=True):
            self.next_canvas.delete("all")

            bg_color = self.colors["background_blue"] if enabled else "#4A7BFF"
            text_color = self.colors["text_white"] if enabled else "#FFFFFF"

            # Рисуем закругленную кнопку
            next_bg = round_rectangle(self.next_canvas, 0, 0, 150, 46, radius=25,
                                      fill=bg_color, outline=bg_color)
            next_text = self.next_canvas.create_text(75, 23, text="Далее",
                                                     fill=text_color,
                                                     font=("Inter", 12, "bold"))

            if enabled:
                def on_next_click(event):
                    self._create_screen2()

                def on_next_enter(event):
                    self.next_canvas.configure(cursor="hand2")
                    if enabled:
                        self.next_canvas.itemconfig(next_bg, fill="#3A6BEE")

                def on_next_leave(event):
                    self.next_canvas.configure(cursor="")
                    if enabled:
                        self.next_canvas.itemconfig(next_bg, fill=bg_color)

                self.next_canvas.bind("<Button-1>", on_next_click)
                self.next_canvas.bind("<Enter>", on_next_enter)
                self.next_canvas.bind("<Leave>", on_next_leave)
            else:
                self.next_canvas.unbind("<Button-1>")
                self.next_canvas.unbind("<Enter>")
                self.next_canvas.unbind("<Leave>")

        # Изначально кнопка отключена
        draw_next_button(False)
        self.draw_next_button = draw_next_button

    def _load_file_step1(self):
        """Загрузка файла на первом экране"""
        path = filedialog.askopenfilename(title="Выберите .docx",
                                          filetypes=[("Word", "*.docx")])
        if path:
            self.file_path = path
            file_name = Path(path).name
            self.file_info.config(text=f"Выбран файл: {file_name}")
            # Включаем кнопку Далее
            if hasattr(self, 'draw_next_button'):
                self.draw_next_button(True)

    def _create_screen2(self):
        """Второй экран - выбор параметров проверки"""
        if self.current_screen:
            self.current_screen.destroy()

        self.current_screen = tk.Frame(self.container, bg=self.colors["background_light"])
        self.current_screen.pack(fill="both", expand=True)

        # Боковая панель - синяя на всю высоту
        sidebar = tk.Frame(self.current_screen, bg=self.colors["background_blue"], width=350)
        sidebar.pack(side="left", fill="both", expand=False)
        sidebar.pack_propagate(False)

        title_label = tk.Label(sidebar, text="NormaText", font=("Inter", 36, "bold"),
                               bg=self.colors["background_blue"], fg=self.colors["text_white"])
        title_label.pack(pady=(80, 30), padx=40, anchor="w")

        # Описание
        description_text = (
            "Выберите параметры проверки документа. "
            "Укажите тип документа и категории проверки для точного анализа."
        )
        description_label = tk.Label(sidebar, text=description_text, font=("Inter", 18),
                                     bg=self.colors["background_blue"], fg=self.colors["text_white"],
                                     wraplength=270, justify="left")
        description_label.pack(pady=20, padx=40, anchor="w")

        # Основная область
        main_area = tk.Frame(self.current_screen, bg=self.colors["background_light"])
        main_area.pack(side="left", fill="both", expand=True)

        # Контент
        content_frame = tk.Frame(main_area, bg=self.colors["background_light"])
        content_frame.place(relx=0.5, rely=0.4, anchor="center")

        # Заголовок
        screen_title = tk.Label(content_frame, text="Настройка проверки",
                                font=("Inter", 28, "bold"),
                                bg=self.colors["background_light"],
                                fg=self.colors["text_dark"])
        screen_title.pack(pady=(0, 40), anchor="w")

        # Тип документа
        doc_type_frame = tk.Frame(content_frame, bg=self.colors["background_light"])
        doc_type_frame.pack(fill="x", pady=(0, 30))

        doc_type_label = tk.Label(doc_type_frame, text="Тип документа:",
                                  font=("Inter", 18),
                                  bg=self.colors["background_light"], fg=self.colors["text_dark"])
        doc_type_label.pack(anchor="w")

        self.doc_type_var = tk.StringVar(value="приказ")
        doc_combo = ttk.Combobox(doc_type_frame, textvariable=self.doc_type_var,
                                 values=["приказ", "отчёт", "служебная записка"],
                                 state="readonly",
                                 font=("Inter", 16),
                                 height=5)
        doc_combo.pack(fill="x", pady=(10, 0))

        # Категории проверки
        rules_frame = tk.Frame(content_frame, bg=self.colors["background_light"])
        rules_frame.pack(fill="x", pady=(0, 40))

        rules_label = tk.Label(rules_frame, text="Категории проверки:",
                               font=("Inter", 18),
                               bg=self.colors["background_light"], fg=self.colors["text_dark"])
        rules_label.pack(anchor="w")

        self.check_vars = {
            "терминология": tk.BooleanVar(value=True),
            "структура": tk.BooleanVar(value=True),
            "нумерация": tk.BooleanVar(value=True)
        }

        check_frame = tk.Frame(rules_frame, bg=self.colors["background_light"])
        check_frame.pack(fill="x", pady=(10, 0))

        for name, var in self.check_vars.items():
            chk = tk.Checkbutton(check_frame, text=name.capitalize(),
                                 variable=var,
                                 font=("Inter", 16),
                                 bg=self.colors["background_light"],
                                 fg=self.colors["text_dark"],
                                 selectcolor=self.colors["background_light"])
            chk.pack(anchor="w", pady=5)

        # Кнопка запуска проверки
        def round_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
            points = [x1 + radius, y1,
                      x2 - radius, y1,
                      x2, y1,
                      x2, y1 + radius,
                      x2, y2 - radius,
                      x2, y2,
                      x2 - radius, y2,
                      x1 + radius, y2,
                      x1, y2,
                      x1, y2 - radius,
                      x1, y1 + radius,
                      x1, y1]
            return canvas.create_polygon(points, smooth=True, **kwargs)

        # Фрейм для кнопок
        buttons_frame = tk.Frame(content_frame, bg=self.colors["background_light"])
        buttons_frame.pack(pady=(20, 0))

        # Кнопка "Назад"
        back_frame = tk.Frame(buttons_frame, bg=self.colors["background_light"])
        back_frame.pack(side="left", padx=(0, 20))

        back_canvas = tk.Canvas(back_frame, width=150, height=46,
                                bg=self.colors["background_light"], highlightthickness=0)
        back_canvas.pack()

        back_bg = round_rectangle(back_canvas, 0, 0, 150, 46, radius=25,
                                  fill="#E5E8EF", outline="#E5E8EF")
        back_text = back_canvas.create_text(75, 23, text="Назад",
                                            fill=self.colors["background_blue"],
                                            font=("Inter", 12, "bold"))

        def on_back_click(event):
            self._create_screen1()

        def on_back_enter(event):
            back_canvas.configure(cursor="hand2")
            back_canvas.itemconfig(back_bg, fill="#D5D8DF")

        def on_back_leave(event):
            back_canvas.configure(cursor="")
            back_canvas.itemconfig(back_bg, fill="#E5E8EF")

        back_canvas.bind("<Button-1>", on_back_click)
        back_canvas.bind("<Enter>", on_back_enter)
        back_canvas.bind("<Leave>", on_back_leave)

        # Кнопка "Запустить проверку"
        check_frame = tk.Frame(buttons_frame, bg=self.colors["background_light"])
        check_frame.pack(side="left")

        check_canvas = tk.Canvas(check_frame, width=200, height=46,
                                 bg=self.colors["background_light"], highlightthickness=0)
        check_canvas.pack()

        check_bg = round_rectangle(check_canvas, 0, 0, 200, 46, radius=25,
                                   fill=self.colors["background_blue"],
                                   outline=self.colors["background_blue"])
        check_text = check_canvas.create_text(100, 23, text="Запустить проверку",
                                              fill=self.colors["text_white"],
                                              font=("Inter", 12, "bold"))

        def on_check_click(event):
            self._run_check_and_show_results()

        def on_check_enter(event):
            check_canvas.configure(cursor="hand2")
            check_canvas.itemconfig(check_bg, fill="#3A6BEE")

        def on_check_leave(event):
            check_canvas.configure(cursor="")
            check_canvas.itemconfig(check_bg, fill=self.colors["background_blue"])

        check_canvas.bind("<Button-1>", on_check_click)
        check_canvas.bind("<Enter>", on_check_enter)
        check_canvas.bind("<Leave>", on_check_leave)

    def _create_screen3(self, errors: List[str]):
        """Третий экран - результаты проверки"""

        self.current_errors = errors

        if self.current_screen:
            self.current_screen.destroy()

        self.current_screen = tk.Frame(self.container, bg=self.colors["background_light"])
        self.current_screen.pack(fill="both", expand=True)

        # Боковая панель - синяя на всю высоту
        sidebar = tk.Frame(self.current_screen, bg=self.colors["background_blue"], width=350)
        sidebar.pack(side="left", fill="both", expand=False)
        sidebar.pack_propagate(False)

        title_label = tk.Label(sidebar, text="NormaText", font=("Inter", 36, "bold"),
                               bg=self.colors["background_blue"], fg=self.colors["text_white"])
        title_label.pack(pady=(80, 30), padx=40, anchor="w")

        # Описание
        description_text = (
            "Просмотрите результаты проверки документа. "
            "Вы можете исправить ошибки автоматически или сохранить отчет."
        )
        description_label = tk.Label(sidebar, text=description_text, font=("Inter", 18),
                                     bg=self.colors["background_blue"], fg=self.colors["text_white"],
                                     wraplength=270, justify="left")
        description_label.pack(pady=20, padx=40, anchor="w")

        # Основная область
        main_area = tk.Frame(self.current_screen, bg=self.colors["background_light"])
        main_area.pack(side="left", fill="both", expand=True)

        # Главный контейнер с прокруткой
        main_container = tk.Frame(main_area, bg=self.colors["background_light"])
        main_container.pack(fill="both", expand=True, padx=40, pady=20)

        # Заголовок
        screen_title = tk.Label(main_container, text="Результаты проверки",
                                font=("Inter", 28, "bold"),
                                bg=self.colors["background_light"],
                                fg=self.colors["text_dark"])
        screen_title.pack(pady=(0, 20), anchor="w")

        # Область для результатов с прокруткой
        results_container = tk.Frame(main_container, bg=self.colors["background_light"])
        results_container.pack(fill="both", expand=True, pady=(0, 20))

        # Создаем Scrollbar и Text вручную для лучшего контроля
        scrollbar = tk.Scrollbar(results_container)
        scrollbar.pack(side="right", fill="y")

        self.results_text = tk.Text(results_container,
                                    wrap=tk.WORD,
                                    font=("Inter", 14),
                                    bg=self.colors["card_bg"],
                                    fg=self.colors["text_dark"],
                                    relief="flat",
                                    borderwidth=0,
                                    padx=20,
                                    pady=20,
                                    yscrollcommand=scrollbar.set)
        self.results_text.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=self.results_text.yview)

        # Вставляем текст
        if errors:
            report = "Проверка завершена.\n\nНайденные ошибки:\n" + "\n".join(errors)
        else:
            report = "Проверка завершена.\n\nОшибок не найдено!"

        self.results_text.insert(tk.END, report)
        self.results_text.config(state="disabled")

        # Функция для круглых кнопок
        def round_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
            points = [x1 + radius, y1,
                      x2 - radius, y1,
                      x2, y1,
                      x2, y1 + radius,
                      x2, y2 - radius,
                      x2, y2,
                      x2 - radius, y2,
                      x1 + radius, y2,
                      x1, y2,
                      x1, y2 - radius,
                      x1, y1 + radius,
                      x1, y1]
            return canvas.create_polygon(points, smooth=True, **kwargs)

        # Кнопки действий - ОТДЕЛЬНЫЙ ФРЕЙМ ВНИЗУ
        actions_frame = tk.Frame(main_container, bg=self.colors["background_light"])
        actions_frame.pack(fill="x", pady=(10, 0))

        buttons_config = [
            ("Исправить автоматически", self.on_auto_fix),
            ("Скачать исправленный", self.on_save),
            ("Экспортировать ошибки в TXT", self.on_export)
        ]

        for text, command in buttons_config:
            btn_frame = tk.Frame(actions_frame, bg=self.colors["background_light"])
            btn_frame.pack(side="left", padx=(0, 15))

            canvas = tk.Canvas(btn_frame, width=220, height=46,
                               bg=self.colors["background_light"], highlightthickness=0)
            canvas.pack()

            bg = round_rectangle(canvas, 0, 0, 220, 46, radius=25,
                                 fill=self.colors["background_blue"],
                                 outline=self.colors["background_blue"])
            canvas.create_text(110, 23, text=text,
                               fill=self.colors["text_white"],
                               font=("Inter", 12, "bold"))

            def create_handler(cmd):
                def handler(event):
                    cmd()

                return handler

            def on_enter(event, bg_item=bg):
                canvas.configure(cursor="hand2")
                canvas.itemconfig(bg_item, fill="#3A6BEE")

            def on_leave(event, bg_item=bg):
                canvas.configure(cursor="")
                canvas.itemconfig(bg_item, fill=self.colors["background_blue"])

            canvas.bind("<Button-1>", create_handler(command))
            canvas.bind("<Enter>", on_enter)
            canvas.bind("<Leave>", on_leave)

        # Кнопка "Проверить другой документ" - ТОЖЕ В ОТДЕЛЬНОМ ФРЕЙМЕ
        back_frame = tk.Frame(main_container, bg=self.colors["background_light"])
        back_frame.pack(fill="x", pady=(20, 0))

        back_canvas = tk.Canvas(back_frame, width=250, height=46,
                                bg=self.colors["background_light"], highlightthickness=0)
        back_canvas.pack(anchor="w")  # выравниваем по левому краю

        back_bg = round_rectangle(back_canvas, 0, 0, 250, 46, radius=25,
                                  fill="#E5E8EF", outline="#E5E8EF")
        back_text = back_canvas.create_text(125, 23, text="Проверить другой документ",
                                            fill=self.colors["background_blue"],
                                            font=("Inter", 12, "bold"))

        def on_back_click(event):
            self._create_screen1()

        def on_back_enter(event):
            back_canvas.configure(cursor="hand2")
            back_canvas.itemconfig(back_bg, fill="#D5D8DF")

        def on_back_leave(event):
            back_canvas.configure(cursor="")
            back_canvas.itemconfig(back_bg, fill="#E5E8EF")

        back_canvas.bind("<Button-1>", on_back_click)
        back_canvas.bind("<Enter>", on_back_enter)
        back_canvas.bind("<Leave>", on_back_leave)

    def _run_check_and_show_results(self):
        """Запуск проверки и переход к результатам"""
        if not self.file_path:
            messagebox.showwarning("Внимание", "Сначала загрузите документ!")
            return

        selected_rules = [k for k, v in self.check_vars.items() if v.get()]
        if not selected_rules:
            messagebox.showwarning("Внимание", "Выберите категории проверки!")
            return

        try:
            # Вызываем основную функцию проверки
            self.on_check(self.file_path, self.doc_type_var.get(), selected_rules)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обработать файл:\n{str(e)}")

    def update_report(self, errors: List[str]):
        """Обновляет отчет с ошибками (вызывается из main.py)"""
        # Просто переходим на 3й экран с переданным списком ошибок
        self._create_screen3(errors)

    def get_report_text(self) -> str:
        """Возвращает текст отчета"""
        if hasattr(self, 'results_text'):
            return self.results_text.get(1.0, tk.END).strip()
        return ""