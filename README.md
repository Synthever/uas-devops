# TechNova Inventory Management — DevOps Pipeline

Aplikasi web manajemen inventaris dengan pipeline DevOps lengkap.

## Quick Start

```bash
# Local development
pip install -r requirements.txt
python -m app.main

# Run tests
pytest tests/ -v --cov=app

# Full stack (app + monitoring)
docker compose up -d
```

## Stack

- **App:** Flask + SQLite + Gunicorn
- **CI/CD:** GitHub Actions (4 stages)
- **Testing:** Pytest (17 tests, 93% coverage)
- **Security:** SonarQube
- **Monitoring:** Prometheus + Grafana + Loki + Promtail

## Endpoints

| Method | URL | Description |
|---|---|---|
| GET | /api/health | Health check |
| GET | /api/items | List items |
| POST | /api/items | Create item |
| PUT | /api/items/:id | Update item |
| DELETE | /api/items/:id | Delete item |
| GET | /metrics | Prometheus metrics |

## Access (Docker Compose)

- App: http://localhost:5000
- Grafana: http://localhost:3000 (admin/technova2024)
- Prometheus: http://localhost:9090
- SonarQube: http://localhost:9000
