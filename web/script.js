// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    loadAvailableFonts();
    loadAvailablePatterns();
    loadTemplates();
    updateProfilesCount();
    setupAutoPreview();
    setupEditAutoPreview();
    setupRecoverAutoPreview();
});

// Таймеры для задержки предпросмотра
let previewTimeout;
let editPreviewTimeout;
let recoverPreviewTimeout;

// Функция для отображения уведомлений
function showAlert(message, type) {
    const alertDiv = document.getElementById('liveAlert');
    alertDiv.innerHTML = message;
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.style.display = 'block';
    
    setTimeout(() => {
        alertDiv.style.display = 'none';
    }, 5000);
}

// Функция для установки даты +30 дней
async function set30Days() {
    const date = await eel.get_30_days_date()();
    document.getElementById('expiration-date').value = date;
    schedulePreview();
}

// Функция для конвертации изображения в base64
function convertImageToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
        reader.readAsDataURL(file);
    });
}

// Настройка автоматического предпросмотра для формы создания
function setupAutoPreview() {
    const fields = [
        'full-name', 'organization', 'department', 'expiration-date',
        'convert-photo-bw', 'convert-pattern-bw', 'template-select', 'photo'
    ];

    fields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            if (field.type === 'file') {
                field.addEventListener('change', schedulePreview);
            } else if (field.type === 'checkbox' || field.tagName === 'SELECT') {
                field.addEventListener('change', schedulePreview);
            } else {
                field.addEventListener('input', schedulePreview);
            }
        }
    });

    setTimeout(schedulePreview, 500);
}

// Настройка автоматического предпросмотра для формы редактирования
function setupEditAutoPreview() {
    const editFields = [
        'edit-full-name', 'edit-organization', 'edit-department', 'edit-expiration-date',
        'edit-convert-photo-bw', 'edit-convert-pattern-bw', 'edit-template-select', 'edit-photo'
    ];

    editFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            if (field.type === 'file') {
                field.addEventListener('change', scheduleEditPreview);
            } else if (field.type === 'checkbox' || field.tagName === 'SELECT') {
                field.addEventListener('change', scheduleEditPreview);
            } else {
                field.addEventListener('input', scheduleEditPreview);
            }
        }
    });
}

// Настройка автоматического предпросмотра для формы восстановления
function setupRecoverAutoPreview() {
    const recoverFields = [
        'recover-convert-photo-bw', 'recover-convert-pattern-bw', 
        'recover-template-select', 'recover-photo'
    ];

    recoverFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            if (field.type === 'file') {
                field.addEventListener('change', scheduleRecoverPreview);
            } else if (field.type === 'checkbox' || field.tagName === 'SELECT') {
                field.addEventListener('change', scheduleRecoverPreview);
            }
        }
    });
}

// Функция для отложенного предпросмотра (создание)
function schedulePreview() {
    clearTimeout(previewTimeout);
    previewTimeout = setTimeout(generatePreview, 300);
}

// Функция для отложенного предпросмотра (редактирование)
function scheduleEditPreview() {
    clearTimeout(editPreviewTimeout);
    editPreviewTimeout = setTimeout(generateEditPreview, 300);
}

// Функция для отложенного предпросмотра (восстановление)
function scheduleRecoverPreview() {
    clearTimeout(recoverPreviewTimeout);
    recoverPreviewTimeout = setTimeout(generateRecoverPreview, 300);
}

