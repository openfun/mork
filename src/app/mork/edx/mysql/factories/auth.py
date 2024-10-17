"""Factory classes for auth models."""

import factory

from mork.edx.mysql.models.auth import (
    AuthRegistration,
    AuthtokenToken,
    AuthUser,
    AuthUserGroups,
    AuthUserprofile,
)

from .base import BaseSQLAlchemyModelFactory, faker
from .bulk import EdxBulkEmailCourseemailFactory, EdxBulkEmailOptoutFactory
from .certificates import (
    EdxCertificatesCertificatehtmlviewconfigurationFactory,
    EdxCertificatesGeneratedCertificateFactory,
)
from .contentstore import EdxContentstoreVideouploadconfigFactory
from .course import (
    EdxCourseActionStateCoursererunstateFactory,
    EdxCourseCreatorsCoursecreatorFactory,
    EdxCourseGroupsCohortmembershipFactory,
    EdxCourseGroupsCourseusergroupUsersFactory,
)
from .courseware import (
    EdxCoursewareOfflinecomputedgradeFactory,
    EdxCoursewareStudentmoduleFactory,
    EdxCoursewareXmodulestudentinfofieldFactory,
    EdxCoursewareXmodulestudentprefsfieldFactory,
)
from .dark import EdxDarkLangDarklangconfigFactory
from .django import EdxDjangoCommentClientRoleUsersFactory
from .instructor import EdxInstructorTaskInstructortaskFactory
from .notify import EdxNotifySettingFactory
from .payment import EdxPaymentUseracceptanceFactory
from .proctoru import EdxProctoruProctoruexamFactory, EdxProctoruProctoruuserFactory
from .student import (
    EdxStudentAnonymoususeridFactory,
    EdxStudentCourseaccessroleFactory,
    EdxStudentCourseenrollmentFactory,
    EdxStudentHistoricalcourseenrollmentFactory,
    EdxStudentLanguageproficiencyFactory,
    EdxStudentLoginfailureFactory,
    EdxStudentPendingemailchangeFactory,
    EdxStudentUserstandingFactory,
)
from .user import EdxUserApiUserpreferenceFactory
from .util import EdxUtilRatelimitconfigurationFactory
from .verify import (
    EdxVerifyStudentHistoricalverificationdeadlineFactory,
    EdxVerifyStudentSoftwaresecurephotoverificationFactory,
)


class EdxAuthRegistrationFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `auth_registration` table."""

    class Meta:
        """Factory configuration."""

        model = AuthRegistration

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    activation_key = factory.Faker("hexify", text="^" * 32)


class EdxAuthtokenTokenFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `authtoken_token` table."""

    class Meta:
        """Factory configuration."""

        model = AuthtokenToken

    key = factory.Faker("hexify", text="^" * 40)
    user_id = factory.Sequence(lambda n: n + 1)
    created = factory.Faker("date_time")


class EdxAuthUserGroupsFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `auth_user_groups` table."""

    class Meta:
        """Factory configuration."""

        model = AuthUserGroups

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    group_id = factory.Sequence(lambda n: n + 1)


class EdxAuthUserprofileFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `auth_userprofile` table."""

    class Meta:
        """Factory configuration."""

        model = AuthUserprofile

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("name")
    language = factory.Faker("language_code")
    location = factory.Faker("address")
    meta = factory.Faker("json")
    courseware = factory.Faker("pystr")
    allow_certificate = factory.Faker("random_int", min=0, max=1)
    gender = factory.Faker("random_element", elements=["f", "m"])
    mailing_address = factory.Faker("email")
    year_of_birth = factory.Faker("year")
    level_of_education = factory.Faker("pystr", max_chars=6)
    goals = factory.Faker("text")
    country = factory.Faker("country_code")
    city = factory.Faker("city")
    bio = factory.Faker("text")
    profile_image_uploaded_at = factory.Faker("date_time")

    student_languageproficiency = factory.RelatedFactoryList(
        EdxStudentLanguageproficiencyFactory,
        "user_profile",
        size=3,
        user_profile_id=factory.SelfAttribute("..id"),
    )


class EdxAuthUserFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `auth_user` table."""

    class Meta:
        """Factory configuration."""

        model = AuthUser

    class Params:
        """Factory parameter to toggle generation of protected tables on or off."""

        with_protected_tables = factory.Trait(
            authtoken_token=factory.RelatedFactory(
                EdxAuthtokenTokenFactory, user_id=factory.SelfAttribute("..id")
            ),
            certificates_certificatehtmlviewconfiguration=factory.RelatedFactoryList(
                EdxCertificatesCertificatehtmlviewconfigurationFactory,
                "changed_by",
                size=3,
                changed_by_id=factory.SelfAttribute("..id"),
            ),
            contentstore_videouploadconfig=factory.RelatedFactoryList(
                EdxContentstoreVideouploadconfigFactory,
                "changed_by",
                size=3,
                changed_by_id=factory.SelfAttribute("..id"),
            ),
            course_action_state_coursererunstate_created_user=factory.RelatedFactoryList(
                EdxCourseActionStateCoursererunstateFactory,
                "created_user",
                size=3,
                created_user_id=factory.SelfAttribute("..id"),
            ),
            course_action_state_coursererunstate_updated_user=factory.RelatedFactoryList(
                EdxCourseActionStateCoursererunstateFactory,
                "updated_user",
                size=3,
                updated_user_id=factory.SelfAttribute("..id"),
            ),
            course_creators_coursecreator=factory.RelatedFactory(
                EdxCourseCreatorsCoursecreatorFactory,
                user_id=factory.SelfAttribute("..id"),
            ),
            dark_lang_darklangconfig=factory.RelatedFactoryList(
                EdxDarkLangDarklangconfigFactory,
                "changed_by",
                size=3,
                changed_by_id=factory.SelfAttribute("..id"),
            ),
            util_ratelimitconfiguration=factory.RelatedFactoryList(
                EdxUtilRatelimitconfigurationFactory,
                "changed_by",
                size=3,
                changed_by_id=factory.SelfAttribute("..id"),
            ),
            verify_student_historicalverificationdeadline=factory.RelatedFactoryList(
                EdxVerifyStudentHistoricalverificationdeadlineFactory,
                "history_user",
                size=3,
                history_user_id=factory.SelfAttribute("..id"),
            ),
        )

    id = factory.Sequence(lambda n: n + 1)
    username = factory.Sequence(lambda n: f"{faker.user_name()}{n}")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.Faker("password")
    email = factory.Faker("email")
    is_staff = False
    is_superuser = False
    is_active = True
    date_joined = factory.Faker("date_time")
    last_login = factory.Faker("date_time")

    auth_registration = factory.RelatedFactory(
        EdxAuthRegistrationFactory, user_id=factory.SelfAttribute("..id")
    )
    auth_userprofile = factory.RelatedFactory(
        EdxAuthUserprofileFactory, user_id=factory.SelfAttribute("..id")
    )
    auth_user_groups = factory.RelatedFactory(
        EdxAuthUserGroupsFactory, user_id=factory.SelfAttribute("..id")
    )
    bulk_email_courseemail = factory.RelatedFactoryList(
        EdxBulkEmailCourseemailFactory,
        "sender",
        size=3,
        sender_id=factory.SelfAttribute("..id"),
    )
    bulk_email_optout = factory.RelatedFactoryList(
        EdxBulkEmailOptoutFactory,
        "user",
        size=3,
        user_id=factory.SelfAttribute("..id"),
    )
    certificates_generatedcertificate = factory.RelatedFactoryList(
        EdxCertificatesGeneratedCertificateFactory,
        "user",
        size=3,
        user_id=factory.SelfAttribute("..id"),
    )
    course_groups_courseusergroup_users = factory.RelatedFactoryList(
        EdxCourseGroupsCourseusergroupUsersFactory,
        "user",
        size=3,
        user_id=factory.SelfAttribute("..id"),
    )
    course_groups_cohortmembership = factory.RelatedFactoryList(
        EdxCourseGroupsCohortmembershipFactory,
        "user",
        size=3,
        user_id=factory.SelfAttribute("..id"),
    )
    courseware_offlinecomputedgrade = factory.RelatedFactoryList(
        EdxCoursewareOfflinecomputedgradeFactory,
        "user",
        size=3,
        user_id=factory.SelfAttribute("..id"),
    )
    courseware_studentmodule = factory.RelatedFactoryList(
        EdxCoursewareStudentmoduleFactory,
        "student",
        size=3,
        student_id=factory.SelfAttribute("..id"),
    )
    courseware_xmodulestudentinfofield = factory.RelatedFactoryList(
        EdxCoursewareXmodulestudentinfofieldFactory,
        "student",
        size=3,
        student_id=factory.SelfAttribute("..id"),
    )
    courseware_xmodulestudentprefsfield = factory.RelatedFactoryList(
        EdxCoursewareXmodulestudentprefsfieldFactory,
        "student",
        size=3,
        student_id=factory.SelfAttribute("..id"),
    )
    django_comment_client_role_users = factory.RelatedFactoryList(
        EdxDjangoCommentClientRoleUsersFactory,
        "user",
        size=3,
        user_id=factory.SelfAttribute("..id"),
    )
    instructor_task_instructortask = factory.RelatedFactoryList(
        EdxInstructorTaskInstructortaskFactory,
        "requester",
        size=3,
        requester_id=factory.SelfAttribute("..id"),
    )
    notify_settings = factory.RelatedFactoryList(
        EdxNotifySettingFactory,
        "user",
        size=3,
        user_id=factory.SelfAttribute("..id"),
    )
    payment_useracceptance = factory.RelatedFactoryList(
        EdxPaymentUseracceptanceFactory,
        "user",
        size=3,
        user_id=factory.SelfAttribute("..id"),
    )
    proctoru_proctoruexam = factory.RelatedFactoryList(
        EdxProctoruProctoruexamFactory,
        "user",
        size=3,
        user_id=factory.SelfAttribute("..id"),
    )
    proctoru_proctoruuser = factory.RelatedFactory(
        EdxProctoruProctoruuserFactory, student_id=factory.SelfAttribute("..id")
    )
    student_anonymoususerid = factory.RelatedFactoryList(
        EdxStudentAnonymoususeridFactory,
        "user",
        size=3,
        user_id=factory.SelfAttribute("..id"),
    )
    student_courseaccessrole = factory.RelatedFactoryList(
        EdxStudentCourseaccessroleFactory,
        "user",
        size=3,
        user_id=factory.SelfAttribute("..id"),
    )
    student_courseenrollment = factory.RelatedFactoryList(
        EdxStudentCourseenrollmentFactory,
        "user",
        size=3,
        user_id=factory.SelfAttribute("..id"),
    )
    student_historicalcourseenrollment_history_user = factory.RelatedFactoryList(
        EdxStudentHistoricalcourseenrollmentFactory,
        "history_user",
        size=3,
        history_user_id=factory.SelfAttribute("..id"),
        user_id=factory.SelfAttribute("..id"),
    )
    student_historicalcourseenrollment_user = factory.RelatedFactoryList(
        EdxStudentHistoricalcourseenrollmentFactory,
        "user",
        size=3,
        user_id=factory.SelfAttribute("..id"),
        history_user_id=factory.SelfAttribute("..id"),
    )
    student_loginfailure = factory.RelatedFactoryList(
        EdxStudentLoginfailureFactory,
        "user",
        size=3,
        user_id=factory.SelfAttribute("..id"),
    )
    student_pendingemailchange = factory.RelatedFactory(
        EdxStudentPendingemailchangeFactory, user_id=factory.SelfAttribute("..id")
    )
    student_userstanding_user = factory.RelatedFactory(
        EdxStudentUserstandingFactory,
        changed_by_id=factory.SelfAttribute("..id"),
        user_id=factory.SelfAttribute("..id"),
    )
    user_api_userpreference = factory.RelatedFactoryList(
        EdxUserApiUserpreferenceFactory,
        "user",
        size=3,
        user_id=factory.SelfAttribute("..id"),
    )
    verify_student_softwaresecurephotoverification_reviewing_user = (
        factory.RelatedFactoryList(
            EdxVerifyStudentSoftwaresecurephotoverificationFactory,
            "reviewing_user",
            size=3,
            reviewing_user_id=factory.SelfAttribute("..id"),
            user_id=factory.SelfAttribute("..id"),
        )
    )
    verify_student_softwaresecurephotoverification_user = factory.RelatedFactoryList(
        EdxVerifyStudentSoftwaresecurephotoverificationFactory,
        "user",
        size=3,
        user_id=factory.SelfAttribute("..id"),
        reviewing_user_id=factory.SelfAttribute("..id"),
    )
