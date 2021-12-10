from test.integration.app.event_expecter import EventExpecter
from test.shared.infra.data.producer import DataProducer
from test.shared.infra.facade_mock import InfraFacadeMock
from test.util import TestCase
from unittest.mock import Mock

from OpenCast.app.controller.module import ControllerModule
from OpenCast.app.facade import AppFacade
from OpenCast.app.service.module import ServiceModule
from OpenCast.domain.service.factory import ServiceFactory
from OpenCast.infra.data.manager import DataManager, StorageType
from OpenCast.infra.data.repo.factory import RepoFactory


class ServiceTestCase(TestCase):
    def setUp(self):
        def execute_handler(handler, *args):
            handler(*args)

        app_executor = Mock()
        app_executor.submit = Mock(side_effect=execute_handler)
        self.app_facade = AppFacade(app_executor)

        repo_factory = RepoFactory()
        data_manager = DataManager(repo_factory)
        self.data_facade = data_manager.connect(StorageType.MEMORY)
        self.data_producer = DataProducer.make()

        self.media_player = Mock()
        self.downloader = Mock()
        self.video_parser = Mock()
        self.deezer = Mock()
        self.file_service = Mock()
        self.infra_facade = InfraFacadeMock()
        self.infra_facade.media_factory.make_player.return_value = self.media_player
        self.infra_facade.media_factory.make_downloader.return_value = self.downloader
        self.infra_facade.media_factory.make_video_parser.return_value = (
            self.video_parser
        )
        self.infra_facade.media_factory.make_deezer_service.return_value = self.deezer
        self.infra_facade.service_factory.make_file_service.return_value = (
            self.file_service
        )

        self.service_factory = ServiceFactory(self.infra_facade.service_factory)

        self.evt_expecter = EventExpecter(
            self.app_facade.cmd_dispatcher, self.app_facade.evt_dispatcher
        )

        ControllerModule(
            self.app_facade, self.infra_facade, self.data_facade, self.service_factory
        )
        ServiceModule(
            self.app_facade, self.infra_facade, self.data_facade, self.service_factory
        )