// Функция для генерации предпросмотра
async function generatePreview() {
    try {
        const fullName = document.getElementById('full-name').value;
        if (!fullName) {
            document.getElementById('preview-image').style.display = 'none';
            document.querySelector('#preview-container p').style.display = 'block';
            return;
        }

        const profileData = {
            full_name: fullName,
            organization: document.getElementById('organization').value,
            department: document.getElementById('department').value,
            expiration_date: document.getElementById('expiration-date').value,
            convert_photo_to_bw: document.getElementById('convert-photo-bw').checked,
            convert_pattern_to_bw: document.getElementById('convert-pattern-bw').checked,
            template_name: document.getElementById('template-select').value
        };

        const photoInput = document.getElementById('photo');
        if (photoInput.files.length > 0) {
            const file = photoInput.files[0];
            profileData.photo_base64 = await convertImageToBase64(file);
        }

        const result = await eel.generate_preview(profileData)();
        
        if (result.image_data) {
            document.getElementById('preview-image').src = result.image_data;
            document.getElementById('preview-image').style.display = 'block';
            document.querySelector('#preview-container p').style.display = 'none';
        } else if (result.error) {
            console.error('Ошибка генерации предпросмотра:', result.error);
        }
    } catch (error) {
        console.error('Ошибка при генерации предпросмотра:', error);
    }
}

// Функция для создания профиля
async function createProfile() {
    try {
        const fullName = document.getElementById('full-name').value;
        if (!fullName) {
            showAlert('Поле ФИО обязательно для заполнения!', 'warning');
            return;
        }

        const profileData = {
            full_name: fullName,
            organization: document.getElementById('organization').value,
            department: document.getElementById('department').value,
            expiration_date: document.getElementById('expiration-date').value,
            convert_photo_to_bw: document.getElementById('convert-photo-bw').checked,
            convert_pattern_to_bw: document.getElementById('convert-pattern-bw').checked,
            template_name: document.getElementById('template-select').value
        };

        const photoInput = document.getElementById('photo');
        if (photoInput.files.length > 0) {
            const file = photoInput.files[0];
            profileData.photo_base64 = await convertImageToBase64(file);
        }

        const result = await eel.create_profile(profileData)();
        
        if (result.success) {
            showAlert(`Профиль успешно создан! ID: ${result.user_id}`, 'success');
            document.getElementById('profile-form').reset();
            document.getElementById('preview-image').style.display = 'none';
            document.querySelector('#preview-container p').style.display = 'block';
            updateProfilesCount();
        } else {
            showAlert('Ошибка при создании профиля: ' + result.error, 'danger');
        }
    } catch (error) {
        console.error('Ошибка при создании профиля:', error);
        showAlert('Ошибка при создании профиля!', 'danger');
    }
}

// Функция для загрузки доступных шрифтов
async function loadAvailableFonts() {
    const fonts = await eel.get_available_fonts()();
    const fontSelect = document.getElementById('template-font');
    const dataFontSelect = document.getElementById('template-data-font');
    
    fonts.forEach(font => {
        const option1 = document.createElement('option');
        option1.value = font;
        option1.textContent = font;
        fontSelect.appendChild(option1);
        
        const option2 = document.createElement('option');
        option2.value = font;
        option2.textContent = font;
        dataFontSelect.appendChild(option2);
    });
}

// Функция для загрузки доступных паттернов
async function loadAvailablePatterns() {
    const patterns = await eel.get_available_patterns()();
    const patternSelect = document.getElementById('template-pattern');
    
    patterns.forEach(pattern => {
        const option = document.createElement('option');
        option.value = pattern;
        option.textContent = pattern;
        patternSelect.appendChild(option);
    });
}

// Функция для загрузки шаблонов в выпадающие списки
async function loadTemplateOptions() {
    const templates = await eel.get_templates()();
    const templateSelect = document.getElementById('template-select');
    const editTemplateSelect = document.getElementById('edit-template-select');
    const recoverTemplateSelect = document.getElementById('recover-template-select');

    templateSelect.innerHTML = '<option value="default">По умолчанию</option>';
    editTemplateSelect.innerHTML = '<option value="default">По умолчанию</option>';
    recoverTemplateSelect.innerHTML = '<option value="default">По умолчанию</option>';

    templates.forEach(template => {
        const option = document.createElement('option');
        option.value = template.name;
        option.textContent = template.name;
        templateSelect.appendChild(option);

        const option2 = document.createElement('option');
        option2.value = template.name;
        option2.textContent = template.name;
        editTemplateSelect.appendChild(option2);

        const option3 = document.createElement('option');
        option3.value = template.name;
        option3.textContent = template.name;
        recoverTemplateSelect.appendChild(option3);
    });
}

