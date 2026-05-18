import datetime
import re
from typing import Optional

from pydantic import BaseModel

_SUB_TEACHER_RE = re.compile(r"^(?:-\s*)?(.*?)\s*\(([\w-]+)\)$")


class Substitution(BaseModel):
    class_name: str
    period: str
    absent_teacher: str
    substitution_teacher: Optional[str]
    subject_abbreviation: Optional[str]
    room: str
    info: str
    date: datetime.date

    def __str__(self):
        return (
            f"{self.class_name}: {self.period}, {self.absent_teacher}, "
            f"{self.substitution_teacher}, {self.subject_abbreviation}, "
            f"{self.room}, {self.info}"
        )

    def __hash__(self):
        return hash(
            (
                self.class_name,
                self.period,
                self.absent_teacher,
                self.substitution_teacher,
                self.subject_abbreviation,
                self.room,
                self.info,
                self.date,
            )
        )

    @staticmethod
    def _parse_substitution_teacher(raw: str) -> tuple[Optional[str], Optional[str]]:
        raw = raw.strip()
        if not raw:
            return None, None

        match = _SUB_TEACHER_RE.match(raw)
        if not match:
            # Fallback: treat the whole string as the teacher, no subject
            return raw or None, None

        teacher = match.group(1).strip() or None
        subject = match.group(2).strip() or None
        return teacher, subject

    @classmethod
    def from_array(cls, values: list, date: datetime.date):
        if len(values) < 6:
            raise ValueError("Not enough values provided")

        teacher, subject = cls._parse_substitution_teacher(values[3])

        return cls(
            class_name=values[0],
            period=values[1],
            absent_teacher=values[2],
            substitution_teacher=teacher,
            subject_abbreviation=subject,
            room=values[4],
            info=values[5],
            date=date,
        )

    @classmethod
    def from_array_with_class_name(
        cls, values: list, class_name: str, date: datetime.date
    ):
        if len(values) < 6:
            raise ValueError("Not enough values provided")

        teacher, subject = cls._parse_substitution_teacher(values[3])

        return cls(
            class_name=class_name,
            period=values[1],
            absent_teacher=values[2],
            substitution_teacher=teacher,
            subject_abbreviation=subject,
            room=values[4],
            info=values[5],
            date=date,
        )
