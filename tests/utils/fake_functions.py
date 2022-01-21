from datetime import date, time
from enum import Enum
from typing import List, Type

from faker import Faker

fake = Faker("es_ES")


def fake_random_word():
    return fake.word()


def fake_random_number(min_number=1, max_number=100):
    return fake.pyint(min_value=min_number, max_value=max_number)


def fake_date(start_date: date = None, end_date: date = None):
    if start_date is None:
        start_date = date(year=2000, month=1, day=1)
    if end_date is None:
        end_date = date.today()
    return fake.date_between(start_date, end_date)


def fake_date_str(
    str_format: str = "%Y-%m-%d",
    start_date: date = None,
    end_date: date = None,
):
    random_date = fake_date(start_date, end_date)
    return random_date.strftime(str_format)


def fake_time(start_time: time = None):
    min_hour = 1
    min_minute = 1
    if start_time:
        min_hour = start_time.hour
        min_minute = start_time.minute
    return time(
        hour=fake_random_number(min_number=min_hour, max_number=23),
        minute=fake_random_number(min_number=min_minute, max_number=59),
    )


def fake_time_str(str_format: str = "%H:%M"):
    time_object = fake_time()
    return time_object.strftime(str_format)


def fake_random_selection(selection_list: List, length: int = 1, unique: bool = True):
    return fake.random_elements(selection_list, length=length, unique=unique)


def fake_random_enum(custom_enum: Type[Enum]):
    selection = fake_random_selection([enum_item.value for enum_item in custom_enum])[0]
    return custom_enum(selection)
