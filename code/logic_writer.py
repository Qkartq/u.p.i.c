# logic_writer.py - Бизнес-логика приложения
import random
import string
import json
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
from datetime import datetime, timedelta
import textwrap

class ProfileManager:
    def __init__(self):
        # Определяем базовую директорию проекта
        self.base_dir = self.get_base_directory()
        self.existing_data = self.load_existing_data()
        self.templates = self.load_templates()
        self.current_template = self.get_default_template()
        self.check_expired_ids()
    
    def get_base_directory(self):
        """Возвращает базовую директорию проекта"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(current_dir)
    
    def get_full_path(self, relative_path):
        """Преобразует относительный путь в абсолютный относительно базовой директории"""
        return os.path.join(self.base_dir, relative_path)
    
    def get_output_dir(self):
        """Возвращает путь к папке output и создает ее если не существует"""
        output_dir = self.get_full_path("output")
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def get_available_fonts(self):
        """Возвращает список доступных шрифтов"""
        font_dir = self.get_full_path("font")
        available_fonts = []
        
        if os.path.exists(font_dir):
            for file in os.listdir(font_dir):
                if file.lower().endswith(('.ttf', '.otf')):
                    available_fonts.append(file)
        
        return available_fonts
    
    def get_available_patterns(self):
        """Возвращает список доступных паттернов"""
        pattern_dir = self.get_full_path("pattern")
        available_patterns = []
        
        if os.path.exists(pattern_dir):
            for file in os.listdir(pattern_dir):
                if file.lower().endswith(('.bmp', '.jpg', '.jpeg', '.png')):
                    available_patterns.append(file)
        
        return available_patterns
    
    def resolve_font_path(self, font_name):
        """Преобразует имя шрифта в полный путь"""
        if not font_name:
            default_font = self.get_full_path("font/Cormorant-Bold.ttf")
            return default_font
        
        if os.path.isabs(font_name) and os.path.exists(font_name):
            return font_name
        
        font_path = self.get_full_path(f"font/{font_name}")
        if os.path.exists(font_path):
            return font_path
        
        font_path_in_root = os.path.join(self.base_dir, font_name)
        if os.path.exists(font_path_in_root):
            return font_path_in_root
        
        try:
            from PIL import ImageFont
            test_font = ImageFont.truetype(font_name, 12)
            return font_name
        except:
            default_font = self.get_full_path("font/Cormorant-Bold.ttf")
            return default_font
    
    def resolve_pattern_path(self, pattern_name):
        """Преобразует имя паттерна в полный путь"""
        if not pattern_name:
            default_pattern = self.get_full_path("pattern/sys.bmp")
            return default_pattern
        
        if os.path.isabs(pattern_name) and os.path.exists(pattern_name):
            return pattern_name
        
        pattern_path = self.get_full_path(f"pattern/{pattern_name}")
        if os.path.exists(pattern_path):
            return pattern_path
        
        pattern_path_in_root = os.path.join(self.base_dir, pattern_name)
        if os.path.exists(pattern_path_in_root):
            return pattern_path_in_root
        
        default_pattern = self.get_full_path("pattern/sys.bmp")
        return default_pattern
    
    def load_existing_data(self):
        """Загружает существующие данные из database/data_user.md"""
        data_file = self.get_full_path("database/data_user.md")
        if os.path.exists(data_file):
            try:
                with open(data_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if not content:
                        return []
                    
                    users = []
                    user_blocks = content.split('---')
                    
                    for block in user_blocks:
                        block = block.strip()
                        if not block:
                            continue
                            
                        user_data = {}
                        lines = block.split('\n')
                        for line in lines:
                            if ':' in line:
                                key, value = line.split(':', 1)
                                user_data[key.strip()] = value.strip()
                        
                        if user_data:
                            users.append(user_data)
                    
                    return users
            except Exception as e:
                print(f"Ошибка при загрузке данных: {e}")
                return []
        return []
    
    def reload_templates(self):
        """Перезагружает шаблоны из файла"""
        self.templates = self.load_templates()
    
    def load_templates(self):
        """Загружает шаблоны из database/templates.json"""
        templates_file = self.get_full_path("database/templates.json")
        if os.path.exists(templates_file):
            try:
                with open(templates_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Ошибка при загрузке шаблонов: {e}")
                return {}
        return {}
    
    def save_templates(self):
        """Сохраняет шаблоны в database/templates.json"""
        templates_file = self.get_full_path("database/templates.json")
        os.makedirs(os.path.dirname(templates_file), exist_ok=True)
        
        with open(templates_file, "w", encoding="utf-8") as f:
            json.dump(self.templates, f, ensure_ascii=False, indent=2)
    
    def get_default_template(self):
        """Возвращает настройки по умолчанию"""
        cormorant_font_path = self.get_full_path("font/Cormorant-Bold.ttf")
        
        return {
            "name": "По умолчанию",
            "pattern": self.get_full_path("pattern/sys.bmp"),
            "font": cormorant_font_path,
            "data_font": cormorant_font_path,
            "font_size_normal": 18,
            "data_font_size_normal": 16,
            "convert_photo_to_bw": True,
            "convert_pattern_to_bw": False
        }
    
    def save_all_data(self):
        """Сохраняет все данные в database/data_user.md"""
        data_file = self.get_full_path("database/data_user.md")
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        
        content = ""
        for user in self.existing_data:
            content += "---\n"
            for key, value in user.items():
                content += f"{key}: {value}\n"
            content += "\n"
        
        with open(data_file, "w", encoding="utf-8") as f:
            f.write(content)
    
    def check_expired_ids(self):
        """Проверяет и удаляет просроченные ID"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        expired_profiles = []
        
        for user in self.existing_data:
            if isinstance(user, dict) and user.get('expiration_date'):
                if user['expiration_date'] < current_date:
                    expired_profiles.append(user)
        
        for expired_user in expired_profiles:
            self.existing_data.remove(expired_user)
            
            safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in expired_user.get('full_name', ''))
            filename = os.path.join(self.get_output_dir(), f"{safe_name}_{expired_user.get('ID', '')}_profile.bmp")
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except Exception as e:
                    print(f"Не удалось удалить файл {filename}: {e}")
        
        if expired_profiles:
            self.save_all_data()
            print(f"Удалено {len(expired_profiles)} просроченных профилей")
    
    def generate_unique_id(self):
        """Генерирует уникальный ID, которого еще нет в системе"""
        characters = string.ascii_uppercase + string.digits
        existing_ids = [user.get('ID', '') for user in self.existing_data if isinstance(user, dict)]
        
        while True:
            new_id = ''.join(random.choice(characters) for _ in range(8))
            if new_id not in existing_ids:
                return new_id
    
    def validate_date(self, date_string):
        """Проверяет корректность введенной даты"""
        try:
            datetime.strptime(date_string, "%d.%m.%Y")
            return True
        except ValueError:
            return False
    
    def format_date_for_storage(self, date_string):
        """Преобразует дату из формата ДД.ММ.ГГГГ в ГГГГ-ММ-ДД для хранения"""
        try:
            date_obj = datetime.strptime(date_string, "%d.%m.%Y")
            return date_obj.strftime("%Y-%m-%d")
        except ValueError:
            return None
    
    def format_date_for_display(self, date_string):
        """Преобразует дату из формата ГГГГ-ММ-ДД в ДД.ММ.ГГГГ для отображения"""
        try:
            date_obj = datetime.strptime(date_string, "%Y-%m-%d")
            return date_obj.strftime("%d.%m.%Y")
        except ValueError:
            return date_string
    
    def create_profile(self, full_name, organization, department, expiration_date=None, photo_path=None, convert_photo_to_bw=True, convert_pattern_to_bw=False, template_name=None):
        """Создает новый профиль"""
        if not full_name:
            raise ValueError("Поле ФИО обязательно для заполнения!")
        
        if template_name and template_name != "default":
            template = self.load_template(template_name)
            if template:
                old_template = self.current_template
                self.current_template = template
        
        expiration_storage = None
        if expiration_date:
            if not self.validate_date(expiration_date):
                raise ValueError("Неверный формат даты! Используйте ДД.ММ.ГГГГ")
            expiration_storage = self.format_date_for_storage(expiration_date)
        
        user_id = self.generate_unique_id()
        
        data = {
            "ID": user_id,
            "full_name": full_name,
            "organization": organization,
            "department": department,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if expiration_storage:
            data["expiration_date"] = expiration_storage
            data["is_temporary"] = True
        
        self.existing_data.append(data)
        self.save_all_data()
        
        filename = self.create_profile_image(data, convert_pattern_to_bw=convert_pattern_to_bw)
        
        if photo_path:
            self.add_user_photo(filename, photo_path, convert_photo_to_bw=convert_photo_to_bw, convert_pattern_to_bw=convert_pattern_to_bw)
        
        if template_name and template_name != "default":
            self.current_template = old_template
        
        return {
            "success": True,
            "user_id": user_id,
            "filename": filename,
            "is_temporary": bool(expiration_storage)
        }
    
    def update_profile(self, user_id, full_name, organization, department, expiration_date=None, photo_path=None, convert_photo_to_bw=True, convert_pattern_to_bw=False, template_name=None):
        """Обновляет существующий профиль"""
        if not full_name:
            raise ValueError("Поле ФИО обязательно для заполнения!")
        
        if template_name and template_name != "default":
            template = self.load_template(template_name)
            if template:
                old_template = self.current_template
                self.current_template = template
        
        expiration_storage = None
        if expiration_date:
            if not self.validate_date(expiration_date):
                raise ValueError("Неверный формат даты! Используйте ДД.ММ.ГГГГ")
            expiration_storage = self.format_date_for_storage(expiration_date)
        
        for user in self.existing_data:
            if user.get('ID') == user_id:
                user['full_name'] = full_name
                user['organization'] = organization
                user['department'] = department
                user['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if expiration_storage:
                    user['expiration_date'] = expiration_storage
                    user['is_temporary'] = True
                elif 'expiration_date' in user:
                    del user['expiration_date']
                    if 'is_temporary' in user:
                        del user['is_temporary']
                break
        
        self.save_all_data()
        
        updated_user = next((user for user in self.existing_data if user.get('ID') == user_id), None)
        if updated_user:
            filename = self.create_profile_image(updated_user, update_mode=True, convert_pattern_to_bw=convert_pattern_to_bw)
            
            if photo_path:
                self.add_user_photo(filename, photo_path, convert_photo_to_bw=convert_photo_to_bw, convert_pattern_to_bw=convert_pattern_to_bw)
            
            if template_name and template_name != "default":
                self.current_template = old_template
            
            return {
                "success": True,
                "filename": filename
            }
        
        return {"success": False}
    
    def delete_profile(self, user_id):
        """Удаляет профиль"""
        user_to_delete = next((user for user in self.existing_data if user.get('ID') == user_id), None)
        if not user_to_delete:
            return {"success": False, "error": "Профиль не найден"}
        
        self.existing_data = [user for user in self.existing_data if user.get('ID') != user_id]
        self.save_all_data()
        
        safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in user_to_delete.get('full_name', ''))
        filename = os.path.join(self.get_output_dir(), f"{safe_name}_{user_id}_profile.bmp")
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception as e:
                print(f"Не удалось удалить файл {filename}: {e}")
        
        return {"success": True}
    
    def search_profiles(self, search_term):
        """Ищет профили по ID или ФИО"""
        results = []
        
        if not search_term.strip():
            return self.existing_data
        
        for user in self.existing_data:
            if isinstance(user, dict):
                if user.get('ID', '').upper() == search_term.upper():
                    results.append(user)
                elif search_term.lower() in user.get('full_name', '').lower():
                    results.append(user)
        
        return results
    
    def get_profile_by_id(self, user_id):
        """Возвращает профиль по ID"""
        for user in self.existing_data:
            if user.get('ID') == user_id:
                return user
        return None
    
    def recover_profile(self, user_id, photo_path=None, convert_photo_to_bw=True, convert_pattern_to_bw=False, template_name=None):
        """Восстанавливает профиль (создает изображение заново)"""
        user_data = self.get_profile_by_id(user_id)
        if not user_data:
            return {"success": False, "error": "Профиль не найден"}
        
        if template_name and template_name != "default":
            template = self.load_template(template_name)
            if template:
                old_template = self.current_template
                self.current_template = template
        
        filename = self.create_profile_image(user_data, recover_mode=True, convert_pattern_to_bw=convert_pattern_to_bw)
        
        if photo_path:
            self.add_user_photo(filename, photo_path, convert_photo_to_bw=convert_photo_to_bw, convert_pattern_to_bw=convert_pattern_to_bw)
        
        if template_name and template_name != "default":
            self.current_template = old_template
        
        return {
            "success": True,
            "filename": filename
        }
    
    def wrap_text(self, text, max_chars_per_line):
        """Разбивает текст на несколько строк с увеличенным переносом"""
        adjusted_max_chars = max_chars_per_line - 5
        
        if len(text) <= adjusted_max_chars:
            return [text]
        
        wrapped_lines = textwrap.wrap(text, width=adjusted_max_chars)
        return wrapped_lines
    
    def create_profile_image(self, data, recover_mode=False, update_mode=False, preview_mode=False, convert_pattern_to_bw=False):
        """Создает изображение профиля на основе данных"""
        template_settings = self.current_template
        
        pattern_path = self.resolve_pattern_path(template_settings.get("pattern"))
        font_path = self.resolve_font_path(template_settings.get("font"))
        data_font_path = self.resolve_font_path(template_settings.get("data_font", template_settings.get("font")))
        
        font_size_normal = template_settings.get("font_size_normal", 18)
        data_font_size_normal = template_settings.get("data_font_size_normal", 16)
        
        try:
            template = Image.open(pattern_path)
        except FileNotFoundError:
            print(f"Ошибка: Паттерн не найден: {pattern_path}")
            template = Image.new('RGB', (800, 500), color='white')

        if convert_pattern_to_bw and template.mode != 'L':
            template = ImageOps.grayscale(template)

        draw = ImageDraw.Draw(template)
        
        try:
            font_normal = ImageFont.truetype(font_path, font_size_normal)
            data_font_normal = ImageFont.truetype(data_font_path, data_font_size_normal)
        except Exception as e:
            print(f"Ошибка загрузки шрифтов: {e}")
            font_normal = ImageFont.load_default()
            data_font_normal = ImageFont.load_default()

        text_area_width = template.width // 2 + 100
        y_offset = 50
        
        # ФИО
        draw.text((50, y_offset), "ФИО:", fill="black", font=font_normal)
        
        fio_text = data['full_name']
        fio_lines = self.wrap_text(fio_text, 30)
        
        header_width = draw.textlength("ФИО:", font=font_normal)
        data_x = 50 + header_width + 10
        
        for i, line in enumerate(fio_lines):
            if i == 0:
                draw.text((data_x, y_offset), line, fill="black", font=data_font_normal)
                y_offset += 30
            else:
                draw.text((50, y_offset), line, fill="black", font=data_font_normal)
                y_offset += 30

        # Организация
        draw.text((50, y_offset), "Организация:", fill="black", font=font_normal)
        
        org_text = data['organization']
        org_lines = self.wrap_text(org_text, 25)
        
        header_width = draw.textlength("Организация:", font=font_normal)
        data_x = 50 + header_width + 10
        
        for i, line in enumerate(org_lines):
            if i == 0:
                draw.text((data_x, y_offset), line, fill="black", font=data_font_normal)
                y_offset += 25
            else:
                draw.text((50, y_offset), line, fill="black", font=data_font_normal)
                y_offset += 25
    
        # Отдел
        draw.text((50, y_offset), "Отдел:", fill="black", font=font_normal)
        
        dept_text = data['department']
        dept_lines = self.wrap_text(dept_text, 35)
        
        header_width = draw.textlength("Отдел:", font=font_normal)
        data_x = 50 + header_width + 10
        
        for i, line in enumerate(dept_lines):
            if i == 0:
                draw.text((data_x, y_offset), line, fill="black", font=data_font_normal)
                y_offset += 25
            else:
                draw.text((50, y_offset), line, fill="black", font=data_font_normal)
                y_offset += 25
    
        # Срок действия
        if 'expiration_date' in data:
            expiration_display = self.format_date_for_display(data['expiration_date'])
            
            draw.text((50, y_offset), "Действителен до:", fill="black", font=font_normal)
            
            expiration_text = expiration_display
            expiration_lines = self.wrap_text(expiration_text, 35)
            
            header_width = draw.textlength("Действителен до:", font=font_normal)
            data_x = 50 + header_width + 10
            
            for i, line in enumerate(expiration_lines):
                if i == 0:
                    draw.text((data_x, y_offset), line, fill="black", font=data_font_normal)
                    y_offset += 30
                else:
                    draw.text((50, y_offset), line, fill="black", font=data_font_normal)
                    y_offset += 30
            
            try:
                timer_image_path = self.get_full_path("interface/timer.png")
                timer_image = Image.open(timer_image_path)
                
                if timer_image.mode == 'RGBA':
                    background = Image.new('RGB', timer_image.size, (255, 255, 255))
                    background.paste(timer_image, mask=timer_image.split()[3])
                    timer_image = background
                
                if convert_pattern_to_bw and timer_image.mode != 'L':
                    timer_image = ImageOps.grayscale(timer_image)
                
                timer_image.thumbnail((100, 100))
                template.paste(timer_image, (20, template.height - timer_image.height - 20))
            except FileNotFoundError:
                try:
                    timer_image_path = self.get_full_path("interface/timer.bmp")
                    timer_image = Image.open(timer_image_path)
                    if convert_pattern_to_bw and timer_image.mode != 'L':
                        timer_image = ImageOps.grayscale(timer_image)
                    timer_image.thumbnail((100, 100))
                    template.paste(timer_image, (20, template.height - timer_image.height - 20))
                except FileNotFoundError:
                    draw.text((20, template.height - 40), "ВРЕМЕННЫЙ", fill="black", font=font_normal)

        # QR-код
        try:
            qr = qrcode.QRCode(
                version=1,
                box_size=10,
                border=2,
                error_correction=qrcode.constants.ERROR_CORRECT_L
            )
            qr.add_data(data['ID'])
            qr.make(fit=True)
            
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            qr_size = min(template.width // 2, template.height // 2, 200)
            qr_image = qr_image.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
            
            if convert_pattern_to_bw and qr_image.mode != 'L':
                qr_image = ImageOps.grayscale(qr_image)
            
            qr_position = (template.width - qr_image.width - 68, template.height - qr_image.height - 28)
            
            template.paste(qr_image, qr_position)
            
        except Exception as e:
            print(f"Ошибка при создании QR-кода: {str(e)}")
            draw.text((template.width - 150, template.height - 30), 
                     f"ID: {data['ID']}", fill="black", font=font_normal)

        if preview_mode:
            if template.mode == 'RGBA':
                template = template.convert('RGB')
            return template
        
        safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in data['full_name'])
        output_dir = self.get_output_dir()
        filename = os.path.join(output_dir, f"{safe_name}_{data['ID']}_profile.bmp")
        
        if not recover_mode and not update_mode:
            counter = 1
            original_filename = filename
            while os.path.exists(filename):
                name_part, ext = original_filename.rsplit('.', 1)
                filename = f"{name_part}_{counter}.{ext}"
                counter += 1
        
        if template.mode == 'RGBA':
            template = template.convert('RGB')
        
        template.save(filename)
            
        return filename
    
    def crop_to_square(self, image):
        """Обрезает изображение до квадратного формата 1:1"""
        width, height = image.size
        
        min_side = min(width, height)
        
        left = (width - min_side) / 2
        top = (height - min_side) / 2
        right = (width + min_side) / 2
        bottom = (height + min_side) / 2
        
        cropped_image = image.crop((left, top, right, bottom))
        
        return cropped_image
    
    def add_user_photo_to_image(self, profile_image, photo_path, convert_photo_to_bw=True, convert_pattern_to_bw=False):
        """Добавляет фото пользователя к изображению профиля в памяти"""
        if not photo_path or not os.path.exists(photo_path):
            return profile_image
            
        try:
            result_image = profile_image.copy()
            
            user_photo = Image.open(photo_path)
            
            if convert_photo_to_bw and user_photo.mode != 'L':
                user_photo = ImageOps.grayscale(user_photo)
            
            user_photo = self.crop_to_square(user_photo)
            
            user_photo.thumbnail((180, 180))
            
            photo_x = result_image.width - user_photo.width - 80
            photo_y = 35
            
            if convert_pattern_to_bw and user_photo.mode != 'L':
                user_photo = ImageOps.grayscale(user_photo)
            
            result_image.paste(user_photo, (photo_x, photo_y))
            
            user_photo.close()
            
            return result_image
            
        except Exception as e:
            print(f"Не удалось добавить фото пользователя: {str(e)}")
            return profile_image
    
    def add_user_photo(self, profile_image_path, photo_path, convert_photo_to_bw=True, convert_pattern_to_bw=False):
        """Добавляет фото пользователя на изображение профиля"""
        if not photo_path or not os.path.exists(photo_path):
            return
            
        try:
            profile = Image.open(profile_image_path)
            
            if convert_pattern_to_bw and profile.mode != 'L':
                profile = ImageOps.grayscale(profile)
            
            user_photo = Image.open(photo_path)
            
            if convert_photo_to_bw and user_photo.mode != 'L':
                user_photo = ImageOps.grayscale(user_photo)
            
            user_photo = self.crop_to_square(user_photo)
            
            user_photo.thumbnail((180, 180))
            
            photo_x = profile.width - user_photo.width - 80
            photo_y = 35
            
            if convert_pattern_to_bw and user_photo.mode != 'L':
                user_photo = ImageOps.grayscale(user_photo)
            
            profile.paste(user_photo, (photo_x, photo_y))
            profile.save(profile_image_path)
            
            profile.close()
            user_photo.close()
            
        except Exception as e:
            print(f"Не удалось добавить фото пользователя: {str(e)}")
            raise
    
    def get_profiles_count(self):
        """Возвращает количество профилей в системе"""
        return len(self.existing_data)
    
    def get_add_30_days_date(self):
        """Возвращает дату +30 дней от текущей"""
        future_date = datetime.now() + timedelta(days=30)
        return future_date.strftime("%d.%m.%Y")
    
    def set_current_template(self, template):
        """Устанавливает текущий шаблон"""
        if template and isinstance(template, dict):
            self.current_template = template
        else:
            self.current_template = self.get_default_template()
    
    def get_current_template(self):
        """Возвращает текущий шаблон"""
        return self.current_template
    
    def get_template_names(self):
        """Возвращает список имен шаблонов"""
        return list(self.templates.keys())
    
    def save_template(self, name, pattern, font, data_font=None, font_size_normal=18, 
                     data_font_size_normal=16, convert_photo_to_bw=True, convert_pattern_to_bw=False):
        """Сохраняет новый шаблон"""
        if data_font is None:
            data_font = font
        
        self.templates[name] = {
            "name": name,
            "pattern": pattern,
            "font": font,
            "data_font": data_font,
            "font_size_normal": font_size_normal,
            "data_font_size_normal": data_font_size_normal,
            "convert_photo_to_bw": convert_photo_to_bw,
            "convert_pattern_to_bw": convert_pattern_to_bw
        }
        self.save_templates()
        
        current_template = self.get_current_template()
        if current_template.get("name") == name:
            self.set_current_template(self.templates[name])
    
    def load_template(self, name):
        """Загружает шаблон по имени"""
        self.reload_templates()
        if name in self.templates:
            return self.templates[name]
        return None
    
    def delete_template(self, name):
        """Удаляет шаблон"""
        if name in self.templates:
            del self.templates[name]
            self.save_templates()
            return True
        return False
    
    def preview_profile_image(self, data, convert_pattern_to_bw=False, template_name=None):
        """Создает изображение для предпросмотра"""
        old_template = self.current_template
        
        if template_name and template_name != "default":
            template = self.load_template(template_name)
            if template:
                self.current_template = template
        
        preview_image = self.create_profile_image(data, preview_mode=True, convert_pattern_to_bw=convert_pattern_to_bw)
        
        if template_name and template_name != "default":
            self.current_template = old_template
        
        return preview_image
    
    def preview_template(self, template_name, convert_pattern_to_bw=False):
        """Создает предпросмотр шаблона с тестовыми данными"""
        test_data = {
            "ID": "TEMPLATE01",
            "full_name": "Иванов Иван Иванович",
            "organization": "ООО 'Пример'",
            "department": "Отдел разработки",
            "expiration_date": "31.12.2025"
        }
        
        return self.preview_profile_image(test_data, convert_pattern_to_bw=convert_pattern_to_bw, template_name=template_name)