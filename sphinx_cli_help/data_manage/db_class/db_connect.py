from __future__ import annotations
from ...cfg import AppConfig


class DbConnect:
    def __init__(self) -> None:
        self._conn = str(AppConfig.root_path / AppConfig.resource_dir / AppConfig.db_name)

    @property
    def connection_str(self) -> str:
        """Gets connection_str value"""
        return self._conn
