# Swiss Ephemeris Setup

Astrologi-AI computes natal and transit charts via [PySwissEph](https://github.com/astrorigin/pyswisseph), which requires Swiss Ephemeris data files (`*.se1`) on disk. These files are **not tracked in git** — each environment fetches them at setup time.

## Why ephemeris is required

PySwissEph computes high-precision planetary positions by reading binary ephemeris files distributed by [Astrodienst](https://www.astro.com/swisseph/). Without them, `swe.calc_ut()` returns errors or, worse, falls back to noon defaults — producing subtly wrong charts. To prevent that, the backend has a **hard guard** at startup (`app.core.ephemeris_guard.assert_ephemeris_ready`) that refuses to launch if the required files are missing.

The required minimum set covers Sun, Moon, planets, and asteroids (Chiron etc.) for the 1800–2399 epoch chunk, which spans every birth date the app currently supports:

| File | Body | Epoch |
|---|---|---|
| `seas_18.se1` | Asteroids (Chiron, Pholus…) | 1800–2399 |
| `sepl_18.se1` | Planets | 1800–2399 |
| `semo_18.se1` | Moon | 1800–2399 |

The full Swiss Ephemeris distribution has many more files; the setup script only pulls these three. If you need broader coverage (other epochs, other asteroids), drop additional `*.se1` files into the same directory — `swe.set_ephe_path()` reads any file present.

## How to run setup

From repo root:

```bash
bash backend/scripts/setup_ephemeris.sh
```

The script is **idempotent** — files already present (and non-empty) are skipped. Safe to re-run after pulling, in CI, or after upgrading.

After setup, the backend will boot without errors:

```bash
PYTHONPATH=backend python -m uvicorn app.main:app
# → Swiss Ephemeris path set to /…/backend/ephemeris
```

## How to override the path

By default the script writes to `backend/ephemeris/` and the backend reads from the same directory (resolved relative to `backend/`).

To use a different location (e.g. shared cache on a server):

```bash
export SE_EPHE_PATH=/var/lib/swisseph
bash backend/scripts/setup_ephemeris.sh   # downloads into /var/lib/swisseph
PYTHONPATH=backend python -m uvicorn app.main:app   # reads from same path
```

The legacy env var `SWISSEPH_PATH` is still honored for backward compat. Order of precedence: `SE_EPHE_PATH` → `SWISSEPH_PATH` → `./ephemeris` (relative to `backend/`).

## CI / Deployment

| Environment | Where setup runs |
|---|---|
| Local dev | `bash backend/scripts/setup_ephemeris.sh` once after clone |
| Render.com | `render.yaml` `buildCommand` runs the script after `pip install` |
| GitHub Actions | Add a step that runs the script before tests (see "CI integration" below) |
| Docker | If using Docker, add `RUN bash backend/scripts/setup_ephemeris.sh` after copying the repo (see "Docker" below) |

### CI integration (when you add GitHub Actions)

```yaml
# Example .github/workflows/test.yml step
- name: Install Swiss Ephemeris
  run: bash backend/scripts/setup_ephemeris.sh
- name: Run tests
  run: pytest backend/tests
  env:
    PYTHONPATH: backend
```

### Docker (when you add a Dockerfile)

```dockerfile
WORKDIR /app
COPY . .
RUN pip install -r backend/requirements.txt
RUN bash backend/scripts/setup_ephemeris.sh
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### `EphemerisMissingError: Swiss Ephemeris missing required files…`
The backend startup guard fired. The error message lists the missing files. Run `bash backend/scripts/setup_ephemeris.sh` to fetch them. If you see this in production, your deploy build step is not running the script — fix the `buildCommand` (Render) or the equivalent for your platform.

### `curl: (6) Could not resolve host: www.astro.com`
No network access in the build environment. Options:
- Pre-populate the ephemeris directory in your image / volume.
- Mirror the files to your own object storage and patch `BASE_URL` in `setup_ephemeris.sh`.

### `WARNING: Failed to calculate Chiron: SwissEph file 'seas_18.se1' not found`
This message means the runtime guard didn't fire (perhaps the route is being called without going through `create_app()`, e.g. some test). Check that `seas_18.se1` is present at the configured path. If it is, verify the path resolution: `python -c "from app.core.config import settings; print(settings.swisseph_path)"`.

### Files downloaded but appear empty / corrupted
The setup script `--fail`s on HTTP errors and aborts on zero-byte files, so this is rare. If it happens, delete the file and re-run; the script will redownload.

### Files were tracked in git before — what happened to them?
The legacy `backend/ephe/` directory contained ~150 `.se1` files committed to git. As of `<this commit>`, those files are removed from history-going-forward and `backend/ephemeris/` is gitignored. Existing checkouts may still have the legacy directory locally; safe to delete it.

## Source of truth

Required file list lives in two places and **must be kept in sync**:
- `backend/scripts/setup_ephemeris.sh` → `REQUIRED_FILES`
- `backend/app/core/ephemeris_guard.py` → `REQUIRED_EPHE_FILES`

If you change one, change the other.
