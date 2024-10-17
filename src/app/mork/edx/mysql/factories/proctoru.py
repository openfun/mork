"""Factory classes for proctoru models."""

import factory

from mork.edx.mysql.models.proctoru import ProctoruProctoruexam, ProctoruProctoruuser

from .base import BaseSQLAlchemyModelFactory


class EdxProctoruProctoruexamFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `proctoru_proctoruexam` table."""

    class Meta:
        """Factory configuration."""

        model = ProctoruProctoruexam

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    start_date = factory.Faker("date_time")
    actual_start_time = factory.Faker("date_time")
    is_completed = factory.Faker("random_int", min=0, max=1)
    is_started = factory.Faker("random_int", min=0, max=1)
    is_canceled = factory.Faker("random_int", min=0, max=1)
    block_id = factory.Faker("hexify", text="^" * 32)
    end_time = factory.Faker("date_time")
    reservation_id = factory.Faker("hexify", text="^" * 40)
    reservation_no = str(factory.Sequence(lambda n: n))
    url = factory.Faker("url")


class EdxProctoruProctoruuserFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `proctoru_proctoruuser` table."""

    class Meta:
        """Factory configuration."""

        model = ProctoruProctoruuser

    id = factory.Sequence(lambda n: n + 1)
    student_id = factory.Sequence(lambda n: n + 1)
    phone_number = factory.Faker("phone_number")
    time_zone = factory.Faker("timezone")
    address = factory.Faker("street_address")
    city = factory.Faker("city")
    country = factory.Faker("country_code")
    date_created = factory.Faker("date_time")
    time_zone_display_name = factory.Faker("pystr", max_chars=100)
    state = factory.Faker("word")
