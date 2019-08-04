import pytest

import factories


@pytest.fixture()
def logic_module():
    return factories.LogicModule.create(name='documents',
                                        endpoint_name='documents',
                                        endpoint='http://documentservice:8080')


@pytest.fixture()
def datamesh():
    lm1 = factories.LogicModule.create(name='location', endpoint_name='location',
                                       endpoint='http://locationservice:8080')
    lm2 = factories.LogicModule.create(name='documents', endpoint_name='documents',
                                       endpoint='http://documentservice:8080')
    lmm1 = factories.LogicModuleModel(logic_module_endpoint_name=lm1.endpoint_name, model='SiteProfile',
                                      endpoint='/siteprofiles/', lookup_field_name='uuid')
    lmm2 = factories.LogicModuleModel(logic_module_endpoint_name=lm2.endpoint_name, model='Document',
                                      endpoint='/documents/', lookup_field_name='id')
    relationship = factories.Relationship(origin_model=lmm1, related_model=lmm2, key='documents')
    return lm1, lm2, relationship
