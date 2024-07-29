"""Tests of the edx models."""

from mork.edx.factories import EdxUserFactory


def test_edx_models_user_safe_dict(db):
    """Test the `safe_dict` method for the User model."""
    edx_user = EdxUserFactory()

    assert edx_user.safe_dict() == {
        "id": edx_user.id,
        "is_staff": edx_user.is_staff,
        "is_superuser": edx_user.is_superuser,
        "last_login": edx_user.last_login,
    }
