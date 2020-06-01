from test.integration.app.event_expecter import EventExpecter
from test.shared.infra.data.producer import DataProducer
from test.shared.infra.facade_mock import InfraFacadeMock
from test.util import TestCase
from unittest.mock import Mock

from OpenCast.app.facade import AppFacade
from OpenCast.domain.service.factory import ServiceFactory
from OpenCast.infra.data.facade import DataFacade
from OpenCast.infra.data.repo.factory import RepoFactory


class ServiceTestCase(TestCase):
    def setUp(self):
        def execute_handler(handler, *args):
            handler(*args)

        app_executor = Mock()
        app_executor.submit = Mock(side_effect=execute_handler)
        self.app_facade = AppFacade(app_executor)

        repo_factory = RepoFactory()
        self.data_facade = DataFacade(repo_factory)

        infraServiceFactory = Mock()
        self.service_factory = ServiceFactory(infraServiceFactory)

        self.infra_facade = InfraFacadeMock()
        self.evt_expecter = EventExpecter(
            self.app_facade.cmd_dispatcher, self.app_facade.evt_dispatcher
        )
        self.data_producer = DataProducer.make()
