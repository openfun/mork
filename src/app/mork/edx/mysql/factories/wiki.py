"""Factory classes for verify models."""

import factory

from mork.edx.mysql.models.wiki import WikiArticle, WikiArticlerevision

from .base import BaseSQLAlchemyModelFactory


class WikiArticleFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `wiki_article` table."""

    class Meta:
        """Factory configuration."""

        model = WikiArticle

    id = factory.Sequence(lambda n: n + 1)
    current_revision_id = factory.Sequence(lambda n: n + 1)
    created = factory.Faker("date_time")
    modified = factory.Faker("date_time")
    owner_id = factory.Sequence(lambda n: n + 1)
    group_id = factory.Sequence(lambda n: n + 1)
    group_read = factory.Faker("random_int", min=0, max=1)
    group_write = factory.Faker("random_int", min=0, max=1)
    other_read = factory.Faker("random_int", min=0, max=1)
    other_write = factory.Faker("random_int", min=0, max=1)


class WikiArticlerevisionFactory(BaseSQLAlchemyModelFactory):
    """Factory for the `wiki_articlerevision` table."""

    class Meta:
        """Factory configuration."""

        model = WikiArticlerevision

    id = factory.Sequence(lambda n: n + 1)
    revision_number = factory.Sequence(lambda n: n + 1)
    user_message = factory.Faker("text")
    automatic_log = factory.Faker("text")
    ip_address = ""
    user_id = factory.Sequence(lambda n: n + 1)
    modified = factory.Faker("date_time")
    created = factory.Faker("date_time")
    previous_revision_id = factory.Sequence(lambda n: n + 1)
    deleted = factory.Faker("random_int", min=0, max=1)
    locked = factory.Faker("random_int", min=0, max=1)
    article_id = factory.Sequence(lambda n: n + 1)
    content = factory.Faker("text", max_nb_chars=2000)
    title = factory.Faker("sentence")
