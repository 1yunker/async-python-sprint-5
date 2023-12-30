from models.models import File as FileModel
from schemas.file import FileUpload

from .base import RepositoryDB


class RepositoryFile(RepositoryDB[FileModel, FileUpload, FileUpload]):
    pass


file_crud = RepositoryFile(FileModel)
