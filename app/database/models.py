from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
  ARRAY,
  Boolean,
  Column,
  ForeignKey,
  JSON,
  Integer,
  Numeric,
  String,
  Table,
  Text,
  TIMESTAMP,
  Float,
  Enum
)
from app.database.enums import(
  AccountStatusEnum,
  StatusEnum,
  PriorityLevelEnum,
  LegalCaseStatusEnum,
  CaseTypeEnum,
  InvoiceStatusEnum,
  ) 
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, Set



class Base(DeclarativeBase):
  type_annotation_map = {
    datetime: TIMESTAMP(timezone=True),
  }

tbl_role_x_permissions = Table(
  "role_x_permissions",
  Base.metadata,
  Column("role_id", ForeignKey("role.id"), primary_key=True),
  Column("permission_id", ForeignKey("permission.id"), primary_key=True),
)

class Permission(Base):
  __tablename__ = "permission"

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)

  roles: Mapped[Set["Role"]] = relationship(
    secondary=tbl_role_x_permissions,
    back_populates="permissions"
  )

  def __repr__(self) -> str:
    return f"{self.id}"


class Role(Base):
  __tablename__ = "role"

  id: Mapped[int] = mapped_column(primary_key=True)
  name: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)

  permissions: Mapped[Set["Permission"]] = relationship(
    secondary=tbl_role_x_permissions,
    back_populates="roles"
  )
  users: Mapped[Set["User"]] = relationship(back_populates="role")


  def __repr__(self) -> str:
    return f"{self.id}"




class Subscription(Base):
    __tablename__ = "subscription"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_name: Mapped[str] = mapped_column(String(20))
    pricing: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    
    accounts: Mapped[Set["Account"]] = relationship(back_populates="subscription")
    
    def __repr__(self) -> str:
        return f"{self.id}"   
 
tbl_account_x_clients = Table(
  "account_x_clients",
  Base.metadata,
  Column("account_id", ForeignKey("account.id"), primary_key=True),
  Column("client_id", ForeignKey("client.id"), primary_key=True),
)   


class Account(Base):
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    subscription_type: Mapped[int] = mapped_column(ForeignKey("subscription.id"),nullable=False)  
    subscription_end_date: Mapped[datetime] = mapped_column(nullable=False)
    add_ons: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    ##status: Mapped[str] = mapped_column(String, nullable=False)  # Luego se reemplaza por Enum
    
    status: Mapped[AccountStatusEnum] = mapped_column(
        Enum(AccountStatusEnum, name="account_status", native_enum=True),
        nullable=False,
        default=AccountStatusEnum.RUNNING
    )
    
    subscription:Mapped["Subscription"] = relationship(back_populates="accounts")
    users: Mapped[Set["User"]] = relationship(back_populates="account")
    
    clients: Mapped[Set["Client"]] = relationship(
      secondary=tbl_account_x_clients,
      back_populates="accounts"
    )
    
    legal_cases: Mapped[Set["LegalCase"]] = relationship(back_populates="account")
    agendas: Mapped[Set["Agenda"]] = relationship(back_populates="account")
    
    def __repr__(self) -> str:
        return f"{self.id}"
      
class Client(Base):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone_1: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    phone_2: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    dni: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # Luego se reemplaza por Enum
    address: Mapped[str] = mapped_column(Text, nullable=False)


    accounts: Mapped[Set["Account"]] = relationship(
      secondary=tbl_account_x_clients,
      back_populates="clients"
    )
    
    legal_cases: Mapped[Set["LegalCase"]] = relationship(back_populates="client")
    invoices: Mapped[Set["Invoice"]] = relationship(back_populates="client")

    def __repr__(self) -> str:
        return f"{self.id}"
      
tbl_legal_case_x_users = Table(
  "legal_case_x_users",
  Base.metadata,
  Column("legal_case_id", ForeignKey("legal_case.id"), primary_key=True),
  Column("user_id", ForeignKey("user.id"), primary_key=True),
)  

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    dni: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    username:Mapped[str]=mapped_column(String(24),nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    association:Mapped[int]=mapped_column(Integer,nullable=False,unique=True)#numero de colegiatura aun cosideramos si es factible que se quede
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    city:Mapped[str]=mapped_column(Text)
    
    ##status: Mapped[str] = mapped_column(String(10), nullable=True)  # Luego se reemplaza por Enum
    
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum, name="user_status", native_enum=True),
        nullable=False,
        default=StatusEnum.INACTIVE
    )

    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), nullable=False)

    account: Mapped["Account"] = relationship(back_populates="users")
    role: Mapped["Role"] = relationship(back_populates="users")
    agendas: Mapped[Set["Agenda"]] = relationship(back_populates="user")
    
    legal_cases: Mapped[Set["LegalCase"]] = relationship(
      secondary=tbl_legal_case_x_users,
      back_populates="users"
    )
    
    invoices_issued: Mapped[Set["Invoice"]] = relationship(back_populates="issued_by_user")


    def __repr__(self) -> str:
      return f"{self.id}"

