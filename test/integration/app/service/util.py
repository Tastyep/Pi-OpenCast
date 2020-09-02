from test.integration.app.event_expecter import EventExpecter
from test.shared.infra.data.producer import DataProducer
from test.shared.infra.facade_mock import InfraFacadeMock
from test.util import TestCase
from unittest.mock import Mock

from OpenCast.app.controller.module import ControllerModule
from OpenCast.app.facade import AppFacade
from OpenCast.app.service.module import ServiceModule
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
        self.data_producer = DataProducer.make()
        self.data_producer.player().populate(self.data_facade)

        infraServiceFactory = Mock()
        self.service_factory = ServiceFactory(infraServiceFactory)

        self.downloader = Mock()
        self.video_parser = Mock()
        self.infra_facade = InfraFacadeMock()
        self.infra_facade.media_factory.make_downloader.return_value = self.downloader
        self.infra_facade.media_factory.make_video_parser.return_value = (
            self.video_parser
        )

        self.evt_expecter = EventExpecter(
            self.app_facade.cmd_dispatcher, self.app_facade.evt_dispatcher
        )

        ControllerModule(
            self.app_facade, self.infra_facade, self.data_facade, self.service_factory
        )
        ServiceModule(
            self.app_facade, self.infra_facade, self.data_facade, self.service_factory
        )
