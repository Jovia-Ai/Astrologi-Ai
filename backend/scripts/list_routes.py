from __future__ import annotations

from backend.app.main import app


def main() -> None:
    rows = []
    for route in app.routes:
        path = getattr(route, "path", "")
        methods = sorted(list(getattr(route, "methods", []) or []))
        if not methods:
            continue
        rows.append((",".join(methods), path, route.name))
    rows.sort(key=lambda x: x[1])
    for methods, path, name in rows:
        print(f"{methods:12} {path:50} {name}")


if __name__ == "__main__":
    main()
