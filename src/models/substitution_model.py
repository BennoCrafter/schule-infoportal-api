from typing import Optional
from pydantic import BaseModel
import datetime

class Substitution(BaseModel):
    class_name: str
    period: str
    absent_teacher: str
    substitution_teacher: str
    room: str
    info: str
    date: datetime.date

    def __str__(self):
        return f"{self.class_name}: {self.period}, {self.absent_teacher}, {self.substitution_teacher}, {self.room}, {self.info}"

    def __hash__(self):
        return hash((self.class_name, self.period, self.absent_teacher, self.substitution_teacher, self.room, self.info, self.date))

    @classmethod
    def from_array(cls, values: list, date: datetime.date):
        if len(values) < 6:
            raise ValueError("Not enough values provided")
        return cls(
            class_name=values[0],  # class_name
            period=values[1],  # period
            absent_teacher=values[2],  # absent_teacher
            substitution_teacher=values[3],  # substitution
            room=values[4],  # room
            info=values[5],  # info
            date=date,
        )

    @classmethod
    def from_array_with_class_name(cls, values: list, class_name: str, date: datetime.date):
        if len(values) < 6:
            raise ValueError("Not enough values provided")
        return cls(
            class_name=class_name,  # class_name
            period=values[1],  # period
            absent_teacher=values[2],  # absent_teacher
            substitution_teacher=values[3],  # substitution
            room=values[4],  # room
            info=values[5],  # info
            date=date,
        )
