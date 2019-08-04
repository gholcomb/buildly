import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

import workflow.models as wfm
from .fixtures import org


@pytest.mark.django_db()
class TestEmailTemplateModel:

    def test_create(self, org):
        tpl = wfm.EmailTemplate(
            organization=org,
            type=wfm.TEMPLATE_RESET_PASSWORD,
            subject='Custom subject',
            template="""
            Custom template
            {{ password_reset_link }}
            """
        )
        tpl.save()

        updated = wfm.EmailTemplate.objects.get(organization=org, type=wfm.TEMPLATE_RESET_PASSWORD)
        assert updated.subject == tpl.subject
        assert updated.template == tpl.template

    def test_create_fail_without_subj(self, org):
        tpl = wfm.EmailTemplate.objects.create(
            organization=org,
            type=wfm.TEMPLATE_RESET_PASSWORD
        )
        with pytest.raises(ValidationError):
            tpl.full_clean()
            tpl.save()

    def test_create_fail_unique_constraint(self, org):
        tpl = wfm.EmailTemplate(
            organization=org,
            type=wfm.TEMPLATE_RESET_PASSWORD,
            subject='Custom subject',
            template="""
            Custom template
            {{ password_reset_link }}
            """
        )
        tpl.save()
        tpl = wfm.EmailTemplate(
            organization=org,
            type=wfm.TEMPLATE_RESET_PASSWORD,
            subject='Another custom subject',
            template="""
            Another custom template
            {{ password_reset_link }}
            """
        )
        with pytest.raises(IntegrityError):
            tpl.save()

    def test_update(self, org):
        tpl = wfm.EmailTemplate.objects.create(
            organization=org,
            type=wfm.TEMPLATE_RESET_PASSWORD,
            subject='Custom subject',
            template="""
            Custom template
            {{ password_reset_link }}
            """
        )

        tpl.subject = 'Updated custom subject'
        tpl.template = """
            Updated custom template
            {{ password_reset_link }}
            """
        tpl.save()

        updated = wfm.EmailTemplate.objects.get(organization=org, type=wfm.TEMPLATE_RESET_PASSWORD)
        assert updated.subject == tpl.subject
        assert updated.template == tpl.template
