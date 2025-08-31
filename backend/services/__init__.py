"""
Services package for SoF Event Extractor

Avoid importing heavy submodules at package import time to prevent optional
dependency errors in minimal environments. Import submodules directly, e.g.:

    from services.event_extractor import EventExtractor
    from services.ai_service import AIService
    from services.document_processor import DocumentProcessor
"""

__all__ = [
    'DocumentProcessor',
    'EventExtractor',
    'AIService',
]

