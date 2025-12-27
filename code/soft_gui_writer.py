# gui.py - Графический интерфейс приложения
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import ImageTk, Image
import os
from datetime import datetime
from logic_writer import ProfileManager

class TemplateManagerWindow:
    def __init__(self, parent, profile_manager, on_template_change_callback):
        self.parent = parent
        self.profile_manager = profile_manager
        self.on_template_change_callback = on_template_change_callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("Управление стилями")
        self.window.geometry("1000x600")
        self.window.resizable(False, False)
        
        # Переменные для шаблонов
        self.current_pattern = tk.StringVar(value=self.profile_manager.current_template.get("pattern", ""))
        self.current_font = tk.StringVar(value=self.profile_manager.current_template.get("font", "arial.ttf"))
        self.current_data_font = tk.StringVar(value=self.profile_manager.current_template.get("data_font", "arial.ttf"))
        self.template_name = tk.StringVar(value="По умолчанию")
        self.convert_photo_to_bw = tk.BooleanVar(value=self.profile_manager.current_template.get("convert_photo_to_bw", True))
        self.convert_pattern_to_bw = tk.BooleanVar(value=self.profile_manager.current_template.get("convert_pattern_to_bw", False))
        
        # Переменные для размеров шрифтов (только обычные)
        self.font_size_normal = tk.IntVar(value=self.profile_manager.current_template.get("font_size_normal", 18))
        self.data_font_size_normal = tk.IntVar(value=self.profile_manager.current_template.get("data_font_size_normal", 16))
        
        self.setup_ui()
        self.update_templates_list()
    
    def setup_ui(self):
        """Настраивает интерфейс окна управления стилями"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Управление стилями", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Левая панель - список шаблонов
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        ttk.Label(left_frame, text="Сохраненные стили:").pack(anchor='w', pady=5)
        
        listbox_frame = ttk.Frame(left_frame)
        listbox_frame.pack(fill='both', expand=True, pady=5)
        
        self.templates_listbox = tk.Listbox(listbox_frame, height=10)
        self.templates_listbox.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame, command=self.templates_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.templates_listbox.config(yscrollcommand=scrollbar.set)
        
        # Кнопки управления шаблонами
        template_buttons_frame = ttk.Frame(left_frame)
        template_buttons_frame.pack(fill='x', pady=10)
        
        ttk.Button(template_buttons_frame, text="Загрузить стиль",
                  command=self.load_selected_template).pack(side='left', padx=5)
        ttk.Button(template_buttons_frame, text="Удалить стиль",
                  command=self.delete_selected_template).pack(side='left', padx=5)
        
        # Правая панель - создание/редактирование шаблона
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        ttk.Label(right_frame, text="Создание/Редактирование стиля", font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Создаем скроллируемую область для формы
        canvas = tk.Canvas(right_frame)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        form_frame = ttk.Frame(scrollable_frame)
        form_frame.pack(fill='x', pady=10)
        
        ttk.Label(form_frame, text="Название стиля:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        ttk.Entry(form_frame, textvariable=self.template_name, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Паттерн - только метка и кнопка обзора
        ttk.Label(form_frame, text="Паттерн:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.pattern_label = ttk.Label(form_frame, text=os.path.basename(self.current_pattern.get()), wraplength=200)
        self.pattern_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(form_frame, text="Обзор", command=self.browse_pattern).grid(row=1, column=2, padx=5, pady=5)
        
        # Шрифты для заголовков - только метка и кнопка обзора
        ttk.Label(form_frame, text="Шрифт заголовков:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.font_label = ttk.Label(form_frame, text=os.path.basename(self.current_font.get()), wraplength=200)
        self.font_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(form_frame, text="Обзор", command=self.browse_font).grid(row=2, column=2, padx=5, pady=5)
        
        # Шрифты для данных - только метка и кнопка обзора
        ttk.Label(form_frame, text="Шрифт данных:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.data_font_label = ttk.Label(form_frame, text=os.path.basename(self.current_data_font.get()), wraplength=200)
        self.data_font_label.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(form_frame, text="Обзор", command=self.browse_data_font).grid(row=3, column=2, padx=5, pady=5)
        
        # Только обычные размеры шрифтов
        ttk.Label(form_frame, text="Размеры шрифтов:", font=('Arial', 10, 'bold')).grid(row=4, column=0, columnspan=3, sticky="w", padx=5, pady=10)
        
        ttk.Label(form_frame, text="Обычный (заголовки):").grid(row=5, column=0, sticky="w", padx=5, pady=2)
        ttk.Spinbox(form_frame, from_=10, to=40, textvariable=self.font_size_normal, width=10).grid(row=5, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Обычный (данные):").grid(row=6, column=0, sticky="w", padx=5, pady=2)
        ttk.Spinbox(form_frame, from_=10, to=40, textvariable=self.data_font_size_normal, width=10).grid(row=6, column=1, padx=5, pady=2)
        
        # Галочки для конвертации
        ttk.Checkbutton(form_frame, text="Конвертировать фото в Ч/Б", 
                       variable=self.convert_photo_to_bw).grid(row=7, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        ttk.Checkbutton(form_frame, text="Конвертировать паттерн в Ч/Б", 
                       variable=self.convert_pattern_to_bw).grid(row=8, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопка сохранения в правом нижнем углу
        ttk.Button(right_frame, text="Сохранить стиль", command=self.save_template).pack(side='bottom', pady=10)
    
    def browse_pattern(self):
        """Открывает диалог выбора паттерна"""
        initial_dir = self.profile_manager.get_full_path("pattern")
        filename = filedialog.askopenfilename(
            initialdir=initial_dir,
            filetypes=[("Image files", "*.bmp *.jpg *.jpeg *.png")]
        )
        if filename:
            self.current_pattern.set(filename)
            self.pattern_label.config(text=os.path.basename(filename))
    
    def browse_font(self):
        """Открывает диалог выбора шрифта"""
        filename = filedialog.askopenfilename(filetypes=[("Font files", "*.ttf *.otf")])
        if filename:
            self.current_font.set(filename)
            self.font_label.config(text=os.path.basename(filename))
    
    def browse_data_font(self):
        """Открывает диалог выбора шрифта для данных"""
        filename = filedialog.askopenfilename(filetypes=[("Font files", "*.ttf *.otf")])
        if filename:
            self.current_data_font.set(filename)
            self.data_font_label.config(text=os.path.basename(filename))
    
    def update_templates_list(self):
        """Обновляет список стилей"""
        self.templates_listbox.delete(0, tk.END)
        template_names = self.profile_manager.get_template_names()
        for name in template_names:
            self.templates_listbox.insert(tk.END, name)
    
    def load_selected_template(self):
        """Загружает выбранный стиль"""
        selection = self.templates_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите стиль для загрузки")
            return
        
        selected_index = selection[0]
        template_names = self.profile_manager.get_template_names()
        if selected_index < len(template_names):
            template_name = template_names[selected_index]
            template = self.profile_manager.load_template(template_name)
            if template:
                self.template_name.set(template.get("name", ""))
                self.current_pattern.set(template.get("pattern", ""))
                self.current_font.set(template.get("font", "arial.ttf"))
                self.current_data_font.set(template.get("data_font", "arial.ttf"))
                self.convert_photo_to_bw.set(template.get("convert_photo_to_bw", True))
                self.convert_pattern_to_bw.set(template.get("convert_pattern_to_bw", False))
                
                # Обновляем метки с именами файлов
                self.pattern_label.config(text=os.path.basename(template.get("pattern", "")))
                self.font_label.config(text=os.path.basename(template.get("font", "arial.ttf")))
                self.data_font_label.config(text=os.path.basename(template.get("data_font", "arial.ttf")))
                
                # Загружаем размеры шрифтов (только обычные)
                self.font_size_normal.set(template.get("font_size_normal", 18))
                self.data_font_size_normal.set(template.get("data_font_size_normal", 16))
                
                self.profile_manager.set_current_template(template)
                
                # Немедленно обновляем основной интерфейс
                self.on_template_change_callback()
                
                messagebox.showinfo("Успех", f"Стиль '{template_name}' загружен")
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить стиль")
    
    def delete_selected_template(self):
        """Удаляет выбранный стиль"""
        selection = self.templates_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите стиль для удаления")
            return
        
        selected_index = selection[0]
        template_names = self.profile_manager.get_template_names()
        if selected_index < len(template_names):
            template_name = template_names[selected_index]
            result = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить стиль '{template_name}'?")
            if result:
                if self.profile_manager.delete_template(template_name):
                    self.update_templates_list()
                    messagebox.showinfo("Успех", f"Стиль '{template_name}' удален")
                else:
                    messagebox.showerror("Ошибка", "Не удалось удалить стиль")
    
    def save_template(self):
        """Сохраняет текущие настройки как стиль"""
        if not self.template_name.get():
            messagebox.showwarning("Предупреждение", "Введите название стиля")
            return
        
        try:
            self.profile_manager.save_template(
                name=self.template_name.get(),
                pattern=self.current_pattern.get(),
                font=self.current_font.get(),
                data_font=self.current_data_font.get(),
                font_size_normal=self.font_size_normal.get(),
                data_font_size_normal=self.data_font_size_normal.get(),
                convert_photo_to_bw=self.convert_photo_to_bw.get(),
                convert_pattern_to_bw=self.convert_pattern_to_bw.get()
            )
            self.update_templates_list()
            
            # Если сохраненный шаблон является текущим, обновляем интерфейс
            current_template = self.profile_manager.get_current_template()
            if current_template.get("name") == self.template_name.get():
                self.on_template_change_callback()
            
            messagebox.showinfo("Успех", f"Стиль '{self.template_name.get()}' сохранен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить стиль: {str(e)}")


class PlaceholderEntry(ttk.Entry):
    def __init__(self, master=None, placeholder="", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = 'gray'
        self.default_fg_color = self.cget('foreground')
        
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._set_placeholder)
        
        self._set_placeholder()
    
    def _clear_placeholder(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(foreground=self.default_fg_color)
    
    def _set_placeholder(self, event=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(foreground=self.placeholder_color)
    
    def get(self):
        content = super().get()
        if content == self.placeholder:
            return ""
        return content


class UserProfileApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система управления профилями пользователей")
        self.root.geometry("900x700")
        
        # Инициализация менеджера профилей
        self.profile_manager = ProfileManager()
        
        # Переменные для хранения данных
        self.photo_path = tk.StringVar()
        self.full_name = tk.StringVar()
        self.organization = tk.StringVar()
        self.department = tk.StringVar()
        self.expiration_date = tk.StringVar()
        
        self.admin_search_term = tk.StringVar()
        
        # Переменная для выбора шаблона
        self.selected_template = tk.StringVar(value="По умолчанию")
        
        # Галочки для конвертации
        self.convert_photo_to_bw = tk.BooleanVar(value=True)
        self.convert_pattern_to_bw = tk.BooleanVar(value=False)
        
        # Переменные для отслеживания изменений
        self.preview_scheduled = False
        
        # Переменные для режимов редактирования и восстановления
        self.edit_mode = False
        self.recover_mode = False
        self.current_user_id = None
        self.original_user_data = None
        
        self.create_notebook()
        
        # Привязываем события изменения полей к обновлению предпросмотра
        self.bind_preview_events()
    
    def create_notebook(self):
        """Создает вкладки интерфейса"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_tab = ttk.Frame(self.notebook)
        self.admin_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.create_tab, text='Создание профиля')
        self.notebook.add(self.admin_tab, text='Администрирование')
        
        self.setup_create_tab()
        self.setup_admin_tab()
    
    def setup_create_tab(self):
        """Настраивает вкладку создания профиля"""
        main_frame = ttk.Frame(self.create_tab)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Левая панель - форма
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Заголовок будет меняться в зависимости от режима
        self.create_title_label = ttk.Label(left_frame, text="Создание нового профиля", font=('Arial', 14, 'bold'))
        self.create_title_label.pack(pady=10)
        
        form_frame = ttk.Frame(left_frame)
        form_frame.pack(fill='x', pady=10)
        
        # Поле для загрузки фото - только кнопка, без поля ввода
        photo_frame = ttk.Frame(form_frame)
        photo_frame.grid(row=0, column=0, columnspan=3, sticky="w", padx=5, pady=5)
        
        ttk.Label(photo_frame, text="Фото пользователя (опционально):").pack(side='left')
        self.photo_button = ttk.Button(photo_frame, text="Обзор", command=self.browse_photo)
        self.photo_button.pack(side='left', padx=5)
        
        # Поле ФИО
        ttk.Label(form_frame, text="ФИО*:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.full_name_entry = ttk.Entry(form_frame, textvariable=self.full_name, width=40)
        self.full_name_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Поле организации
        ttk.Label(form_frame, text="Организация (опционально):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.organization_entry = ttk.Entry(form_frame, textvariable=self.organization, width=40)
        self.organization_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Поле принадлежности
        ttk.Label(form_frame, text="Принадлежность (опционально):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.department_entry = ttk.Entry(form_frame, textvariable=self.department, width=40)
        self.department_entry.grid(row=3, column=1, padx=5, pady=5)
        
        # Поле срока действия с placeholder
        ttk.Label(form_frame, text="Срок действия (опционально):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.expiration_entry = PlaceholderEntry(form_frame, placeholder="ДД.ММ.ГГГГ", width=40)
        self.expiration_entry.grid(row=4, column=1, padx=5, pady=5)
        self.expiration_button = ttk.Button(form_frame, text="+30 дней", command=self.add_30_days)
        self.expiration_button.grid(row=4, column=2, padx=5, pady=5)
        
        # Привязываем переменную к полю с placeholder
        self.expiration_date.trace_add('write', self.on_expiration_date_changed)
        self.expiration_entry.bind('<KeyRelease>', self.on_expiration_entry_changed)
        
        # Галочки для конвертации
        self.convert_photo_check = ttk.Checkbutton(form_frame, text="Конвертировать фото в Ч/Б", 
                       variable=self.convert_photo_to_bw)
        self.convert_photo_check.grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        self.convert_pattern_check = ttk.Checkbutton(form_frame, text="Конвертировать паттерн в Ч/Б", 
                       variable=self.convert_pattern_to_bw)
        self.convert_pattern_check.grid(row=6, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Выбор стиля (ранее шаблона)
        ttk.Label(form_frame, text="Стиль:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
        
        template_frame = ttk.Frame(form_frame)
        template_frame.grid(row=7, column=1, columnspan=2, sticky="w", padx=5, pady=5)
        
        template_names = self.profile_manager.get_template_names()
        template_names.insert(0, "По умолчанию")
        
        self.template_combo = ttk.Combobox(template_frame, textvariable=self.selected_template, 
                                     values=template_names, width=37)
        self.template_combo.pack(side='left')
        self.template_combo.bind('<<ComboboxSelected>>', self.on_template_selected)
        
        self.template_button = ttk.Button(template_frame, text="Управление стилями",
                  command=self.open_template_manager)
        self.template_button.pack(side='left', padx=(5, 0))
        
        # Кнопка создания/применения изменений
        self.buttons_frame = ttk.Frame(left_frame)
        self.buttons_frame.pack(pady=20)
        
        self.create_button = ttk.Button(self.buttons_frame, text="Создать профиль", command=self.generate_profile, style='Accent.TButton')
        self.create_button.pack(side='left', padx=5)
        
        # Кнопка отмены (появляется только в режимах редактирования/восстановления)
        self.cancel_button = ttk.Button(self.buttons_frame, text="Отменить изменения", command=self.cancel_edit)
        
        ttk.Label(left_frame, text="* - обязательные поля", foreground='gray').pack(side='bottom')
        
        # Правая панель - предпросмотр
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        ttk.Label(right_frame, text="Предпросмотр", font=('Arial', 14, 'bold')).pack(pady=10)
        
        self.preview_frame = ttk.Frame(right_frame, relief='sunken', borderwidth=2)
        self.preview_frame.pack(fill='both', expand=True, pady=10)
        
        # Создаем Canvas для предпросмотра с возможностью скроллинга
        self.preview_canvas = tk.Canvas(self.preview_frame, bg='white')
        self.preview_scrollbar_y = ttk.Scrollbar(self.preview_frame, orient='vertical', command=self.preview_canvas.yview)
        self.preview_scrollbar_x = ttk.Scrollbar(self.preview_frame, orient='horizontal', command=self.preview_canvas.xview)
        
        self.preview_canvas.configure(yscrollcommand=self.preview_scrollbar_y.set, xscrollcommand=self.preview_scrollbar_x.set)
        
        self.preview_scrollbar_y.pack(side='right', fill='y')
        self.preview_scrollbar_x.pack(side='bottom', fill='x')
        self.preview_canvas.pack(side='left', fill='both', expand=True)
        
        # Привязываем изменение размера окна к обновлению предпросмотра
        self.preview_frame.bind('<Configure>', self.on_preview_resize)
    
    def update_current_template(self):
        """Обновляет текущий шаблон в менеджере профилей"""
        template_name = self.selected_template.get()
        if template_name == "По умолчанию":
            self.profile_manager.set_current_template(self.profile_manager.get_default_template())
        else:
            template = self.profile_manager.load_template(template_name)
            if template:
                self.profile_manager.set_current_template(template)
        
        # Немедленно обновляем предпросмотр
        self.update_preview()
    
    def on_expiration_date_changed(self, *args):
        """Обновляет поле ввода при изменении переменной даты"""
        current_value = self.expiration_date.get()
        if current_value != self.expiration_entry.get():
            self.expiration_entry.delete(0, tk.END)
            if current_value:
                self.expiration_entry.insert(0, current_value)
                self.expiration_entry.config(foreground=self.expiration_entry.default_fg_color)
            else:
                self.expiration_entry._set_placeholder()
    
    def on_expiration_entry_changed(self, event):
        """Обновляет переменную при изменении поля ввода"""
        current_value = self.expiration_entry.get()
        if current_value != self.expiration_date.get():
            self.expiration_date.set(current_value)
    
    def on_preview_resize(self, event):
        """Обрабатывает изменение размера области предпросмотра"""
        self.update_preview()
    
    def setup_admin_tab(self):
        """Настраивает вкладку администрирования"""
        main_frame = ttk.Frame(self.admin_tab)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="Администрирование профилей", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Поиск профилей
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill='x', pady=10)
        
        ttk.Label(search_frame, text="Введите ID или ФИО для поиска (оставьте пустым для показа всех):").pack(anchor='w')
        
        search_entry_frame = ttk.Frame(search_frame)
        search_entry_frame.pack(fill='x', pady=5)
        
        ttk.Entry(search_entry_frame, textvariable=self.admin_search_term, width=50).pack(side='left', fill='x', expand=True)
        ttk.Button(search_entry_frame, text="Найти", command=self.perform_admin_search).pack(side='right', padx=(5, 0))
        
        # Результаты поиска
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill='both', expand=True, pady=10)
        
        ttk.Label(results_frame, text="Результаты поиска:").pack(anchor='w')
        
        listbox_frame = ttk.Frame(results_frame)
        listbox_frame.pack(fill='both', expand=True, pady=5)
        
        self.admin_results_listbox = tk.Listbox(listbox_frame, height=10)
        self.admin_results_listbox.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame, command=self.admin_results_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.admin_results_listbox.config(yscrollcommand=scrollbar.set)
        
        # Кнопки управления - новое расположение
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=10)
        
        # Левая группа кнопок
        left_buttons_frame = ttk.Frame(buttons_frame)
        left_buttons_frame.pack(side='left')
        
        self.edit_button = ttk.Button(left_buttons_frame, text="Редактировать выбранный", 
                                     command=self.edit_selected, state='disabled')
        self.edit_button.pack(side='left', padx=5)
        
        self.recover_button = ttk.Button(left_buttons_frame, text="Восстановить выбранный", 
                                        command=self.recover_selected, state='disabled')
        self.recover_button.pack(side='left', padx=5)
        
        # Правая группа кнопок
        right_buttons_frame = ttk.Frame(buttons_frame)
        right_buttons_frame.pack(side='right')
        
        self.delete_button = ttk.Button(right_buttons_frame, text="Удалить выбранный", 
                                       command=self.delete_selected, state='disabled')
        self.delete_button.pack(side='right', padx=5)
        
        self.admin_results_listbox.bind('<<ListboxSelect>>', self.on_admin_select)
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
    
    def set_edit_mode(self, user_data):
        """Включает режим редактирования"""
        self.edit_mode = True
        self.recover_mode = False
        self.current_user_id = user_data.get('ID')
        self.original_user_data = user_data.copy()
        
        # Переключаемся на вкладку создания и переименовываем ее
        self.notebook.select(0)
        self.notebook.tab(0, text="Редактирование профиля")
        
        # Обновляем заголовок
        self.create_title_label.config(text="Редактирование профиля")
        
        # Заполняем поля данными пользователя
        self.full_name.set(user_data.get('full_name', ''))
        self.organization.set(user_data.get('organization', ''))
        self.department.set(user_data.get('department', ''))
        if user_data.get('expiration_date'):
            expiration_display = self.profile_manager.format_date_for_display(user_data.get('expiration_date'))
            self.expiration_date.set(expiration_display)
        else:
            self.expiration_date.set('')
        
        # Меняем кнопку
        self.create_button.config(text="Применить изменения")
        
        # Показываем кнопку отмены
        self.cancel_button.pack(side='left', padx=5)
    
    def set_recover_mode(self, user_data):
        """Включает режим восстановления"""
        self.edit_mode = False
        self.recover_mode = True
        self.current_user_id = user_data.get('ID')
        self.original_user_data = user_data.copy()
        
        # Переключаемся на вкладку создания и переименовываем ее
        self.notebook.select(0)
        self.notebook.tab(0, text="Восстановление профиля")
        
        # Обновляем заголовок
        self.create_title_label.config(text="Восстановление профиля")
        
        # Заполняем поля данными пользователя
        self.full_name.set(user_data.get('full_name', ''))
        self.organization.set(user_data.get('organization', ''))
        self.department.set(user_data.get('department', ''))
        if user_data.get('expiration_date'):
            expiration_display = self.profile_manager.format_date_for_display(user_data.get('expiration_date'))
            self.expiration_date.set(expiration_display)
        else:
            self.expiration_date.set('')
        
        # Блокируем поля для редактирования (кроме фото и настроек)
        self.full_name_entry.config(state='disabled')
        self.organization_entry.config(state='disabled')
        self.department_entry.config(state='disabled')
        self.expiration_entry.config(state='disabled')
        self.expiration_button.config(state='disabled')
        
        # Меняем кнопку
        self.create_button.config(text="Восстановить профиль")
        
        # Показываем кнопку отмены
        self.cancel_button.pack(side='left', padx=5)
    
    def cancel_edit(self):
        """Отменяет режимы редактирования/восстановления"""
        self.edit_mode = False
        self.recover_mode = False
        self.current_user_id = None
        self.original_user_data = None
        
        # Восстанавливаем обычный режим и название вкладки
        self.notebook.tab(0, text="Создание профиля")
        self.create_title_label.config(text="Создание нового профиля")
        
        # Очищаем поля
        self.clear_fields()
        
        # Разблокируем поля
        self.full_name_entry.config(state='normal')
        self.organization_entry.config(state='normal')
        self.department_entry.config(state='normal')
        self.expiration_entry.config(state='normal')
        self.expiration_button.config(state='normal')
        
        # Восстанавливаем кнопку
        self.create_button.config(text="Создать профиль")
        
        # Скрываем кнопку отмены
        self.cancel_button.pack_forget()
    
    def bind_preview_events(self):
        """Привязывает события изменения полей к обновлению предпросмотра"""
        self.full_name.trace_add('write', self.schedule_preview_update)
        self.organization.trace_add('write', self.schedule_preview_update)
        self.department.trace_add('write', self.schedule_preview_update)
        self.expiration_date.trace_add('write', self.schedule_preview_update)
        self.photo_path.trace_add('write', self.schedule_preview_update)
        self.selected_template.trace_add('write', self.schedule_preview_update)
        self.convert_photo_to_bw.trace_add('write', self.schedule_preview_update)
        self.convert_pattern_to_bw.trace_add('write', self.schedule_preview_update)
        
        # Добавляем прямое обновление для настроек конвертации (без задержки)
        self.convert_photo_check.configure(command=self.update_preview)
        self.convert_pattern_check.configure(command=self.update_preview)
    
    def schedule_preview_update(self, *args):
        """Планирует обновление предпросмотра с задержкой"""
        if not self.preview_scheduled:
            self.preview_scheduled = True
            self.root.after(500, self.update_preview)  # 500 мс задержка
    
    def update_preview(self):
        """Обновляет предпросмотр"""
        self.preview_scheduled = False
        try:
            self.preview_profile()
        except Exception as e:
            # В случае ошибки просто не обновляем предпросмотр
            print(f"Ошибка при обновлении предпросмотра: {str(e)}")
            pass
    
    def on_tab_changed(self, event):
        """Обработчик переключения вкладок"""
        if self.notebook.index(self.notebook.select()) == 1:  # Вкладка администрирования
            self.perform_admin_search()
    
    def browse_photo(self):
        """Открывает диалог выбора фото"""
        filename = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if filename:
            self.photo_path.set(filename)
            # Убрано всплывающее окно "Фото выбрано"
    
    def add_30_days(self):
        """Добавляет 30 дней к текущей дате"""
        self.expiration_date.set(self.profile_manager.get_add_30_days_date())
    
    def on_template_selected(self, event):
        """Обрабатывает выбор стиля"""
        template_name = self.selected_template.get()
        if template_name == "По умолчанию":
            self.profile_manager.set_current_template(self.profile_manager.get_default_template())
        else:
            template = self.profile_manager.load_template(template_name)
            if template:
                self.profile_manager.set_current_template(template)
                # Обновляем галочки в соответствии с выбранным стилем
                self.convert_photo_to_bw.set(template.get("convert_photo_to_bw", True))
                self.convert_pattern_to_bw.set(template.get("convert_pattern_to_bw", False))
        
        # Немедленно обновляем предпросмотр
        self.update_preview()
    
    def open_template_manager(self):
        """Открывает окно управления стилями"""
        TemplateManagerWindow(self.root, self.profile_manager, self.on_template_change)
    
    def on_template_change(self):
        """Обновляет интерфейс при изменении стиля"""
        # Обновляем список стилей в выпадающем списке
        template_names = self.profile_manager.get_template_names()
        template_names.insert(0, "По умолчанию")
        
        # Находим текущий выбранный стиль
        current_template = self.profile_manager.get_current_template()
        current_name = current_template.get("name", "По умолчанию")
        
        # Обновляем выпадающий список
        self.template_combo['values'] = template_names
        self.selected_template.set(current_name)
        
        # Обновляем галочки в соответствии с выбранным стилем
        self.convert_photo_to_bw.set(current_template.get("convert_photo_to_bw", True))
        self.convert_pattern_to_bw.set(current_template.get("convert_pattern_to_bw", False))
        
        # Немедленно обновляем предпросмотр
        self.update_preview()
    
    def generate_profile(self):
        """Создает новый профиль или применяет изменения в зависимости от режима"""
        if self.edit_mode:
            # Режим редактирования
            try:
                result = self.profile_manager.update_profile(
                    user_id=self.current_user_id,
                    full_name=self.full_name.get(),
                    organization=self.organization.get(),
                    department=self.department.get(),
                    expiration_date=self.expiration_date.get() or None,
                    photo_path=self.photo_path.get() or None,
                    convert_photo_to_bw=self.convert_photo_to_bw.get(),
                    convert_pattern_to_bw=self.convert_pattern_to_bw.get()
                )
                
                if result["success"]:
                    messagebox.showinfo("Успех", "Профиль успешно обновлен!")
                    self.cancel_edit()
                else:
                    messagebox.showerror("Ошибка", "Не удалось обновить профиль")
            
            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Неизвестная ошибка: {str(e)}")
                
        elif self.recover_mode:
            # Режим восстановления
            try:
                result = self.profile_manager.recover_profile(
                    user_id=self.current_user_id,
                    photo_path=self.photo_path.get() or None,
                    convert_photo_to_bw=self.convert_photo_to_bw.get(),
                    convert_pattern_to_bw=self.convert_pattern_to_bw.get()
                )
                
                if result["success"]:
                    messagebox.showinfo("Успех", f"Профиль восстановлен!\nФайл: {result['filename']}")
                    self.cancel_edit()
                else:
                    messagebox.showerror("Ошибка", result.get("error", "Не удалось восстановить профиль"))
            
            except Exception as e:
                messagebox.showerror("Ошибка", f"Неизвестная ошибка: {str(e)}")
                
        else:
            # Обычный режим создания
            try:
                result = self.profile_manager.create_profile(
                    full_name=self.full_name.get(),
                    organization=self.organization.get(),
                    department=self.department.get(),
                    expiration_date=self.expiration_date.get() or None,
                    photo_path=self.photo_path.get() or None,
                    convert_photo_to_bw=self.convert_photo_to_bw.get(),
                    convert_pattern_to_bw=self.convert_pattern_to_bw.get()
                )
                
                if result["success"]:
                    message_type = "временный" if result["is_temporary"] else "бессрочный"
                    messagebox.showinfo("Успех", 
                                      f"Профиль успешно создан!\nID: {result['user_id']}\nТип: {message_type}\nФайл: {result['filename']}")
                    
                    self.clear_fields()
            
            except ValueError as e:
                messagebox.showerror("Ошибка", str(e))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Неизвестная ошибка: {str(e)}")
    
    def preview_profile(self):
        """Создает предпросмотр профиля"""
        if not self.full_name.get():
            # Очищаем предпросмотр, если нет данных
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(150, 150, text="Здесь будет отображаться предпросмотр", 
                                           fill="gray", font=('Arial', 12), width=280)
            return
        
        try:
            # Создаем временные данные для предпросмотра
            preview_data = {
                "ID": "PREVIEW01",
                "full_name": self.full_name.get(),
                "organization": self.organization.get(),
                "department": self.department.get(),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if self.expiration_date.get():
                expiration_storage = self.profile_manager.format_date_for_storage(self.expiration_date.get())
                if expiration_storage:
                    preview_data["expiration_date"] = expiration_storage
            
            # Создаем изображение для предпросмотра
            preview_image = self.profile_manager.preview_profile_image(
                preview_data, 
                convert_pattern_to_bw=self.convert_pattern_to_bw.get()
            )
            
            # Добавляем фото если указано
            if self.photo_path.get() and os.path.exists(self.photo_path.get()):
                preview_image = self.profile_manager.add_user_photo_to_image(
                    preview_image, 
                    self.photo_path.get(),
                    convert_photo_to_bw=self.convert_photo_to_bw.get(),
                    convert_pattern_to_bw=self.convert_pattern_to_bw.get()
                )
            
            # Получаем размеры области предпросмотра
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:  # Проверяем, что canvas уже отрисован
                # Масштабируем изображение под размер области предпросмотра
                scale_factor = min(canvas_width / preview_image.width, canvas_height / preview_image.height) * 0.9
                new_width = int(preview_image.width * scale_factor)
                new_height = int(preview_image.height * scale_factor)
                
                preview_image = preview_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Конвертируем для Tkinter
            photo = ImageTk.PhotoImage(preview_image)
            
            # Обновляем canvas
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(canvas_width // 2, canvas_height // 2, image=photo, anchor="center")
            self.preview_canvas.image = photo  # Сохраняем ссылку
            
            # Обновляем скроллрегион
            self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
            
        except Exception as e:
            # В случае ошибки просто не обновляем предпросмотр
            print(f"Ошибка при создании предпросмотра: {str(e)}")
            pass
    
    def clear_fields(self):
        """Очищает поля ввода"""
        self.photo_path.set("")
        self.full_name.set("")
        self.organization.set("")
        self.department.set("")
        self.expiration_date.set("")
    
    def perform_admin_search(self):
        """Выполняет поиск для администрирования"""
        term = self.admin_search_term.get().strip()
        results = self.profile_manager.search_profiles(term)
        
        self.admin_results_listbox.delete(0, tk.END)
        
        if not results:
            self.admin_results_listbox.insert(tk.END, "Профили не найдены")
            self.edit_button.config(state='disabled')
            self.delete_button.config(state='disabled')
            self.recover_button.config(state='disabled')
        else:
            for user in results:
                expiration_info = ""
                if user.get('expiration_date'):
                    expiration_display = self.profile_manager.format_date_for_display(user['expiration_date'])
                    expiration_info = f" | Действует до: {expiration_display}"
                
                display_text = f"{user.get('full_name', '')} | ID: {user.get('ID', '')} | Орг: {user.get('organization', '')} | Отдел: {user.get('department', '')}{expiration_info}"
                self.admin_results_listbox.insert(tk.END, display_text)
            
            self.admin_results_listbox.results = results
            self.edit_button.config(state='normal')
            self.delete_button.config(state='normal')
            self.recover_button.config(state='normal')
    
    def on_admin_select(self, event):
        """Обработчик выбора в администрировании"""
        selection = self.admin_results_listbox.curselection()
        if selection and hasattr(self.admin_results_listbox, 'results') and selection[0] < len(self.admin_results_listbox.results):
            self.edit_button.config(state='normal')
            self.delete_button.config(state='normal')
            self.recover_button.config(state='normal')
        else:
            self.edit_button.config(state='disabled')
            self.delete_button.config(state='disabled')
            self.recover_button.config(state='disabled')
    
    def recover_selected(self):
        """Восстанавливает выбранный профиль"""
        selection = self.admin_results_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите профиль для восстановления")
            return
        
        selected_index = selection[0]
        if hasattr(self.admin_results_listbox, 'results') and selected_index < len(self.admin_results_listbox.results):
            user_data = self.admin_results_listbox.results[selected_index]
            self.set_recover_mode(user_data)
        else:
            messagebox.showerror("Ошибка", "Не удалось восстановить профиль")
    
    def edit_selected(self):
        """Открывает окно редактирования"""
        selection = self.admin_results_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите профиль для редактирования")
            return
        
        selected_index = selection[0]
        if hasattr(self.admin_results_listbox, 'results') and selected_index < len(self.admin_results_listbox.results):
            user_data = self.admin_results_listbox.results[selected_index]
            self.set_edit_mode(user_data)
        else:
            messagebox.showerror("Ошибка", "Не удалось редактировать профиль")
    
    def delete_selected(self):
        """Удаляет выбранный профиль"""
        selection = self.admin_results_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите профиль для удаления")
            return
        
        selected_index = selection[0]
        if hasattr(self.admin_results_listbox, 'results') and selected_index < len(self.admin_results_listbox.results):
            user_data = self.admin_results_listbox.results[selected_index]
            user_id = user_data.get('ID')
            
            result = messagebox.askyesno(
                "Подтверждение удаления", 
                f"Вы уверены, что хотите удалить профиль?\n\n"
                f"ФИО: {user_data.get('full_name', '')}\n"
                f"ID: {user_id}\n\n"
                f"Это действие нельзя отменить."
            )
            
            if result:
                delete_result = self.profile_manager.delete_profile(user_id)
                if delete_result["success"]:
                    self.perform_admin_search()
                    messagebox.showinfo("Успех", "Профиль успешно удален!")
                else:
                    messagebox.showerror("Ошибка", delete_result.get("error", "Не удалось удалить профиль"))
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить профиль")


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
    app = UserProfileApp(root)
    root.mainloop()