// Функция для загрузки шаблонов
async function loadTemplates() {
    const templates = await eel.get_templates()();
    const templatesList = document.getElementById('templates-list');
    templatesList.innerHTML = '';

    if (templates.length === 0) {
        templatesList.innerHTML = '<p class="text-muted">Шаблоны не найдены</p>';
        return;
    }

    templates.forEach(template => {
        const templateCard = document.createElement('div');
        templateCard.className = 'card mb-3 template-card';
        templateCard.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">${template.name}</h5>
                <p class="card-text mb-2">
                    <small class="text-muted">Паттерн: ${template.pattern}</small><br>
                    <small class="text-muted">Шрифт: ${template.font}</small><br>
                    <small class="text-muted">Размер шрифта: ${template.font_size_normal}/${template.data_font_size_normal}</small>
                </p>
                <div class="btn-group btn-group-sm w-100">
                    <button type="button" class="btn btn-outline-primary" onclick="loadTemplateSettings('${template.name}')">
                        <i class="fas fa-edit"></i> Загрузить
                    </button>
                    <button type="button" class="btn btn-outline-info" onclick="previewTemplate('${template.name}')">
                        <i class="fas fa-eye"></i> Предпросмотр
                    </button>
                    <button type="button" class="btn btn-outline-danger" onclick="deleteTemplate('${template.name}')">
                        <i class="fas fa-trash"></i> Удалить
                    </button>
                </div>
            </div>
        `;
        templatesList.appendChild(templateCard);
    });

    loadTemplateOptions();
}

// Функция для предпросмотра шаблона
async function previewTemplate(templateName) {
    try {
        const result = await eel.preview_template(templateName)();
        
        if (result.image_data) {
            document.getElementById('template-preview-image').src = result.image_data;
            document.getElementById('template-preview-image').style.display = 'block';
            document.querySelector('#template-preview-container p').style.display = 'none';
        } else if (result.error) {
            console.error('Ошибка генерации предпросмотра шаблона:', result.error);
        }
    } catch (error) {
        console.error('Ошибка при генерации предпросмотра шаблона:', error);
    }
}

// Функция для сохранения шаблона
async function saveTemplate() {
    try {
        const templateData = {
            name: document.getElementById('template-name').value,
            pattern: document.getElementById('template-pattern').value,
            font: document.getElementById('template-font').value,
            data_font: document.getElementById('template-data-font').value || document.getElementById('template-font').value,
            font_size_normal: parseInt(document.getElementById('template-font-size').value) || 18,
            data_font_size_normal: parseInt(document.getElementById('template-data-font-size').value) || 16,
            convert_photo_to_bw: document.getElementById('template-convert-photo-bw').checked,
            convert_pattern_to_bw: document.getElementById('template-convert-pattern-bw').checked
        };

        if (!templateData.name || !templateData.pattern || !templateData.font) {
            showAlert('Заполните все обязательные поля!', 'warning');
            return;
        }

        const result = await eel.save_template(templateData)();
        if (result) {
            showAlert('Шаблон успешно сохранен!', 'success');
            document.getElementById('template-form').reset();
            loadTemplates();
        } else {
            showAlert('Ошибка при сохранении шаблона!', 'danger');
        }
    } catch (error) {
        console.error('Ошибка при сохранении шаблона:', error);
        showAlert('Ошибка при сохранении шаблона!', 'danger');
    }
}

// Функция для загрузки настроек шаблона
async function loadTemplateSettings(templateName) {
    const template = await eel.load_template(templateName)();
    if (template) {
        document.getElementById('template-name').value = template.name;
        document.getElementById('template-pattern').value = template.pattern;
        document.getElementById('template-font').value = template.font;
        document.getElementById('template-data-font').value = template.data_font;
        document.getElementById('template-font-size').value = template.font_size_normal;
        document.getElementById('template-data-font-size').value = template.data_font_size_normal;
        document.getElementById('template-convert-photo-bw').checked = template.convert_photo_to_bw;
        document.getElementById('template-convert-pattern-bw').checked = template.convert_pattern_to_bw;
        
        showAlert(`Шаблон "${template.name}" загружен!`, 'success');
    }
}

// Функция для удаления шаблона
async function deleteTemplate(templateName) {
    if (!confirm(`Удалить шаблон "${templateName}"?`)) return;
    
    const result = await eel.delete_template(templateName)();
    if (result) {
        showAlert('Шаблон удален!', 'success');
        loadTemplates();
    } else {
        showAlert('Ошибка при удалении шаблона!', 'danger');
    }
}

// ==================== АДМИНИСТРИРОВАНИЕ ====================

// Функция для поиска профилей
async function searchProfiles() {
    const searchTerm = document.getElementById('search-profiles').value;
    const profiles = await eel.search_profiles(searchTerm)();
    displayProfiles(profiles);
}

// Функция для очистки поиска
async function clearSearch() {
    document.getElementById('search-profiles').value = '';
    await loadAllProfiles();
}

// Функция для загрузки всех профилей
async function loadAllProfiles() {
    const profiles = await eel.search_profiles('')();
    displayProfiles(profiles);
    updateProfilesCount();
}

// Функция для отображения профилей в таблице
function displayProfiles(profiles) {
    const tbody = document.getElementById('profiles-tbody');
    tbody.innerHTML = '';

    if (profiles.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted">
                    <i class="fas fa-info-circle"></i> Профили не найдены
                </td>
            </tr>
        `;
        return;
    }

    profiles.forEach(profile => {
        const row = document.createElement('tr');
        
        const createdDate = formatDisplayDate(profile.created_at);
        const expirationDate = profile.expiration_date ? 
            formatDisplayDate(profile.expiration_date) : 'Бессрочный';

        row.innerHTML = `
            <td>
                <span class="badge bg-secondary">${profile.ID}</span>
                ${profile.is_temporary ? '<i class="fas fa-clock text-warning ms-1" title="Временный профиль"></i>' : ''}
            </td>
            <td>${profile.full_name}</td>
            <td>${profile.organization || '-'}</td>
            <td>${profile.department || '-'}</td>
            <td>${createdDate}</td>
            <td>
                ${profile.expiration_date ? 
                    `<span class="${isDateExpired(profile.expiration_date) ? 'text-danger' : 'text-success'}">${expirationDate}</span>` : 
                    '<span class="text-success">Бессрочный</span>'
                }
            </td>
            <td>
                <div class="btn-group btn-group-sm" role="group">
                    <button type="button" class="btn btn-outline-primary" onclick="editProfile('${profile.ID}')" title="Редактировать">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button type="button" class="btn btn-outline-warning" onclick="openRecoverModal('${profile.ID}')" title="Восстановить">
                        <i class="fas fa-redo"></i>
                    </button>
                    <button type="button" class="btn btn-outline-danger" onclick="showDeleteModal('${profile.ID}', '${profile.full_name}')" title="Удалить">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Функция для открытия модального окна редактирования
async function editProfile(userId) {
    try {
        const profile = await eel.get_profile_by_id(userId)();
        
        if (!profile) {
            showAlert('Профиль не найден!', 'danger');
            return;
        }

        document.getElementById('edit-user-id').value = profile.ID;
        document.getElementById('edit-full-name').value = profile.full_name || '';
        document.getElementById('edit-organization').value = profile.organization || '';
        document.getElementById('edit-department').value = profile.department || '';
        
        if (profile.expiration_date) {
            document.getElementById('edit-expiration-date').value = formatDisplayDate(profile.expiration_date);
        } else {
            document.getElementById('edit-expiration-date').value = '';
        }

        document.getElementById('edit-convert-photo-bw').checked = true;
        document.getElementById('edit-convert-pattern-bw').checked = false;
        document.getElementById('edit-template-select').value = 'default';

        const modal = new bootstrap.Modal(document.getElementById('editProfileModal'));
        modal.show();

        setTimeout(scheduleEditPreview, 100);

    } catch (error) {
        console.error('Ошибка при загрузке профиля:', error);
        showAlert('Ошибка при загрузке профиля!', 'danger');
    }
}

// Функция для открытия модального окна восстановления
async function openRecoverModal(userId) {
    try {
        const profile = await eel.get_profile_by_id(userId)();
        
        if (!profile) {
            showAlert('Профиль не найден!', 'danger');
            return;
        }

        document.getElementById('recover-user-id').value = profile.ID;
        document.getElementById('recover-convert-photo-bw').checked = true;
        document.getElementById('recover-convert-pattern-bw').checked = false;
        document.getElementById('recover-template-select').value = 'default';
        document.getElementById('recover-photo').value = '';

        const modal = new bootstrap.Modal(document.getElementById('recoverProfileModal'));
        modal.show();

        setTimeout(scheduleRecoverPreview, 100);

    } catch (error) {
        console.error('Ошибка при загрузке профиля:', error);
        showAlert('Ошибка при загрузке профиля!', 'danger');
    }
}

// Функция для генерации предпросмотра при редактировании
async function generateEditPreview() {
    try {
        const profileData = {
            full_name: document.getElementById('edit-full-name').value,
            organization: document.getElementById('edit-organization').value,
            department: document.getElementById('edit-department').value,
            expiration_date: document.getElementById('edit-expiration-date').value,
            convert_photo_to_bw: document.getElementById('edit-convert-photo-bw').checked,
            convert_pattern_to_bw: document.getElementById('edit-convert-pattern-bw').checked,
            template_name: document.getElementById('edit-template-select').value
        };

        if (!profileData.full_name) {
            document.getElementById('edit-preview-image').style.display = 'none';
            return;
        }

        const photoInput = document.getElementById('edit-photo');
        if (photoInput.files.length > 0) {
            const file = photoInput.files[0];
            profileData.photo_base64 = await convertImageToBase64(file);
        }

        const result = await eel.generate_preview(profileData)();
        
        if (result.image_data) {
            document.getElementById('edit-preview-image').src = result.image_data;
            document.getElementById('edit-preview-image').style.display = 'block';
        } else if (result.error) {
            console.error('Ошибка генерации предпросмотра:', result.error);
        }
    } catch (error) {
        console.error('Ошибка при генерации предпросмотра:', error);
    }
}

// Функция для генерации предпросмотра при восстановлении
async function generateRecoverPreview() {
    try {
        const userId = document.getElementById('recover-user-id').value;
        const profile = await eel.get_profile_by_id(userId)();
        
        if (!profile) return;

        const profileData = {
            full_name: profile.full_name,
            organization: profile.organization || '',
            department: profile.department || '',
            expiration_date: profile.expiration_date ? formatDisplayDate(profile.expiration_date) : '',
            convert_photo_to_bw: document.getElementById('recover-convert-photo-bw').checked,
            convert_pattern_to_bw: document.getElementById('recover-convert-pattern-bw').checked,
            template_name: document.getElementById('recover-template-select').value
        };

        const photoInput = document.getElementById('recover-photo');
        if (photoInput.files.length > 0) {
            const file = photoInput.files[0];
            profileData.photo_base64 = await convertImageToBase64(file);
        }

        const result = await eel.generate_preview(profileData)();
        
        if (result.image_data) {
            document.getElementById('recover-preview-image').src = result.image_data;
            document.getElementById('recover-preview-image').style.display = 'block';
        } else if (result.error) {
            console.error('Ошибка генерации предпросмотра:', result.error);
        }
    } catch (error) {
        console.error('Ошибка при генерации предпросмотра:', error);
    }
}

// Функция для обновления профиля
async function updateProfile() {
    try {
        const userId = document.getElementById('edit-user-id').value;
        const fullName = document.getElementById('edit-full-name').value;

        if (!fullName) {
            showAlert('Поле ФИО обязательно для заполнения!', 'warning');
            return;
        }

        const profileData = {
            user_id: userId,
            full_name: fullName,
            organization: document.getElementById('edit-organization').value,
            department: document.getElementById('edit-department').value,
            expiration_date: document.getElementById('edit-expiration-date').value,
            convert_photo_to_bw: document.getElementById('edit-convert-photo-bw').checked,
            convert_pattern_to_bw: document.getElementById('edit-convert-pattern-bw').checked,
            template_name: document.getElementById('edit-template-select').value
        };

        const photoInput = document.getElementById('edit-photo');
        if (photoInput.files.length > 0) {
            const file = photoInput.files[0];
            profileData.photo_base64 = await convertImageToBase64(file);
        }

        const result = await eel.update_profile(profileData)();
        
        if (result.success) {
            showAlert('Профиль успешно обновлен!', 'success');
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('editProfileModal'));
            modal.hide();
            
            await loadAllProfiles();
        } else {
            showAlert('Ошибка при обновлении профиля: ' + result.error, 'danger');
        }
    } catch (error) {
        console.error('Ошибка при обновлении профиля:', error);
        showAlert('Ошибка при обновлении профиля!', 'danger');
    }
}

// Функция для восстановления профиля
async function recoverProfile() {
    try {
        const userId = document.getElementById('recover-user-id').value;

        const profileData = {
            convert_photo_to_bw: document.getElementById('recover-convert-photo-bw').checked,
            convert_pattern_to_bw: document.getElementById('recover-convert-pattern-bw').checked,
            template_name: document.getElementById('recover-template-select').value
        };

        const photoInput = document.getElementById('recover-photo');
        if (photoInput.files.length > 0) {
            const file = photoInput.files[0];
            profileData.photo_base64 = await convertImageToBase64(file);
        }

        const result = await eel.recover_profile(userId, profileData)();
        
        if (result.success) {
            showAlert('Профиль успешно восстановлен!', 'success');
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('recoverProfileModal'));
            modal.hide();
            
            await loadAllProfiles();
        } else {
            showAlert('Ошибка при восстановлении профиля: ' + result.error, 'danger');
        }
    } catch (error) {
        console.error('Ошибка при восстановлении профиля:', error);
        showAlert('Ошибка при восстановлении профиля!', 'danger');
    }
}

// Функция для проверки истекшей даты
function isDateExpired(dateString) {
    const today = new Date();
    const expDate = new Date(dateString);
    return expDate < today;
}

// Функция для форматирования даты
function formatDisplayDate(dateString) {
    if (!dateString) return '';
    
    if (dateString.includes('.')) {
        return dateString;
    }
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU');
    } catch {
        return dateString;
    }
}

// Функция для обновления счетчика профилей
async function updateProfilesCount() {
    const count = await eel.get_profiles_count()();
    document.getElementById('profiles-count').textContent = count;
}

// Функция для показа модального окна удаления
function showDeleteModal(userId, userName) {
    document.getElementById('delete-profile-name').textContent = userName;
    
    const confirmBtn = document.getElementById('confirm-delete-btn');
    confirmBtn.onclick = function() {
        deleteProfile(userId);
    };
    
    const modal = new bootstrap.Modal(document.getElementById('deleteProfileModal'));
    modal.show();
}

// Функция для удаления профиля
async function deleteProfile(userId) {
    try {
        const result = await eel.delete_profile(userId)();
        if (result.success) {
            showAlert('Профиль удален!', 'success');
            await loadAllProfiles();
            const modal = bootstrap.Modal.getInstance(document.getElementById('deleteProfileModal'));
            modal.hide();
        } else {
            showAlert('Ошибка при удалении: ' + result.error, 'danger');
        }
    } catch (error) {
        console.error('Ошибка при удалении профиля:', error);
        showAlert('Ошибка при удалении профиля!', 'danger');
    }
}

// Загрузка профилей при открытии вкладки администрирования
document.getElementById('admin-tab').addEventListener('click', function() {
    loadAllProfiles();
});