tbl_legal_case_x_files = Table(
  "legal_case_x_files",
  Base.metadata,
  Column("legal_case_id", ForeignKey("legal_case.id"), primary_key=True),
  Column("file_id", ForeignKey("file.id"), primary_key=True),
) 

class LegalCase(Base):
    __tablename__ = "legal_case"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    case_number:Mapped[Optional[str]]=mapped_column(String(20))
    start_date: Mapped[datetime] = mapped_column(
      TIMESTAMP(timezone=True), nullable=True
    )
    end_date: Mapped[datetime] = mapped_column(
      TIMESTAMP(timezone=True), nullable=True
    )
    ##case_type: Mapped[str] = mapped_column(String(50), nullable=False)  # Luego se reemplaza por Enum
    
    case_type: Mapped[CaseTypeEnum] = mapped_column(
        Enum(CaseTypeEnum, name="case_type_legal_case", native_enum=True),
        nullable=False,
        default=CaseTypeEnum.CIVIL
    )
    
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    ##priority_level: Mapped[str] = mapped_column(String(20), nullable=False)  # Luego se reemplaza por Enum
    
    priority_level: Mapped[PriorityLevelEnum] = mapped_column(
        Enum(PriorityLevelEnum, name="priority_level_legal_case", native_enum=True),
        nullable=False,
        default=PriorityLevelEnum.NORMAL
    )
  
    
    notes:Mapped[str]=mapped_column(Text)
    
    ##status: Mapped[str] = mapped_column(String(30), nullable=False)  # Luego se reemplaza por Enum
    
    status: Mapped[LegalCaseStatusEnum] = mapped_column(
        Enum(LegalCaseStatusEnum, name="status_legal_case", native_enum=True),
        nullable=False,
        default=LegalCaseStatusEnum.ACTIVO
    )
    
    client: Mapped["Client"] = relationship(back_populates="legal_cases")
    account: Mapped["Account"] = relationship(back_populates="legal_cases")
    
    files: Mapped[Set["File"]] = relationship(
      secondary=tbl_legal_case_x_files,
      back_populates="legal_cases"
    )
    
    users: Mapped[Set["User"]] = relationship(
      secondary=tbl_legal_case_x_users,
      back_populates="legal_cases"
    )

    def __repr__(self) -> str:
        return f"{self.id}"
      
class File(Base):
    __tablename__ = "file"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(String(100), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    upload_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    size_mb:Mapped[Float]=mapped_column(Float, nullable=False)
    
    ##status:Mapped[str]=mapped_column(String,nullable=False) # Luego se reemplaza por Enum
    
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum, name="file_status", native_enum=True),
        nullable=False,
        default=StatusEnum.INACTIVE
    )
    
    legal_cases: Mapped[Set["LegalCase"]] = relationship(
      secondary=tbl_legal_case_x_files,
      back_populates="files"
    )
    

    def __repr__(self) -> str:
        return f"{self.id}"



class Agenda(Base):
    __tablename__ = "agenda"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_name: Mapped[str] = mapped_column(String(40), nullable=False)
    description:Mapped[str]= mapped_column(Text,nullable=False)
    due_date: Mapped[datetime] = mapped_column(
      TIMESTAMP(timezone=True), nullable=True
    )
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    
    
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    account: Mapped["Account"] = relationship(back_populates="agendas")
    user: Mapped["User"] = relationship(back_populates="agendas")

    def __repr__(self) -> str:
        return f"{self.id}"

class Invoice(Base):
    __tablename__ = "invoice"

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_number: Mapped[int] = mapped_column(nullable=False)  
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"), nullable=False)
    emission_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    due_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    issued_by_user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    
    
    ##status: Mapped[str] = mapped_column(String(20), nullable=False)  # Luego se reemplaza por Enum
    
    status: Mapped[InvoiceStatusEnum] = mapped_column(
        Enum(InvoiceStatusEnum, name="invoice_status", native_enum=True),
        nullable=False,
        default=InvoiceStatusEnum.DUE
    )

    client: Mapped["Client"] = relationship(back_populates="invoices")
    issued_by_user: Mapped["User"] = relationship(back_populates="invoices_issued")
    items: Mapped[Set["InvoiceItem"]] = relationship(back_populates="invoice", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"{self.id}"

class InvoiceItem(Base):
    __tablename__ = "invoice_item"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(Text)
    hourly_rate: Mapped[float] = mapped_column(Float, nullable=False)
    hours_worked: Mapped[int] = mapped_column(default=1)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoice.id"), nullable=False)

    invoice: Mapped["Invoice"] = relationship(back_populates="items")

    def __repr__(self) -> str:
        return f"{self.id}"
