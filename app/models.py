from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, time
from typing import Optional, List, Dict, Any
from enum import Enum


# Enums for categories
class StudentCategory(str, Enum):
    SUB_JUNIOR = "Sub Junior"
    JUNIOR = "Junior"
    SENIOR = "Senior"
    SUPER_SENIOR = "Super Senior"


# Persistent models (stored in database)
class Admin(SQLModel, table=True):
    __tablename__ = "admins"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, max_length=50)
    password_hash: str = Field(max_length=255)  # Store hashed password
    name: str = Field(max_length=100)
    email: str = Field(unique=True, max_length=255)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Student(SQLModel, table=True):
    __tablename__ = "students"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    class_name: str = Field(max_length=50)  # Using class_name instead of class (reserved keyword)
    category: StudentCategory = Field(default=StudentCategory.SUB_JUNIOR)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    event_participations: List["EventParticipant"] = Relationship(back_populates="student")


class Event(SQLModel, table=True):
    __tablename__ = "events"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    category: str = Field(max_length=100)  # e.g., "Elocution in English", "Song Arabic", "Mappila Song"
    max_participants: Optional[int] = Field(default=None, ge=1)  # Optional maximum number of participants
    priority: int = Field(default=1, ge=1, le=10)  # Priority for scheduling (1-10, higher = more priority)
    average_time_minutes: int = Field(default=30, ge=1)  # Average time per event in minutes for scheduling
    description: str = Field(default="", max_length=1000)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    event_participations: List["EventParticipant"] = Relationship(back_populates="event")
    schedule_slots: List["ScheduleSlot"] = Relationship(back_populates="event")


class EventParticipant(SQLModel, table=True):
    __tablename__ = "event_participants"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="students.id")
    event_id: int = Field(foreign_key="events.id")
    assigned_by_admin_id: int = Field(foreign_key="admins.id")
    assigned_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    student: Student = Relationship(back_populates="event_participations")
    event: Event = Relationship(back_populates="event_participations")
    assigned_by_admin: Admin = Relationship()

    # Unique constraint to prevent duplicate assignments
    __table_args__ = ({"extend_existing": True},)


class Schedule(SQLModel, table=True):
    __tablename__ = "schedules"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)  # e.g., "Main Event Schedule", "Day 1 Schedule"
    description: str = Field(default="", max_length=1000)
    event_date: datetime = Field()  # Date of the scheduled events
    is_generated: bool = Field(default=False)  # True if auto-generated, False if manually created
    is_finalized: bool = Field(default=False)  # True when schedule is locked for printing
    created_by_admin_id: int = Field(foreign_key="admins.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    created_by_admin: Admin = Relationship()
    schedule_slots: List["ScheduleSlot"] = Relationship(back_populates="schedule")


class ScheduleSlot(SQLModel, table=True):
    __tablename__ = "schedule_slots"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    schedule_id: int = Field(foreign_key="schedules.id")
    event_id: int = Field(foreign_key="events.id")
    start_time: time = Field()  # Time of day when event starts
    end_time: time = Field()  # Time of day when event ends
    venue: str = Field(default="", max_length=200)  # Optional venue information
    notes: str = Field(default="", max_length=500)  # Additional notes for the slot
    order_index: int = Field(default=0, ge=0)  # Order within the schedule for display
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    schedule: Schedule = Relationship(back_populates="schedule_slots")
    event: Event = Relationship(back_populates="schedule_slots")


# Non-persistent schemas (for validation, forms, API requests/responses)
class AdminCreate(SQLModel, table=False):
    username: str = Field(max_length=50)
    password: str = Field(min_length=6, max_length=100)  # Raw password for input
    name: str = Field(max_length=100)
    email: str = Field(max_length=255)


class AdminUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = Field(default=None)


class AdminLogin(SQLModel, table=False):
    username: str = Field(max_length=50)
    password: str = Field(max_length=100)


class StudentCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    class_name: str = Field(max_length=50)
    category: StudentCategory = Field(default=StudentCategory.SUB_JUNIOR)


class StudentUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    class_name: Optional[str] = Field(default=None, max_length=50)
    category: Optional[StudentCategory] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class EventCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    category: str = Field(max_length=100)
    max_participants: Optional[int] = Field(default=None, ge=1)
    priority: int = Field(default=1, ge=1, le=10)
    average_time_minutes: int = Field(default=30, ge=1)
    description: str = Field(default="", max_length=1000)


class EventUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    category: Optional[str] = Field(default=None, max_length=100)
    max_participants: Optional[int] = Field(default=None, ge=1)
    priority: Optional[int] = Field(default=None, ge=1, le=10)
    average_time_minutes: Optional[int] = Field(default=None, ge=1)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_active: Optional[bool] = Field(default=None)


class EventParticipantCreate(SQLModel, table=False):
    student_id: int
    event_id: int
    assigned_by_admin_id: int


class ScheduleCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    event_date: datetime
    created_by_admin_id: int


class ScheduleSlotCreate(SQLModel, table=False):
    schedule_id: int
    event_id: int
    start_time: time
    end_time: time
    venue: str = Field(default="", max_length=200)
    notes: str = Field(default="", max_length=500)
    order_index: int = Field(default=0, ge=0)


class ScheduleSlotUpdate(SQLModel, table=False):
    start_time: Optional[time] = Field(default=None)
    end_time: Optional[time] = Field(default=None)
    venue: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None, max_length=500)
    order_index: Optional[int] = Field(default=None, ge=0)


# Read-only schemas for display and printing
class StudentWithEvents(SQLModel, table=False):
    """Student data with their participating events for participant list printing"""

    id: int
    name: str
    class_name: str
    category: StudentCategory
    events: List[str]  # List of event names


class EventWithParticipants(SQLModel, table=False):
    """Event data with participants for event schedule printing"""

    id: int
    name: str
    category: str
    start_time: Optional[time]
    end_time: Optional[time]
    venue: str
    participants: List[Dict[str, Any]]  # List of participant details with name, class, category


class ScheduleSlotDetail(SQLModel, table=False):
    """Detailed schedule slot for printing with event and participant information"""

    id: int
    event_name: str
    event_category: str
    start_time: time
    end_time: time
    venue: str
    notes: str
    participant_count: int
    participants: List[Dict[str, Any]]  # Participants with name, class, category
