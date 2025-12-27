# Web_UI_writer.py - Основной файл для запуска веб-приложения
import eel
import json
import os
import sys
import base64
import tempfile
from io import BytesIO
from datetime import datetime

# Определяем корневую директорию проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE_DIR = os.path.dirname(os.path.abspath(__file__))

# Добавляем путь для импорта
sys.path.append(CODE_DIR)

from logic_writer import ProfileManager

# Инициализация eel с путем к web папке в корне проекта
WEB_DIR = os.path.join(BASE_DIR, 'web')
eel.init(WEB_DIR)

# Инициализация менеджера профилей
profile_manager = ProfileManager()

@eel.expose
def get_available_fonts():
    """Получение списка доступных шрифтов"""
    return profile_manager.get_available_fonts()

@eel.expose
def get_available_patterns():
    """Получение списка доступных паттернов"""
    return profile_manager.get_available_patterns()

@eel.expose
def create_profile(profile_data):
    """Создание нового профиля"""
    try:
        photo_path = None
        if profile_data.get("photo_base64"):
            photo_data = base64.b64decode(profile_data["photo_base64"].split(',')[1])
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(photo_data)
                photo_path = temp_file.name

        result = profile_manager.create_profile(
            full_name=profile_data["full_name"],
            organization=profile_data.get("organization", ""),
            department=profile_data.get("department", ""),
            expiration_date=profile_data.get("expiration_date"),
            photo_path=photo_path,
            convert_photo_to_bw=profile_data.get("convert_photo_to_bw", True),
            convert_pattern_to_bw=profile_data.get("convert_pattern_to_bw", False),
            template_name=profile_data.get("template_name")
        )
        
        if photo_path and os.path.exists(photo_path):
            os.unlink(photo_path)
            
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

@eel.expose
def update_profile(profile_data):
    """Обновление существующего профиля"""
    try:
        photo_path = None
        if profile_data.get("photo_base64"):
            photo_data = base64.b64decode(profile_data["photo_base64"].split(',')[1])
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(photo_data)
                photo_path = temp_file.name

        result = profile_manager.update_profile(
            user_id=profile_data["user_id"],
            full_name=profile_data["full_name"],
            organization=profile_data.get("organization", ""),
            department=profile_data.get("department", ""),
            expiration_date=profile_data.get("expiration_date"),
            photo_path=photo_path,
            convert_photo_to_bw=profile_data.get("convert_photo_to_bw", True),
            convert_pattern_to_bw=profile_data.get("convert_pattern_to_bw", False),
            template_name=profile_data.get("template_name")
        )
        
        if photo_path and os.path.exists(photo_path):
            os.unlink(photo_path)
            
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

@eel.expose
def get_profile_by_id(user_id):
    """Получение профиля по ID"""
    profile = profile_manager.get_profile_by_id(user_id)
    if profile:
        if profile.get('expiration_date'):
            profile['expiration_date'] = profile_manager.format_date_for_display(
                profile['expiration_date']
            )
        if profile.get('created_at'):
            try:
                created_date = datetime.strptime(profile['created_at'], "%Y-%m-%d %H:%M:%S")
                profile['created_at'] = created_date.strftime("%d.%m.%Y")
            except:
                pass
    return profile

@eel.expose
def search_profiles(search_term):
    """Поиск профилей"""
    results = profile_manager.search_profiles(search_term)
    for profile in results:
        if profile.get('expiration_date'):
            profile['expiration_date'] = profile_manager.format_date_for_display(
                profile['expiration_date']
            )
    return results

@eel.expose
def get_templates():
    """Получение списка шаблонов"""
    template_names = profile_manager.get_template_names()
    templates = []
    for name in template_names:
        template = profile_manager.load_template(name)
        if template:
            templates.append({
                "name": template.get("name", name),
                "pattern": os.path.basename(template.get("pattern", "")),
                "font": os.path.basename(template.get("font", "")),
                "data_font": os.path.basename(template.get("data_font", "")),
                "font_size_normal": template.get("font_size_normal", 18),
                "data_font_size_normal": template.get("data_font_size_normal", 16),
                "convert_photo_to_bw": template.get("convert_photo_to_bw", True),
                "convert_pattern_to_bw": template.get("convert_pattern_to_bw", False)
            })
    return templates

@eel.expose
def save_template(template_data):
    """Сохранение шаблона"""
    try:
        profile_manager.save_template(
            name=template_data["name"],
            pattern=template_data["pattern"],
            font=template_data["font"],
            data_font=template_data.get("data_font", template_data["font"]),
            font_size_normal=template_data.get("font_size_normal", 18),
            data_font_size_normal=template_data.get("data_font_size_normal", 16),
            convert_photo_to_bw=template_data.get("convert_photo_to_bw", True),
            convert_pattern_to_bw=template_data.get("convert_pattern_to_bw", False)
        )
        return True
    except Exception as e:
        print(f"Ошибка сохранения шаблона: {e}")
        return False

