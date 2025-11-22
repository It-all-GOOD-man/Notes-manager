"""
Модуль для работы с хранилищем заметок.

Обеспечивает сохранение, загрузку и управление данными заметок в JSON-файле.
"""

import json
import os
from typing import List, Optional
from .models import Note, NoteStatus, NotePriority, NoteCategory


class NoteStorage:
    """Класс для управления хранилищем заметок.
    
    Attributes:
        filename (str): Имя файла для хранения данных.
    """
    
    def __init__(self, filename="notes.json"):
        """Инициализирует хранилище заметок.
        
        Args:
            filename (str, optional): Имя файла для хранения. По умолчанию "notes.json".
        """
        self.filename = filename
    
    def _ensure_file_exists(self):
        """Создает файл для хранения, если он не существует."""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump([], f)
    
    def save_notes(self, notes: List[Note]):
        """Сохраняет список заметок в файл.
        
        Args:
            notes (List[Note]): Список объектов заметок для сохранения.
            
        Raises:
            IOError: Если произошла ошибка при записи в файл.
            PermissionError: Если нет прав для записи в файл.
        """
        self._ensure_file_exists()
        with open(self.filename, 'w') as f:
            json.dump([note.to_dict() for note in notes], f, indent=2)
    
    def load_notes(self) -> List[Note]:
        """Загружает заметки из файла.
        
        Returns:
            List[Note]: Список загруженных заметок.
            
        Raises:
            JSONDecodeError: Если файл содержит некорректный JSON.
            KeyError: Если в данных отсутствуют обязательные поля.
        """
        self._ensure_file_exists()
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                return [Note.from_dict(note_data) for note_data in data]
        except (json.JSONDecodeError, KeyError):
            return []
    
    def get_next_id(self) -> int:
        """Генерирует следующий уникальный идентификатор для новой заметки.
        
        Returns:
            int: Следующий доступный ID.
        """
        notes = self.load_notes()
        if not notes:
            return 1
        return max(note.id for note in notes) + 1
    
    def get_all_tags(self) -> List[str]:
        """Возвращает список всех уникальных тегов из всех заметок.
        
        Returns:
            List[str]: Отсортированный список уникальных тегов.
        """
        notes = self.load_notes()
        all_tags = set()
        for note in notes:
            all_tags.update(note.tags)
        return sorted(list(all_tags))