""" Factory for creating infra services """


from .file import FileService


class ServiceFactory:
    def make_file_service(self, *args):
        return FileService()
