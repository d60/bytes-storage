from pathlib import Path
from uuid import uuid4

DEFAULT_STORAGE_PATH = Path('__bytes_storage__')


class BytesStorage:
    """
    Examples
    --------
    >>> from bytesStorage import BytesStorage

    >>> bs = BytesStorage()
    >>> bytes_obj = bs(b'This is a example bytes.')
    >>> print(bytes_obj)
    <Bytes uuid="15f9392f-8a48-4665-a3a3-549bcd60d0d1">

    >>> print(bytes_obj())
    b'This is a example bytes.'
    """
    _storages = []

    def __init__(self, storage_path = DEFAULT_STORAGE_PATH) -> None:
        self.storage_path = Path(storage_path)
        if self.storage_path in self._storages:
            raise ValueError(f'Storage {storage_path.name} is already exists.')

        self.storage_path.mkdir(exist_ok=True)
        self._storages.append(self.storage_path)
        self.clear()

    def _generate_id(self) -> str:
        return str(uuid4())

    def __call__(self, bytes, release_after_read = True):
        uuid = self._generate_id()
        path = self.storage_path / uuid
        return Bytes(bytes, uuid, path, release_after_read)

    def clear(self):
        for f in self.storage_path.iterdir():
            f.unlink(missing_ok=True)

    def delete(self):
        if self.storage_path in self._storages:
            self._storages.remove(self.storage_path)

        if self.storage_path.exists():
            self.clear()
            self.storage_path.rmdir()

    def __del__(self) -> None:
        self.delete()


class Bytes:
    def __init__(self, bytes, uuid, path: Path, release_after_read) -> None:
        self.uuid = uuid
        self.path = path
        self.release_after_read = release_after_read
        self.path.write_bytes(bytes)

    @property
    def released(self):
        return not self.path.exists()

    def released_check(self):
        if self.released:
            raise FileNotFoundError('Bytes ' + self.uuid + ' already released.')

    def release(self):
        self.released_check()
        self.path.unlink()

    def read(self) -> bytes:
        self.released_check()
        bytes = self.path.read_bytes()
        if self.release_after_read:
            self.release()
        return bytes

    def __call__(self):
        return self.read()

    def __bytes__(self):
        return self.read()

    def __add__(self, other) -> bytes:
        return bytes(self) + bytes(other)

    def __repr__(self) -> str:
        return (
            f'<Bytes uuid="{self.uuid}"'
            f'{" released" if self.released else ""}'
            '>'
        )

    def __del__(self) -> None:
        try:
            self.release()
        except:
            pass
