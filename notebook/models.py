"""
Модуль моделей данных для системы управления заметками.

Содержит классы для представления заметок, их статусов, приоритетов и категорий.
"""

import json
from datetime import datetime
from enum import Enum


class NoteStatus(Enum):
    """Перечисление статусов заметки."""
    
    ACTIVE = "active"
    ARCHIVED = "archived"


class NotePriority(Enum):
    """Перечисление уровней приоритета заметки."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class NoteCategory(Enum):
    """Перечисление категорий заметок."""
    
    WORK = "work"
    PERSONAL = "personal"
    STUDY = "study"
    SHOPPING = "shopping"
    IDEAS = "ideas"
    OTHER = "other"


class Note:
    """Класс, представляющий заметку в системе.
    
    Attributes:
        id (int): Уникальный идентификатор заметки.
        title (str): Заголовок заметки.
        content (str): Текст заметки.
        category (NoteCategory): Категория заметки.
        priority (NotePriority): Приоритет заметки.
        tags (list): Список тегов заметки.
        status (NoteStatus): Статус заметки.
        created_at (str): Время создания в формате ISO.
        updated_at (str): Время последнего обновления в формате ISO.
    """
    
    def __init__(self, id, title, content, category=NoteCategory.OTHER, 
                 priority=NotePriority.MEDIUM, tags=None, status=NoteStatus.ACTIVE,
                 created_at=None, updated_at=None):
        """Инициализирует новую заметку.
        
        Args:
            id (int): Уникальный идентификатор заметки.
            title (str): Заголовок заметки.
            content (str): Текст заметки.
            category (NoteCategory, optional): Категория заметки. По умолчанию OTHER.
            priority (NotePriority, optional): Приоритет заметки. По умолчанию MEDIUM.
            tags (list, optional): Список тегов. По умолчанию пустой список.
            status (NoteStatus, optional): Статус заметки. По умолчанию ACTIVE.
            created_at (str, optional): Время создания. По умолчанию текущее время.
            updated_at (str, optional): Время обновления. По умолчанию текущее время.
        """
        self.id = id
        self.title = title
        self.content = content
        self.category = category
        self.priority = priority
        self.tags = tags or []
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
    
    def to_dict(self):
        """Преобразует объект заметки в словарь для сериализации.
        
        Returns:
            dict: Словарь с данными заметки, готовый для сохранения в JSON.
        """
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category.value,
            'priority': self.priority.value,
            'tags': self.tags,
            'status': self.status.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создает объект заметки из словаря.
        
        Args:
            data (dict): Словарь с данными заметки.
            
        Returns:
            Note: Новый объект заметки.
            
        Raises:
            KeyError: Если в словаре отсутствуют обязательные поля.
            ValueError: Если значения категории, приоритета или статуса некорректны.
        """
        return cls(
            id=data['id'],
            title=data['title'],
            content=data['content'],
            category=NoteCategory(data['category']),
            priority=NotePriority(data['priority']),
            tags=data.get('tags', []),
            status=NoteStatus(data['status']),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def update(self, title=None, content=None, category=None, priority=None, tags=None):
        """Обновляет данные заметки.
        
        Args:
            title (str, optional): Новый заголовок.
            content (str, optional): Новый текст.
            category (NoteCategory, optional): Новая категория.
            priority (NotePriority, optional): Новый приоритет.
            tags (list, optional): Новый список тегов.
        """
        if title is not None:
            self.title = title
        if content is not None:
            self.content = content
        if category is not None:
            self.category = category
        if priority is not None:
            self.priority = priority
        if tags is not None:
            self.tags = tags
        
        self.updated_at = datetime.now().isoformat()
    
    def __str__(self):
        """Возвращает строковое представление заметки.
        
        Returns:
            str: Форматированное строковое представление заметки.
        """
        status_icon = "📁" if self.status == NoteStatus.ARCHIVED else "📝"
        priority_icon = {
            NotePriority.LOW: "⬇",
            NotePriority.MEDIUM: "●",
            NotePriority.HIGH: "⬆"
        }.get(self.priority, "●")
        
        category_icon = {
            NoteCategory.WORK: "💼",
            NoteCategory.PERSONAL: "👤",
            NoteCategory.STUDY: "📚",
            NoteCategory.SHOPPING: "🛒",
            NoteCategory.IDEAS: "💡",
            NoteCategory.OTHER: "📄"
        }.get(self.category, "📄")
        
        tags_str = f" | Tags: {', '.join(self.tags)}" if self.tags else ""
        created = datetime.fromisoformat(self.created_at).strftime("%d.%m.%Y")
        
        return (f"{status_icon} [{priority_icon}] {category_icon} #{self.id}: {self.title}\n"
                f"   Created: {created}{tags_str}\n"
                f"   {self.content[:100]}{'...' if len(self.content) > 100 else ''}")