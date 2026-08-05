"""
Book Learner
============

Learns from books and documents by extracting and storing knowledge.
"""

from pathlib import Path
from typing import Optional

class BookLearner:
    """Learn from books and documents"""
    
    def __init__(self, memory, books_dir: str = 'books'):
        self.memory = memory
        self.books_dir = Path(books_dir)
        self.books_dir.mkdir(parents=True, exist_ok=True)
    
    def learn_from_text(self, text: str, category: str, source: Optional[str] = None) -> bool:
        """Learn from text"""
        return self.memory.learn_from_text(text, category, source)
    
    def learn_from_file(self, file_path: str, category: str) -> bool:
        """Learn from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return self.learn_from_text(text, category, source=file_path)
        except Exception as e:
            print(f"Error learning from file: {e}")
            return False
