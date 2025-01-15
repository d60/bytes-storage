from pathlib import Path
from uuid import uuid4

DEFAULT_STORAGE_PATH = Path('__bytes_storage__')


class BytesStorage:
    def __init__(self, storage_path = None) -> None:
        if not storage_path:
            storage_path = DEFAULT_STORAGE_PATH
        self.storage_path = Path(storage_path)
        if not self.storage_path.exists():
            try:
                self.storage_path.mkdir()
            except Exception as e:
                raise RuntimeError('Could not make directory.') from e
        self.clear()

    def _generate_id(self) -> str:
        return str(uuid4())

    def __call__(self, bytes, release_after_read = True):
        uuid = self._generate_id()
        path = self.storage_path / uuid
        return Bytes(bytes, uuid, path, release_after_read)

    def clear(self):
        for f in self.storage_path.iterdir():
            try:
                f.unlink(missing_ok=True)
            except:
                pass

    def delete(self):
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

    def __bytes__(self):
        return self.read()

    def __add__(self, other) -> bytes:
        return bytes(self) + bytes(other)

    def __repr__(self) -> str:
        return (
            f'<StorageBytes uuid="{self.uuid}"'
            f'{" released" if self.released else ""}'
            '>'
        )

    def __del__(self) -> None:
        try:
            self.release()
        except:
            pass
