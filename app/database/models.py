from datetime import datetime
from sqlalchemy import (
  Boolean,
  Column,
  ForeignKey,
  JSON,
  Integer,
  String,
  Table,
  Text,
  TIMESTAMP,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, Set



class Base(DeclarativeBase):
  type_annotation_map = {
    datetime: TIMESTAMP(timezone=True),
  }

