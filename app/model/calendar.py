from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import ClassVar
from app.services.util import generate_unique_id, date_lower_than_today_error, event_not_found_error, \
    reminder_not_found_error, slot_not_available_error


# TODO: Implement Reminder class here
@dataclass
class Reminder:
    EMAIL = "email"
    SYSTEM = "system"

    date_time: datetime
    type: str = EMAIL

    def __str__(self):
        return f"Reminder on {self.date_time} of type {self.type}"

# TODO: Implement Event class here
@dataclass
class Event:
    title: str
    description: str
    date_: date
    start_at: time
    end_at: time
    reminders: list[Reminder] = field(default_factory=list)
    id: str = field(default_factory=generate_unique_id)

    def add_reminder(self, date_time: datetime, type_: str = Reminder.EMAIL):
        self.reminders.append(Reminder(date_time, type_))

    def delete_reminder(self, reminder_index: int):
        if 0 <= reminder_index < len(self.reminders):
            self.reminders.pop(reminder_index)
        else:
            reminder_not_found_error()

    def __str__(self):
        return f"""
        ID: {self.id}
        Event title: {self.title}
        Description: {self.description}
        Time: {self.start_at} - {self.end_at}
        """.strip()

# TODO: Implement Day class here
class Day:
    def __init__(self, date_: date):
        self.date_ = date_
        self.slots: dict[time, str | None] = {}
        self._init_slots()

    def _init_slots(self):
        start_time = time(0, 0)
        while start_time < time(23, 45):
            self.slots[start_time] = None
            start_time = (datetime.combine(date.today(), start_time) + timedelta(minutes=15)).time()

    def add_event(self, event_id: str, start_at: time, end_at: time):
        for slot in self.slots:
            if start_at <= slot < end_at:
                if self.slots[slot] is not None:
                    slot_not_available_error()
                self.slots[slot] = event_id

    def delete_event(self, event_id: str):
        deleted = False
        for slot, saved_id in self.slots.items():
            if saved_id == event_id:
                self.slots[slot] = None
                deleted = True
        if not deleted:
            event_not_found_error()

    def update_event(self, event_id: str, start_at: time, end_at: time):
        for slot in self.slots:
            if self.slots[slot] == event_id:
                self.slots[slot] = None
        for slot in self.slots:
            if start_at <= slot < end_at:
                if self.slots[slot] is not None:
                    slot_not_available_error()
                self.slots[slot] = event_id

# TODO: Implement Calendar class here
class Calendar:
    def __init__(self):
        self.days: dict[date, Day] = {}
        self.events: dict[str, Event] = {}

    def add_event(self, title: str, description: str, date_: date, start_at: time, end_at: time) -> str:
        if date_ < datetime.now().date():
            date_lower_than_today_error()
        if date_ not in self.days:
            self.days[date_] = Day(date_)
        event = Event(title, description, date_, start_at, end_at)
        self.days[date_].add_event(event.id, start_at, end_at)
        self.events[event.id] = event
        return event.id

    def add_reminder(self, event_id: str, date_time: datetime, type_: str = Reminder.EMAIL):
        if event_id not in self.events:
            event_not_found_error()
        self.events[event_id].add_reminder(date_time, type_)

    def find_available_slots(self, date_: date) -> list[time]:
        if date_ not in self.days:
            return [time(hour, minute) for hour in range(24) for minute in range(0, 60, 15)]
        return [slot for slot, event in self.days[date_].slots.items() if event is None]

    def update_event(self, event_id: str, title: str, description: str, date_: date, start_at: time, end_at: time):
        event = self.events.get(event_id)
        if not event:
            event_not_found_error()
        if event.date_ != date_:
            self.delete_event(event_id)
            event = Event(title, description, date_, start_at, end_at, id=event_id)
            self.events[event_id] = event
            if date_ not in self.days:
                self.days[date_] = Day(date_)
            self.days[date_].add_event(event_id, start_at, end_at)
        else:
            event.title = title
            event.description = description
            event.start_at = start_at
            event.end_at = end_at
            self.days[date_].update_event(event_id, start_at, end_at)

    def delete_event(self, event_id: str):
        if event_id not in self.events:
            event_not_found_error()
        del self.events[event_id]
        for day in self.days.values():
            if event_id in day.slots.values():
                day.delete_event(event_id)
                break

    def find_events(self, start_at: date, end_at: date) -> dict[date, list[Event]]:
        return {event.date_: event for event in self.events.values() if start_at <= event.date_ <= end_at}

    def delete_reminder(self, event_id: str, reminder_index: int):
        if event_id not in self.events:
            event_not_found_error()
        self.events[event_id].delete_reminder(reminder_index)

    def list_reminders(self, event_id: str) -> list[Reminder]:
        if event_id not in self.events:
            event_not_found_error()
        return self.events[event_id].reminders
