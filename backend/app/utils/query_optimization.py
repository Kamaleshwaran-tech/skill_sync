"""
Database query optimization helpers to prevent N+1 issues.
"""
from __future__ import annotations

from typing import Type, TypeVar, Sequence
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import select

T = TypeVar("T")


def load_with_relations(db: Session, model: Type[T], filters: dict = None, relations: Sequence[str] = None) -> Sequence[T]:
    """Load model instances with eager-loaded relationships to prevent N+1 queries."""
    query = select(model)
    
    if relations:
        for relation in relations:
            if hasattr(model, relation):
                query = query.options(selectinload(getattr(model, relation)))
    
    if filters:
        for key, value in filters.items():
            if hasattr(model, key):
                query = query.where(getattr(model, key) == value)
    
    return db.execute(query).unique().scalars().all()
