"""Tests of the edx models."""

from mork.edx.mysql.factories.auth import EdxAuthUserFactory, EdxAuthUserprofileFactory
from mork.edx.mysql.factories.certificates import (
    EdxCertificatesGeneratedCertificateFactory,
)
from mork.edx.mysql.factories.student import EdxStudentCourseenrollmentFactory
from mork.edx.mysql.factories.user import EdxUserApiUserpreferenceFactory


def test_edx_models_auth_user_safe_dict(edx_mysql_db):
    """Test the `safe_dict` method for the AuthUser model."""
    edx_auth_user = EdxAuthUserFactory()

    assert edx_auth_user.safe_dict() == {
        "id": edx_auth_user.id,
        "username": edx_auth_user.username,
        "first_name": edx_auth_user.first_name,
        "last_name": edx_auth_user.last_name,
        "email": edx_auth_user.email,
        "password": edx_auth_user.password,
        "is_staff": edx_auth_user.is_staff,
        "is_superuser": edx_auth_user.is_superuser,
        "is_active": edx_auth_user.is_active,
        "date_joined": edx_auth_user.date_joined,
        "last_login": edx_auth_user.last_login,
    }


def test_edx_models_auth_user_profile_safe_dict(edx_mysql_db):
    """Test the `safe_dict` method for the AuthUserprofile model."""
    edx_auth_user_profile = EdxAuthUserprofileFactory()

    assert edx_auth_user_profile.safe_dict() == {
        "id": edx_auth_user_profile.id,
        "user_id": edx_auth_user_profile.user_id,
        "name": edx_auth_user_profile.name,
        "language": edx_auth_user_profile.language,
        "location": edx_auth_user_profile.location,
        "meta": edx_auth_user_profile.meta,
        "courseware": edx_auth_user_profile.courseware,
        "allow_certificate": edx_auth_user_profile.allow_certificate,
        "gender": edx_auth_user_profile.gender,
        "mailing_address": edx_auth_user_profile.mailing_address,
        "year_of_birth": edx_auth_user_profile.year_of_birth,
        "level_of_education": edx_auth_user_profile.level_of_education,
        "goals": edx_auth_user_profile.goals,
        "country": edx_auth_user_profile.country,
        "city": edx_auth_user_profile.city,
        "bio": edx_auth_user_profile.bio,
        "profile_image_uploaded_at": edx_auth_user_profile.profile_image_uploaded_at,
    }


def test_edx_models_user_api_user_preference_safe_dict(edx_mysql_db):
    """Test the `safe_dict` method for the UserApiUserPreference model."""
    edx_user_api_user_preference = EdxUserApiUserpreferenceFactory()

    assert edx_user_api_user_preference.safe_dict() == {
        "id": edx_user_api_user_preference.id,
        "user_id": edx_user_api_user_preference.user_id,
        "key": edx_user_api_user_preference.key,
        "value": edx_user_api_user_preference.value,
    }


def test_edx_models_student_course_enrollment_safe_dict(edx_mysql_db):
    """Test the `safe_dict` method for the StudentCourseEnrollment model."""
    edx_student_course_enrollment = EdxStudentCourseenrollmentFactory()

    assert edx_student_course_enrollment.safe_dict() == {
        "id": edx_student_course_enrollment.id,
        "user_id": edx_student_course_enrollment.user_id,
        "course_id": edx_student_course_enrollment.course_id,
        "is_active": edx_student_course_enrollment.is_active,
        "mode": edx_student_course_enrollment.mode,
        "created": edx_student_course_enrollment.created,
    }


def test_edx_models_certificates_generated_certificate_safe_dict(edx_mysql_db):
    """Test the `safe_dict` method for the StudentCourseEnrollment model."""
    edx_certificates_generated_certificate = (
        EdxCertificatesGeneratedCertificateFactory()
    )

    assert edx_certificates_generated_certificate.safe_dict() == {
        "id": edx_certificates_generated_certificate.id,
        "user_id": edx_certificates_generated_certificate.user_id,
        "download_url": edx_certificates_generated_certificate.download_url,
        "grade": edx_certificates_generated_certificate.grade,
        "course_id": edx_certificates_generated_certificate.course_id,
        "key": edx_certificates_generated_certificate.key,
        "distinction": edx_certificates_generated_certificate.distinction,
        "status": edx_certificates_generated_certificate.status,
        "verify_uuid": edx_certificates_generated_certificate.verify_uuid,
        "download_uuid": edx_certificates_generated_certificate.download_uuid,
        "name": edx_certificates_generated_certificate.name,
        "created_date": edx_certificates_generated_certificate.created_date,
        "modified_date": edx_certificates_generated_certificate.modified_date,
        "error_reason": edx_certificates_generated_certificate.error_reason,
        "mode": edx_certificates_generated_certificate.mode,
    }
