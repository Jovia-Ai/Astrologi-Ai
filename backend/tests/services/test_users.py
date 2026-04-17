from __future__ import annotations

from app.services import users as users_module


class _FakeTableQuery:
    def __init__(self, parent: "_FakeSupabaseAdmin", table_name: str) -> None:
        self._parent = parent
        self._table_name = table_name
        self._column_name: str | None = None
        self._value: str | None = None

    def delete(self) -> "_FakeTableQuery":
        return self

    def eq(self, column_name: str, value: str) -> "_FakeTableQuery":
        self._column_name = column_name
        self._value = value
        return self

    def execute(self) -> dict[str, str]:
        assert self._column_name is not None
        assert self._value is not None
        self._parent.cleanup_calls.append((self._table_name, self._column_name, self._value))
        if (self._table_name, self._column_name) in self._parent.failures:
            raise RuntimeError("cleanup failed")
        return {"status": "ok"}


class _FakeAuthAdmin:
    def __init__(self, parent: "_FakeSupabaseAdmin") -> None:
        self._parent = parent

    def delete_user(self, user_id: str, should_soft_delete: bool = False) -> dict[str, str]:
        self._parent.auth_delete_calls.append((user_id, should_soft_delete))
        return {"status": "ok"}


class _FakeSupabaseAdmin:
    def __init__(self, failures: set[tuple[str, str]] | None = None) -> None:
        self.failures = failures or set()
        self.cleanup_calls: list[tuple[str, str, str]] = []
        self.auth_delete_calls: list[tuple[str, bool]] = []
        self.auth = type("AuthNamespace", (), {})()
        self.auth.admin = _FakeAuthAdmin(self)

    def table(self, table_name: str) -> _FakeTableQuery:
        return _FakeTableQuery(self, table_name)


def test_delete_user_account_cleans_known_user_tables(monkeypatch) -> None:
    fake_admin = _FakeSupabaseAdmin()
    monkeypatch.setattr(users_module, "supabase_admin", fake_admin)

    result = users_module.delete_user_account("user-123")

    assert result.user_id == "user-123"
    assert result.warnings == ()
    assert len(fake_admin.cleanup_calls) == 13
    assert fake_admin.auth_delete_calls == [("user-123", False)]


def test_delete_user_account_collects_cleanup_warnings_but_deletes_auth_user(monkeypatch) -> None:
    fake_admin = _FakeSupabaseAdmin(
        failures={
            ("stories", "user_id"),
            ("profiles", "id"),
        }
    )
    monkeypatch.setattr(users_module, "supabase_admin", fake_admin)

    result = users_module.delete_user_account("user-123")

    assert set(result.warnings) == {"stories.user_id", "profiles.id"}
    assert fake_admin.auth_delete_calls == [("user-123", False)]
