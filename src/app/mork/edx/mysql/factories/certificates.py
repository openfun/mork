"""Factory classes for certificates models."""

import factory

from mork.edx.mysql.models.certificates import (
    CertificatesCertificatehtmlviewconfiguration,
    CertificatesGeneratedcertificate,
)

from .base import BaseSQLAlchemyModelFactory, faker


class EdxCertificatesCertificatehtmlviewconfigurationFactory(
    BaseSQLAlchemyModelFactory
):
    """Factory for the `certificates_certificatehtmlviewconfiguration` table."""

    class Meta:
        """Factory configuration."""

        model = CertificatesCertificatehtmlviewconfiguration

    id = factory.Sequence(lambda n: n + 1)
    change_date = factory.Faker("date_time")
    changed_by_id = factory.Sequence(lambda n: n + 1)
    enabled = True
    configuration = factory.Faker("pystr")


class EdxCertificatesGeneratedCertificateFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `certificates_generatedcertificate` table."""

    class Meta:
        """Factory configuration."""

        model = CertificatesGeneratedcertificate

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    course_id = factory.Sequence(lambda n: f"course-v1:edX+{faker.pystr()}+{n}")
    download_url = factory.Faker("uri")
    grade = factory.LazyAttribute(lambda _: str(faker.pyfloat())[:5])
    key = factory.Faker("hexify", text="^" * 32)
    distinction = factory.Faker("pyint")
    status = factory.Faker(
        "random_element", elements=["downloadable", "notpassing", "unavailable"]
    )
    verify_uuid = factory.Faker("hexify", text="^" * 32)
    download_uuid = factory.Faker("hexify", text="^" * 32)
    name = factory.Faker("name")
    created_date = factory.Faker("date_time")
    modified_date = factory.Faker("date_time")
    error_reason = factory.Faker("pystr")
    mode = factory.Faker("word")
