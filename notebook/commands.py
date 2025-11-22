"""
Модуль обработчиков команд для системы управления заметками.

Содержит класс с методами для выполнения всех операций с заметками.
"""


import argparse
from typing import List
from datetime import datetime
from .models import Note, NoteStatus, NotePriority, NoteCategory  # Используем относительные импорты
from .storage import NoteStorage  # Используем относительные импорты


class NoteCommands:
    """Класс для обработки команд управления заметками."""
    
    def __init__(self, storage: NoteStorage):
        """Инициализирует обработчик команд.
        
        Args:
            storage (NoteStorage): Объект хранилища заметок.
        """
        self.storage = storage
    
    def add_note(self, title: str, content: str, category: str = "other", 
                 priority: str = "medium", tags: List[str] = None) -> str:
        """Добавляет новую заметку в хранилище.
        
        Args:
            title (str): Заголовок заметки.
            content (str): Текст заметки.
            category (str, optional): Категория заметки. По умолчанию "other".
            priority (str, optional): Приоритет заметки. По умолчанию "medium".
            tags (List[str], optional): Список тегов. По умолчанию None.
            
        Returns:
            str: Сообщение о результате операции.
            
        Raises:
            ValueError: Если категория или приоритет имеют некорректное значение.
        """
        notes = self.storage.load_notes()
        
        # Валидация категории
        try:
            note_category = NoteCategory(category.lower())
        except ValueError:
            valid_categories = [cat.value for cat in NoteCategory]
            return f"Ошибка: Неверная категория '{category}'. Допустимые значения: {', '.join(valid_categories)}"
        
        # Валидация приоритета
        try:
            note_priority = NotePriority(priority.lower())
        except ValueError:
            return f"Ошибка: Неверный приоритет '{priority}'. Допустимые значения: low, medium, high"
        
        new_note = Note(
            id=self.storage.get_next_id(),
            title=title,
            content=content,
            category=note_category,
            priority=note_priority,
            tags=tags or []
        )
        
        notes.append(new_note)
        self.storage.save_notes(notes)
        return f"Заметка добавлена (ID: {new_note.id}): {title}"
    
    def list_notes(self, category: str = None, priority: str = None, 
                   status: str = "active", show_content: bool = False) -> str:
        """Показывает список заметок с возможностью фильтрации.
        
        Args:
            category (str, optional): Фильтр по категории.
            priority (str, optional): Фильтр по приоритету.
            status (str, optional): Фильтр по статусу. По умолчанию "active".
            show_content (bool, optional): Показывать полный текст. По умолчанию False.
            
        Returns:
            str: Отформатированный список заметок.
        """
        notes = self.storage.load_notes()
        
        if not notes:
            return "Нет заметок"
        
        # Фильтрация
        filtered_notes = notes
        
        if category:
            try:
                category_filter = NoteCategory(category.lower())
                filtered_notes = [n for n in filtered_notes if n.category == category_filter]
            except ValueError:
                valid_categories = [cat.value for cat in NoteCategory]
                return f"Ошибка: Неверная категория '{category}'. Допустимые значения: {', '.join(valid_categories)}"
        
        if priority:
            try:
                priority_filter = NotePriority(priority.lower())
                filtered_notes = [n for n in filtered_notes if n.priority == priority_filter]
            except ValueError:
                return f"Ошибка: Неверный приоритет '{priority}'. Допустимые значения: low, medium, high"
        
        if status:
            try:
                status_filter = NoteStatus(status.lower())
                filtered_notes = [n for n in filtered_notes if n.status == status_filter]
            except ValueError:
                return f"Ошибка: Неверный статус '{status}'. Допустимые значения: active, archived"
        
        if not filtered_notes:
            return "Заметки не найдены по заданным критериям"
        
        # Сортировка по дате создания (новые сначала)
        filtered_notes.sort(key=lambda x: x.created_at, reverse=True)
        
        result = []
        result.append(f"=== Найдено заметок: {len(filtered_notes)} ===")
        
        for note in filtered_notes:
            result.append("─" * 50)
            result.append(str(note))
            if show_content and len(note.content) > 100:
                result.append(f"   Полный текст: {note.content}")
        
        return "\n".join(result)
    
    def search_notes(self, search_term: str, search_in: str = "all") -> str:
        """Выполняет поиск заметок по ключевым словам.
        
        Args:
            search_term (str): Текст для поиска.
            search_in (str, optional): Область поиска. По умолчанию "all".
                Допустимые значения: "title", "content", "tags", "all".
                
        Returns:
            str: Отформатированные результаты поиска.
        """
        notes = self.storage.load_notes()
        
        if not notes:
            return "Нет заметок"
        
        search_term = search_term.lower()
        found_notes = []
        
        for note in notes:
            matches = False
            
            if search_in in ["all", "title"] and search_term in note.title.lower():
                matches = True
            elif search_in in ["all", "content"] and search_term in note.content.lower():
                matches = True
            elif search_in in ["all", "tags"] and any(search_term in tag.lower() for tag in note.tags):
                matches = True
            
            if matches:
                found_notes.append(note)
        
        if not found_notes:
            return f"Заметки по запросу '{search_term}' не найдены"
        
        found_notes.sort(key=lambda x: x.created_at, reverse=True)
        
        result = [f"=== Результаты поиска: '{search_term}' ({len(found_notes)} найдено) ==="]
        for note in found_notes:
            result.append("─" * 50)
            result.append(str(note))
        
        return "\n".join(result)
    
    def delete_note(self, note_id: int) -> str:
        """Удаляет заметку по идентификатору.
        
        Args:
            note_id (int): ID заметки для удаления.
            
        Returns:
            str: Сообщение о результате операции.
        """
        notes = self.storage.load_notes()
        
        for i, note in enumerate(notes):
            if note.id == note_id:
                deleted_title = note.title
                del notes[i]
                self.storage.save_notes(notes)
                return f"Заметка удалена: #{note_id} - {deleted_title}"
        
        return f"Ошибка: Заметка с ID #{note_id} не найдена"
    
    def archive_note(self, note_id: int) -> str:
        """Перемещает заметку в архив.
        
        Args:
            note_id (int): ID заметки для архивации.
            
        Returns:
            str: Сообщение о результате операции.
        """
        notes = self.storage.load_notes()
        
        for note in notes:
            if note.id == note_id:
                if note.status == NoteStatus.ARCHIVED:
                    return f"Заметка #{note_id} уже в архиве"
                note.status = NoteStatus.ARCHIVED
                note.updated_at = datetime.now().isoformat()
                self.storage.save_notes(notes)
                return f"Заметка архивирована: #{note_id} - {note.title}"
        
        return f"Ошибка: Заметка с ID #{note_id} не найдена"
    
    def edit_note(self, note_id: int, title: str = None, content: str = None, 
                  category: str = None, priority: str = None, tags: List[str] = None) -> str:
        """Редактирует существующую заметку.
        
        Args:
            note_id (int): ID редактируемой заметки.
            title (str, optional): Новый заголовок.
            content (str, optional): Новый текст.
            category (str, optional): Новая категория.
            priority (str, optional): Новый приоритет.
            tags (List[str], optional): Новые теги.
            
        Returns:
            str: Сообщение о результате операции.
        """
        notes = self.storage.load_notes()
        
        for note in notes:
            if note.id == note_id:
                # Валидация категории
                note_category = None
                if category:
                    try:
                        note_category = NoteCategory(category.lower())
                    except ValueError:
                        valid_categories = [cat.value for cat in NoteCategory]
                        return f"Ошибка: Неверная категория '{category}'. Допустимые значения: {', '.join(valid_categories)}"
                
                # Валидация приоритета
                note_priority = None
                if priority:
                    try:
                        note_priority = NotePriority(priority.lower())
                    except ValueError:
                        return f"Ошибка: Неверный приоритет '{priority}'. Допустимые значения: low, medium, high"
                
                note.update(
                    title=title,
                    content=content,
                    category=note_category,
                    priority=note_priority,
                    tags=tags
                )
                
                self.storage.save_notes(notes)
                return f"Заметка обновлена: #{note_id} - {note.title}"
        
        return f"Ошибка: Заметка с ID #{note_id} не найдена"
    
    def list_tags(self) -> str:
        """Показывает все используемые теги с количеством заметок.
        
        Returns:
            str: Отформатированный список тегов.
        """
        tags = self.storage.get_all_tags()
        
        if not tags:
            return "Теги не найдены"
        
        result = ["=== Все теги ==="]
        for tag in tags:
            # Находим заметки с этим тегом
            notes_with_tag = [note for note in self.storage.load_notes() if tag in note.tags]
            result.append(f"#{tag} ({len(notes_with_tag)} заметок)")
        
        return "\n".join(result)