@eel.expose
def load_template(template_name):
    """Загрузка шаблона"""
    if template_name == "default":
        template = profile_manager.get_default_template()
    else:
        template = profile_manager.load_template(template_name)
    
    if template:
        return {
            "name": template.get("name", "По умолчанию"),
            "pattern": template.get("pattern", ""),
            "font": template.get("font", ""),
            "data_font": template.get("data_font", ""),
            "font_size_normal": template.get("font_size_normal", 18),
            "data_font_size_normal": template.get("data_font_size_normal", 16),
            "convert_photo_to_bw": template.get("convert_photo_to_bw", True),
            "convert_pattern_to_bw": template.get("convert_pattern_to_bw", False)
        }
    return None

@eel.expose
def delete_template(template_name):
    """Удаление шаблона"""
    return profile_manager.delete_template(template_name)

@eel.expose
def get_30_days_date():
    """Получение даты +30 дней"""
    return profile_manager.get_add_30_days_date()

@eel.expose
def delete_profile(user_id):
    """Удаление профиля"""
    return profile_manager.delete_profile(user_id)

@eel.expose
def recover_profile(user_id, profile_data=None):
    """Восстановление профиля с выбором стиля и фото"""
    try:
        if profile_data is None:
            profile_data = {}

        photo_path = None
        if profile_data.get("photo_base64"):
            photo_data = base64.b64decode(profile_data["photo_base64"].split(',')[1])
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(photo_data)
                photo_path = temp_file.name

        result = profile_manager.recover_profile(
            user_id=user_id,
            photo_path=photo_path,
            convert_photo_to_bw=profile_data.get("convert_photo_to_bw", True),
            convert_pattern_to_bw=profile_data.get("convert_pattern_to_bw", False),
            template_name=profile_data.get("template_name")
        )
        
        if photo_path and os.path.exists(photo_path):
            os.unlink(photo_path)
            
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

@eel.expose
def generate_preview(profile_data):
    """Генерация предпросмотра с учетом текущего стиля"""
    try:
        preview_data = {
            "ID": "PREVIEW01",
            "full_name": profile_data["full_name"],
            "organization": profile_data.get("organization", ""),
            "department": profile_data.get("department", ""),
        }
        
        if profile_data.get("expiration_date"):
            expiration_storage = profile_manager.format_date_for_storage(
                profile_data["expiration_date"]
            )
            if expiration_storage:
                preview_data["expiration_date"] = expiration_storage
        
        convert_pattern_to_bw = profile_data.get("convert_pattern_to_bw", False)
        template_name = profile_data.get("template_name")
        
        preview_image = profile_manager.preview_profile_image(
            preview_data,
            convert_pattern_to_bw=convert_pattern_to_bw,
            template_name=template_name
        )
        
        if profile_data.get("photo_base64"):
            photo_data = base64.b64decode(profile_data["photo_base64"].split(',')[1])
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(photo_data)
                temp_photo_path = temp_file.name
            
            convert_photo_to_bw = profile_data.get("convert_photo_to_bw", True)
            
            preview_image = profile_manager.add_user_photo_to_image(
                preview_image,
                temp_photo_path,
                convert_photo_to_bw=convert_photo_to_bw,
                convert_pattern_to_bw=convert_pattern_to_bw
            )
            
            if os.path.exists(temp_photo_path):
                os.unlink(temp_photo_path)
        
        buffered = BytesIO()
        preview_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {"image_data": f"data:image/png;base64,{img_str}"}
        
    except Exception as e:
        print(f"Ошибка генерации предпросмотра: {e}")
        return {"error": str(e)}

@eel.expose
def preview_template(template_name):
    """Генерация предпросмотра шаблона"""
    try:
        preview_image = profile_manager.preview_template(template_name)
        
        buffered = BytesIO()
        preview_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {"image_data": f"data:image/png;base64,{img_str}"}
        
    except Exception as e:
        print(f"Ошибка генерации предпросмотра шаблона: {e}")
        return {"error": str(e)}

@eel.expose
def get_profiles_count():
    """Получение количества профилей"""
    return profile_manager.get_profiles_count()

@eel.expose
def get_current_template():
    """Получение текущего шаблона"""
    template = profile_manager.get_current_template()
    return {
        "name": template.get("name", "По умолчанию"),
        "pattern": os.path.basename(template.get("pattern", "")),
        "font": os.path.basename(template.get("font", "")),
        "data_font": os.path.basename(template.get("data_font", "")),
        "font_size_normal": template.get("font_size_normal", 18),
        "data_font_size_normal": template.get("data_font_size_normal", 16),
        "convert_photo_to_bw": template.get("convert_photo_to_bw", True),
        "convert_pattern_to_bw": template.get("convert_pattern_to_bw", False)
    }

@eel.expose
def set_current_template(template_name):
    """Установка текущего шаблона"""
    if template_name == "default":
        template = profile_manager.get_default_template()
    else:
        template = profile_manager.load_template(template_name)
    
    if template:
        profile_manager.set_current_template(template)
        return True
    return False

@eel.expose
def get_default_template():
    """Получение шаблона по умолчанию"""
    return profile_manager.get_default_template()

@eel.expose
def ping():
    """Проверка связи с Python"""
    return "pong"

if __name__ == "__main__":
    print("=== Система управления профилями ===")
    print("Запуск сервера...")
    print("Откройте Microsoft Edge и перейдите по адресу: http://localhost:8000")
    print("=" * 50)
    
    eel.start('index.html', port=8000, mode=None, host='localhost')