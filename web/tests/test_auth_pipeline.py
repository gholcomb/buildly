import logging

from django.conf import settings
from django.test import TestCase, Client, override_settings

import factories
from web import auth_pipeline

from workflow.models import CoreUser, Organization


class OAuthTest(TestCase):
    """
    Test cases for OAuth Provider interface
    """
    # Fake classes for testing
    class BackendTest(object):
        def __init__(self):
            self.WHITELISTED_EMAILS = []
            self.WHITELISTED_DOMAINS = []

        def setting(self, name, default=None):
            return self.__dict__.get(name, default)

    class CurrentPartialTest(object):
        def __init__(self, token):
            self.token = token

    def setUp(self):
        logging.disable(logging.WARNING)
        self.core_user = factories.CoreUser()
        self.org = factories.Organization(organization_uuid='12345')
        self.app = factories.Application(user=self.core_user, )

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_authorization_success(self):
        # set user's password
        self.core_user.set_password('1234')
        self.core_user.save()

        # change user's organization
        users_org = factories.Organization(name='Test Org')
        self.core_user.organization = users_org
        self.core_user.save()

        c = Client(HTTP_USER_AGENT='Test/1.0')

        # Get Authorization token
        authorize_url = '/oauth/token/?client_id={}'.format(self.app.client_id)

        data = {
            'grant_type': 'password',
            'username': self.core_user.username,
            'password': '1234',
        }

        response = c.post(authorize_url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json())
        self.assertIn('access_token_jwt', response.json())
        self.assertIn('expires_in', response.json())

    def test_create_organization_new_default_org(self):
        Organization.objects.get(name=settings.DEFAULT_ORG).delete()
        coreuser = factories.CoreUser(first_name='John', last_name='Lennon', organization=None)

        response = auth_pipeline.create_organization(core_user=coreuser, is_new_core_user=True)

        self.assertIn('is_new_org', response)
        self.assertTrue(response['is_new_org'])
        self.assertIn('organization', response)
        self.assertTrue(isinstance(response['organization'], Organization))
        self.assertEqual(response['organization'].name, settings.DEFAULT_ORG)

        coreuser.refresh_from_db()
        self.assertEqual(coreuser.organization, response['organization'])

    @override_settings(DEFAULT_ORG=None)
    def test_create_organization_new_username_org(self):
        coreuser = factories.CoreUser(first_name='John', last_name='Lennon')

        response = auth_pipeline.create_organization(core_user=coreuser, is_new_core_user=True)

        self.assertIn('is_new_org', response)
        self.assertTrue(response['is_new_org'])
        self.assertIn('organization', response)
        self.assertTrue(isinstance(response['organization'], Organization))
        self.assertEqual(response['organization'].name, coreuser.username)

        coreuser.refresh_from_db()
        self.assertEqual(coreuser.organization, response['organization'])

    @override_settings(DEFAULT_ORG=None)
    def test_create_organization_org_exists(self):
        coreuser = factories.CoreUser(first_name='John', last_name='Lennon')
        org = factories.Organization(name=coreuser.username)
        coreuser.organization = org
        coreuser.save()

        response = auth_pipeline.create_organization(core_user=coreuser, is_new_core_user=True)

        self.assertIn('is_new_org', response)
        self.assertFalse(response['is_new_org'])
        self.assertIn('organization', response)
        self.assertTrue(isinstance(response['organization'], Organization))
        self.assertEqual(response['organization'], org)

        coreuser.refresh_from_db()
        self.assertEqual(coreuser.organization, org)

    def test_create_organization_no_new_coreuser(self):
        coreuser = factories.CoreUser(first_name='John', last_name='Lennon')

        response = auth_pipeline.create_organization(core_user=coreuser, is_new_core_user=False)
        self.assertIsNone(response)

    def test_create_organization_no_coreuser(self):
        response = auth_pipeline.create_organization(core_user=None, is_new_core_user=True)
        self.assertIsNone(response)

    def test_create_organization_no_is_new_core_user(self):
        coreuser = factories.CoreUser(first_name='John', last_name='Lennon')

        response = auth_pipeline.create_organization(core_user=coreuser)
        self.assertIsNone(response)

    def test_auth_allowed_not_in_whitelist(self):
        factories.Organization(name=settings.DEFAULT_ORG)
        backend = self.BackendTest()
        details = {'email': self.core_user.email}
        response = auth_pipeline.auth_allowed(backend, details, None)
        template_content = response.content
        self.assertIn(b"You don't appear to have permissions to access "
                      b"the system.", template_content)
        self.assertIn(b"Please check with your organization to have access.",
                      template_content)

    def test_auth_allowed_in_whitelisted_domains_conf(self):
        factories.Organization(name=settings.DEFAULT_ORG)

        backend = self.BackendTest()
        backend.WHITELISTED_DOMAINS = ['testenv.com']
        details = {'email': 'test@testenv.com'}
        result = auth_pipeline.auth_allowed(backend, details, None)
        self.assertIsNone(result)
        self.assertIn('organization_uuid', details)

    def test_auth_allowed_multi_oauth_domain(self):
        self.org.oauth_domains = ['testenv.com']
        self.org.save()
        factories.Organization(name='Another Org',
                               oauth_domains=['testenv.com'])

        backend = self.BackendTest()
        details = {'email': self.core_user.email}
        response = auth_pipeline.auth_allowed(backend, details, None)
        template_content = response.content
        self.assertIn(b"You don't appear to have permissions to access "
                      b"the system.", template_content)
        self.assertIn(b"Please check with your organization to have access.",
                      template_content)

    def test_auth_allowed_no_whitelist_oauth_domain(self):
        backend = self.BackendTest()
        details = {'email': self.core_user.email}
        response = auth_pipeline.auth_allowed(backend, details, None)
        template_content = response.content
        self.assertIn(b"You don't appear to have permissions to access "
                      b"the system.", template_content)
        self.assertIn(b"Please check with your organization to have access.",
                      template_content)

    def test_auth_allowed_no_email(self):
        factories.Organization(name=settings.DEFAULT_ORG)
        backend = self.BackendTest()
        details = {}
        response = auth_pipeline.auth_allowed(backend, details, None)
        template_content = response.content
        self.assertIn(b"You don't appear to have permissions to access "
                      b"the system.", template_content)
        self.assertIn(b"Please check with your organization to have access.",
                      template_content)

    def test_create_organization(self):
        pass
