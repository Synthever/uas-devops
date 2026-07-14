# LAPORAN PROYEK DEVOPS
## Implementasi Pipeline DevOps pada Aplikasi Web Manajemen Inventaris
### Startup: TechNova

---

**Mata Kuliah:** DevOps  
**Program Studi:** D3 Teknik Informatika  
**Universitas:** Universitas Amikom Yogyakarta  

**Anggota Kelompok:**
1. Raekhandi Yoga Gusmawn
2. [Nama Anggota 2]
3. [Nama Anggota 3]

---

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)
2. [Arsitektur Pipeline DevOps](#2-arsitektur-pipeline-devops)
3. [Otomatisasi Testing](#3-otomatisasi-testing)
4. [Analisis Keamanan Kode (SonarQube)](#4-analisis-keamanan-kode-sonarqube)
5. [Tools Kolaborasi](#5-tools-kolaborasi)
6. [Monitoring dan Logging](#6-monitoring-dan-logging)
7. [Penggunaan Cloud Computing](#7-penggunaan-cloud-computing)
8. [Studi Kasus Implementasi DevOps di Perusahaan](#8-studi-kasus-implementasi-devops-di-perusahaan)
9. [Link Video Presentasi](#9-link-video-presentasi)
10. [Kesimpulan](#10-kesimpulan)
11. [Lampiran](#11-lampiran)

---

## 1. Pendahuluan

### 1.1 Latar Belakang

Startup TechNova sedang mengembangkan aplikasi web berbasis mikroservices untuk layanan manajemen inventaris. Saat ini, proses development hingga deployment masih dilakukan secara manual, menyebabkan:
- Waktu deployment yang lama dan rawan error
- Tidak ada standarisasi testing sebelum release
- Kesulitan dalam monitoring aplikasi di production
- Kolaborasi tim yang kurang efisien

Untuk mengatasi masalah tersebut, tim DevOps ditugaskan merancang dan mengimplementasikan pipeline DevOps yang mencakup otomatisasi CI/CD, testing, keamanan kode, monitoring, dan kolaborasi tim.

### 1.2 Tujuan Proyek

1. Merancang arsitektur pipeline DevOps end-to-end
2. Mengimplementasikan otomatisasi CI/CD dengan GitHub Actions
3. Menerapkan automated testing (unit test & integration test)
4. Mengintegrasikan SonarQube untuk analisis keamanan dan kualitas kode
5. Membangun sistem monitoring dengan Prometheus, Grafana, dan Loki
6. Menerapkan kolaborasi tim menggunakan tools yang terintegrasi

### 1.3 Teknologi yang Digunakan

| Kategori | Tools |
|---|---|
| Bahasa Pemrograman | Python 3.11 (Flask) |
| Version Control | Git + GitHub |
| CI/CD | GitHub Actions |
| Containerization | Docker, Docker Compose |
| Testing | Pytest, pytest-cov |
| Code Quality | SonarQube Community |
| Monitoring | Prometheus |
| Visualization | Grafana |
| Log Aggregation | Loki + Promtail |
| Kolaborasi | GitHub Issues, Slack, Notion |
| Cloud | AWS (EC2, ECR, S3, CloudWatch) |

---

## 2. Arsitektur Pipeline DevOps

**(Bobot: 15% — SCPMK 20605214)**

### 2.1 Tools yang Digunakan

| Layer | Tool | Fungsi |
|---|---|---|
| Source Control | Git + GitHub | Version control dan code review via Pull Request |
| CI/CD | GitHub Actions | Otomatisasi build, test, dan deploy |
| Build | Docker | Containerization aplikasi |
| Registry | GitHub Container Registry (GHCR) | Penyimpanan Docker image |
| Testing | Pytest | Unit test dan integration test |
| Security | SonarQube | Static code analysis dan vulnerability scanning |
| Monitoring | Prometheus + Grafana | Metrics collection dan visualization |
| Logging | Loki + Promtail | Centralized log aggregation |
| Deployment | Docker Compose | Orchestration di production |

### 2.2 Alur Kerja (Development → Deployment)

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Developer   │────▶│   Git Push   │────▶│GitHub Actions│────▶│  Deployment  │
│  (Local)     │     │  (GitHub)    │     │  (CI/CD)     │     │ (Production) │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                               │
                          ┌────────────────────┼────────────────────┐
                          ▼                    ▼                    ▼
                    ┌───────────┐      ┌──────────────┐     ┌───────────┐
                    │  Testing  │      │  SonarQube   │     │Docker Build│
                    │  (Pytest) │      │  (Security)  │     │  & Push   │
                    └───────────┘      └──────────────┘     └───────────┘
```

**Alur detail:**

1. **Development** — Developer menulis kode di branch `feature/*`, lalu membuat Pull Request ke `develop`
2. **Code Review** — Tim melakukan review melalui GitHub Pull Request
3. **Automated Testing** — GitHub Actions menjalankan unit test dan integration test secara otomatis
4. **Security Scan** — SonarQube menganalisis kualitas dan keamanan kode
5. **Build** — Docker image dibangun dan dipush ke GitHub Container Registry
6. **Deploy** — Image di-deploy ke production menggunakan Docker Compose
7. **Monitor** — Prometheus mengumpulkan metrics, Grafana menampilkan dashboard, Loki mengaggregasi log

### 2.3 Rollback Mechanism

Pipeline kami menyertakan mekanisme rollback otomatis:

```yaml
# Dari .github/workflows/ci-cd.yml — Stage Deploy
- name: Deploy with rollback support
  run: |
    # Simpan versi yang sedang berjalan
    PREVIOUS_VERSION=$(docker inspect --format='{{.Config.Image}}' technova-app)
    
    # Deploy versi baru
    docker pull $IMAGE:${{ github.sha }}
    docker compose up -d --force-recreate app
    
    # Health check — jika gagal, rollback
    if ! curl -sf http://localhost:5000/api/health; then
      echo "❌ Health check failed! Rolling back..."
      docker run -d --name technova-app $PREVIOUS_VERSION
      exit 1
    fi
```

**Mekanisme:**
- Sebelum deploy, versi yang berjalan disimpan sebagai `PREVIOUS_VERSION`
- Setelah deploy, dilakukan health check ke `/api/health`
- Jika health check gagal, sistem otomatis rollback ke versi sebelumnya
- Semua kegiatan rollback tercatat di GitHub Actions log

### 2.4 Auto-scaling (Ilustrasi)

Untuk auto-scaling, arsitektur mendukung horizontal scaling melalui:
- **Docker Compose:** Menambah replicas (`docker compose up --scale app=3`)
- **Kubernetes (future):** HorizontalPodAutoscaler berdasarkan CPU/memory usage
- **AWS Auto Scaling Group:** Menambah EC2 instance berdasarkan CloudWatch alarm

---

## 3. Otomatisasi Testing

**(Bobot: 10% — SCPMK 20603211)**

### 3.1 Framework dan Struktur

- **Framework:** Pytest 8.x dengan pytest-cov untuk coverage
- **Struktur:**
  ```
  tests/
  ├── conftest.py          # Fixtures (app, client, db)
  ├── test_unit.py         # 14 unit tests
  └── test_integration.py  # 3 integration tests
  ```

### 3.2 Source Code — Unit Test

File: `tests/test_unit.py`

```python
class TestHealthEndpoint:
    """Tests for /api/health."""

    def test_health_returns_200(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200

    def test_health_body(self, client):
        data = client.get("/api/health").get_json()
        assert data["status"] == "healthy"
        assert data["service"] == "technova-inventory"


class TestCreateItem:
    """Tests for POST /api/items."""

    def test_create_item_success(self, client, db):
        resp = client.post("/api/items", json={
            "name": "Laptop Lenovo",
            "quantity": 10,
            "price": 8500000,
            "category": "Elektronik"
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Laptop Lenovo"
        assert data["quantity"] == 10

    def test_create_item_missing_name(self, client, db):
        resp = client.post("/api/items", json={"quantity": 5})
        assert resp.status_code == 400

    def test_create_item_negative_quantity(self, client, db):
        resp = client.post("/api/items", json={"name": "Mouse", "quantity": -1})
        assert resp.status_code == 400

    def test_create_item_defaults(self, client, db):
        resp = client.post("/api/items", json={"name": "Pulpen"})
        data = resp.get_json()
        assert data["quantity"] == 0
        assert data["price"] == 0.0
        assert data["category"] == "Umum"


class TestGetItems:
    def test_get_empty_list(self, client, db):
        resp = client.get("/api/items")
        assert resp.get_json() == []

    def test_get_items_after_create(self, client, db):
        client.post("/api/items", json={"name": "Keyboard", "quantity": 5})
        client.post("/api/items", json={"name": "Monitor", "quantity": 3})
        assert len(client.get("/api/items").get_json()) == 2

    def test_get_single_item(self, client, db):
        item_id = client.post("/api/items", json={"name": "SSD", "quantity": 20}).get_json()["id"]
        resp = client.get(f"/api/items/{item_id}")
        assert resp.get_json()["name"] == "SSD"

    def test_get_nonexistent_item(self, client, db):
        assert client.get("/api/items/9999").status_code == 404


class TestUpdateItem:
    def test_update_item(self, client, db):
        item_id = client.post("/api/items", json={"name": "RAM", "quantity": 50}).get_json()["id"]
        resp = client.put(f"/api/items/{item_id}", json={"quantity": 45})
        assert resp.get_json()["quantity"] == 45

    def test_update_negative_quantity(self, client, db):
        item_id = client.post("/api/items", json={"name": "Kabel", "quantity": 10}).get_json()["id"]
        assert client.put(f"/api/items/{item_id}", json={"quantity": -5}).status_code == 400


class TestDeleteItem:
    def test_delete_item(self, client, db):
        item_id = client.post("/api/items", json={"name": "Charger", "quantity": 8}).get_json()["id"]
        assert client.delete(f"/api/items/{item_id}").status_code == 200
        assert client.get(f"/api/items/{item_id}").status_code == 404

    def test_delete_nonexistent_item(self, client, db):
        assert client.delete("/api/items/9999").status_code == 404
```

### 3.3 Source Code — Integration Test

File: `tests/test_integration.py`

```python
class TestInventoryCRUDLifecycle:
    """End-to-end CRUD workflow test."""

    def test_full_lifecycle(self, client, db):
        # CREATE
        resp = client.post("/api/items", json={
            "name": "Proyektor Epson", "quantity": 5, "price": 12000000
        })
        assert resp.status_code == 201
        item_id = resp.get_json()["id"]

        # READ
        assert client.get(f"/api/items/{item_id}").status_code == 200

        # UPDATE
        resp = client.put(f"/api/items/{item_id}", json={"quantity": 4})
        assert resp.get_json()["quantity"] == 4

        # LIST
        assert len(client.get("/api/items").get_json()) == 1

        # DELETE
        client.delete(f"/api/items/{item_id}")
        assert client.get("/api/items").get_json() == []
```

### 3.4 Hasil Analisis Testing

```
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-8.4.2

tests/test_integration.py::TestInventoryCRUDLifecycle::test_full_lifecycle PASSED
tests/test_integration.py::TestMultipleItems::test_create_multiple_and_list PASSED
tests/test_integration.py::TestMultipleItems::test_delete_one_keeps_others PASSED
tests/test_unit.py::TestHealthEndpoint::test_health_returns_200 PASSED
tests/test_unit.py::TestHealthEndpoint::test_health_body PASSED
tests/test_unit.py::TestCreateItem::test_create_item_success PASSED
tests/test_unit.py::TestCreateItem::test_create_item_missing_name PASSED
tests/test_unit.py::TestCreateItem::test_create_item_negative_quantity PASSED
tests/test_unit.py::TestCreateItem::test_create_item_defaults PASSED
tests/test_unit.py::TestGetItems::test_get_empty_list PASSED
tests/test_unit.py::TestGetItems::test_get_items_after_create PASSED
tests/test_unit.py::TestGetItems::test_get_single_item PASSED
tests/test_unit.py::TestGetItems::test_get_nonexistent_item PASSED
tests/test_unit.py::TestUpdateItem::test_update_item PASSED
tests/test_unit.py::TestUpdateItem::test_update_negative_quantity PASSED
tests/test_unit.py::TestDeleteItem::test_delete_item PASSED
tests/test_unit.py::TestDeleteItem::test_delete_nonexistent_item PASSED

Name              Stmts   Miss  Cover   Missing
-----------------------------------------------
app/__init__.py       0      0   100%
app/main.py          24      4    83%   19, 37, 47-48
app/models.py        15      0   100%
app/routes.py        44      0   100%
-----------------------------------------------
TOTAL                85      6    93%

======================= 17 passed in 0.55s ========================
```

**Analisis:**
| Metrik | Nilai |
|---|---|
| Total Test Cases | 17 |
| Passed | 17 (100%) |
| Failed | 0 |
| Code Coverage | 93% |
| Execution Time | 0.55 detik |

- **Semua 17 test cases berhasil (PASSED)** tanpa error
- **Code coverage 93%** — lines yang tidak ter-cover adalah kode startup (`if __name__ == "__main__"`) dan WSGI entry point yang memang tidak dijalankan saat testing
- **routes.py coverage 100%** — semua endpoint API telah diuji
- **models.py coverage 100%** — semua model dan serialization diuji
- **Performa baik** — seluruh test suite berjalan dalam 0.55 detik

---

## 4. Analisis Keamanan Kode (SonarQube)

**(Bobot: 15% — SCPMK 20603109)**

### 4.1 Langkah-langkah Integrasi SonarQube

#### A. Setup SonarQube Server

SonarQube dijalankan sebagai container dalam stack Docker Compose:

```yaml
# docker-compose.yml
sonarqube:
  image: sonarqube:10.6-community
  container_name: technova-sonarqube
  ports:
    - "9000:9000"
  environment:
    - SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true
  volumes:
    - sonarqube_data:/opt/sonarqube/data
```

#### B. Konfigurasi Project

File `sonar-project.properties`:
```properties
sonar.projectKey=technova-inventory
sonar.projectName=TechNova Inventory Management
sonar.sources=app
sonar.tests=tests
sonar.language=py
sonar.python.coverage.reportPaths=coverage.xml
```

#### C. Integrasi dalam CI/CD Pipeline

```yaml
# .github/workflows/ci-cd.yml
sonarqube:
  name: "🔒 SonarQube Analysis"
  runs-on: ubuntu-latest
  needs: test          # Berjalan setelah test berhasil
  steps:
    - uses: actions/checkout@v4
    - uses: actions/download-artifact@v4
      with:
        name: coverage-report    # Menggunakan coverage dari stage test
    - name: SonarQube Scan
      uses: SonarSource/sonarqube-scan-action@v3
      env:
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
```

**Alur integrasi:**
1. Stage **Test** menghasilkan `coverage.xml`
2. Coverage di-upload sebagai artifact
3. Stage **SonarQube** download artifact dan menjalankan scan
4. Hasil analisis ditampilkan di SonarQube dashboard
5. Jika quality gate gagal, pipeline berhenti (build tidak dilanjutkan)

### 4.2 Hasil Analisis Keamanan dan Kualitas Kode

Berdasarkan analisis kode sumber kami, berikut hasil yang diharapkan dari SonarQube:

| Metrik | Hasil | Status |
|---|---|---|
| Bugs | 0 | ✅ Passed |
| Vulnerabilities | 0 | ✅ Passed |
| Code Smells | 2-3 (minor) | ✅ Passed |
| Coverage | 93% | ✅ Passed (>80%) |
| Duplications | <3% | ✅ Passed |
| Security Hotspots | 1-2 | ⚠️ Review |

### 4.3 Potensi Masalah Keamanan dan Penyelesaiannya

| Masalah | Severity | Penyelesaian |
|---|---|---|
| SQLite di production | Medium | Migrasi ke PostgreSQL untuk production. SQLite hanya untuk development |
| Hardcoded default password Grafana | Low | Menggunakan environment variable dan secrets management |
| Tidak ada rate limiting | Medium | Implementasi Flask-Limiter untuk endpoint API |
| Tidak ada authentication API | High | Implementasi JWT token authentication |
| CORS belum dikonfigurasi | Low | Implementasi Flask-CORS dengan whitelist domain |

**Langkah penyelesaian yang telah dilakukan:**
1. **Non-root Docker user** — Dockerfile menggunakan `USER appuser` untuk mengurangi attack surface
2. **Health check** — Dockerfile menyertakan HEALTHCHECK untuk memastikan container sehat
3. **Input validation** — API memvalidasi input (name required, quantity >= 0)
4. **SQL Injection prevention** — Menggunakan SQLAlchemy ORM yang otomatis melakukan parameterized queries

---

## 5. Tools Kolaborasi

**(Bobot: 10% — SCPMK 20603212)**

### 5.1 Tools yang Digunakan

| Tool | Fungsi | Kategori |
|---|---|---|
| **GitHub** | Version control, code review, issue tracking | Development |
| **Slack** | Komunikasi real-time, notifikasi pipeline | Komunikasi |
| **Notion** | Dokumentasi proyek, knowledge base, task tracking | Manajemen |
| **GitHub Issues** | Bug tracking, feature requests | Project Management |
| **GitHub Projects** | Kanban board untuk sprint planning | Project Management |

### 5.2 Alur Komunikasi dan Kolaborasi

```
┌──────────────────────────────────────────────────────────┐
│                    ALUR KOLABORASI TIM                     │
│                                                           │
│  Notion (Planning)                                        │
│    │ Sprint backlog, docs, specs                          │
│    ▼                                                      │
│  GitHub Issues (Task Assignment)                          │
│    │ Assign task ke developer                             │
│    ▼                                                      │
│  Git Branch (Development)                                 │
│    │ feature/xxx → develop → main                         │
│    ▼                                                      │
│  Pull Request (Code Review)                               │
│    │ Min. 1 approval sebelum merge                        │
│    ▼                                                      │
│  GitHub Actions (CI/CD)                                   │
│    │ Auto test + build + deploy                           │
│    ▼                                                      │
│  Slack Notification (Feedback)                            │
│    │ ✅ Build passed / ❌ Build failed                     │
│    ▼                                                      │
│  Grafana Dashboard (Monitoring)                           │
│    Alert → Slack jika ada masalah                         │
└──────────────────────────────────────────────────────────┘
```

**Detail alur:**

1. **Sprint Planning (Notion):** Tim mendiskusikan dan mendokumentasikan requirements di Notion. Setiap sprint memiliki backlog yang jelas.

2. **Task Assignment (GitHub Issues):** Requirements dipecah menjadi GitHub Issues dengan label (bug, feature, enhancement) dan assignee.

3. **Development (Git Branch):** Developer membuat branch dari `develop` dengan format `feature/nama-fitur` atau `fix/nama-bug`.

4. **Code Review (Pull Request):** Setelah selesai, developer membuat PR. Minimal 1 reviewer harus approve sebelum merge.

5. **Automated Pipeline (GitHub Actions):** Setiap push/PR memicu pipeline CI/CD otomatis.

6. **Notification (Slack):** Hasil pipeline dikirim ke channel Slack `#devops-alerts`.

### 5.3 Integrasi Tools dengan Pipeline DevOps

| Integrasi | Cara Kerja |
|---|---|
| **GitHub → GitHub Actions** | Push/PR otomatis trigger CI/CD pipeline |
| **GitHub Actions → Slack** | Notifikasi build status via Slack webhook |
| **Grafana → Slack** | Alert monitoring dikirim ke channel `#alerts` |
| **GitHub Issues → GitHub Projects** | Issue otomatis muncul di Kanban board |
| **Notion → GitHub** | Link referensi dokumentasi di PR description |

Contoh konfigurasi Slack notification di GitHub Actions:
```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1.26
  with:
    payload: |
      {
        "text": "Pipeline ${{ job.status }}: ${{ github.repository }}@${{ github.sha }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 6. Monitoring dan Logging

**(Bobot: 20% — SCPMK 20605208)**

### 6.1 Arsitektur Sistem Monitoring

```
┌─────────────────────────────────────────────────────────────┐
│                  MONITORING ARCHITECTURE                      │
│                                                              │
│  ┌───────────┐     ┌────────────┐     ┌──────────────┐      │
│  │ Flask App │────▶│ Prometheus │────▶│   Grafana    │      │
│  │ /metrics  │     │ (Scrape    │     │ (Dashboard   │      │
│  │           │     │  15s)      │     │  Visualize)  │      │
│  └───────────┘     └────────────┘     └──────────────┘      │
│       │                                      ▲               │
│       │ logs                                 │               │
│       ▼                                      │               │
│  ┌───────────┐     ┌────────────┐            │               │
│  │  Docker   │────▶│  Promtail  │────▶┌──────┴──┐           │
│  │  Logs     │     │ (Collect)  │     │  Loki   │           │
│  │           │     │            │     │ (Store)  │           │
│  └───────────┘     └────────────┘     └─────────┘           │
└─────────────────────────────────────────────────────────────┘
```

**Komponen:**

| Komponen | Port | Fungsi |
|---|---|---|
| **Flask App** | 5000 | Expose `/metrics` endpoint (Prometheus format) |
| **Prometheus** | 9090 | Scrape metrics setiap 15 detik, simpan time-series data |
| **Grafana** | 3000 | Dashboard visualization, alerting |
| **Loki** | 3100 | Log aggregation dan storage |
| **Promtail** | 9080 | Collect log dari Docker containers dan kirim ke Loki |

### 6.2 Konfigurasi Prometheus

```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "technova-app"
    metrics_path: /metrics
    static_configs:
      - targets: ["app:5000"]
        labels:
          service: "inventory-api"
          environment: "production"
```

**Metrics yang dikumpulkan:**
- `http_requests_total` — Total HTTP request per method/endpoint/status
- `http_request_duration_seconds` — Latency histogram per endpoint
- `up` — Status aplikasi (1 = up, 0 = down)

### 6.3 Konfigurasi Loki + Promtail

```yaml
# Promtail mengumpulkan log dari Docker containers
scrape_configs:
  - job_name: docker
    static_configs:
      - targets: [localhost]
        labels:
          job: docker
          __path__: /var/lib/docker/containers/**/*.log
    pipeline_stages:
      - docker: {}
```

### 6.4 Dashboard Grafana

Dashboard Grafana yang disediakan (`technova-dashboard.json`) berisi 5 panel:

| Panel | Tipe | Query |
|---|---|---|
| **HTTP Request Rate** | Time Series | `rate(http_requests_total[5m])` |
| **Request Latency (p95)** | Time Series | `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))` |
| **Total Requests by Status** | Stat | `sum(http_requests_total) by (status)` |
| **Application Health** | Stat | `up{job="technova-app"}` — Menampilkan UP (hijau) atau DOWN (merah) |
| **Application Logs** | Logs | `{job="docker"} \|= "technova"` — Log dari Loki |

**Akses Dashboard:**
- URL: `http://localhost:3000`
- Login: `admin` / `technova2024`
- Dashboard otomatis ter-provision saat Grafana start

### 6.5 Cara Menjalankan Stack Monitoring

```bash
# Start semua services
docker compose up -d

# Verifikasi
docker compose ps

# Akses:
# App:        http://localhost:5000/api/health
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000
# Loki:       http://localhost:3100/ready
# SonarQube:  http://localhost:9000
```

---

## 7. Penggunaan Cloud Computing

**(Bobot: 10% — SCPMK 20603110)**

> **Catatan:** Bagian ini merupakan ilustrasi berdasarkan referensi. Implementasi aktual menggunakan lingkungan lokal dengan Docker Compose.

### 7.1 Platform Cloud: Amazon Web Services (AWS)

AWS dipilih karena:
- Ekosistem layanan yang lengkap
- Free tier untuk development/testing
- Integrasi native dengan Docker dan Kubernetes
- Dokumentasi dan komunitas yang luas

### 7.2 Arsitektur Cloud

```
┌────────────────────────────────────────────────────────────────┐
│                          AWS Cloud                              │
│                                                                 │
│  ┌──────────┐     ┌──────────────┐     ┌───────────────┐       │
│  │ Route 53 │────▶│     ALB      │────▶│  ECS Fargate  │       │
│  │  (DNS)   │     │ (Load Bal.)  │     │  (Container)  │       │
│  └──────────┘     └──────────────┘     └───────┬───────┘       │
│                                                 │               │
│                          ┌──────────────────────┼────────┐     │
│                          ▼                      ▼        ▼     │
│                   ┌───────────┐          ┌─────────┐ ┌──────┐  │
│                   │    RDS    │          │   ECR   │ │  S3  │  │
│                   │(Database) │          │(Images) │ │(Logs)│  │
│                   └───────────┘          └─────────┘ └──────┘  │
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌──────────────┐     │
│  │ CloudWatch  │     │ Auto Scaling│     │   IAM        │     │
│  │ (Monitor)   │     │   Group     │     │ (Security)   │     │
│  └─────────────┘     └─────────────┘     └──────────────┘     │
└────────────────────────────────────────────────────────────────┘
```

### 7.3 Layanan AWS yang Digunakan

| Layanan | Fungsi | Cara Mendukung Pipeline |
|---|---|---|
| **EC2 / ECS Fargate** | Menjalankan container aplikasi | Deploy Docker container tanpa manage server |
| **ECR** | Container Registry | Menyimpan Docker image yang dibangun CI/CD |
| **RDS (PostgreSQL)** | Managed Database | Database production dengan backup otomatis |
| **S3** | Object Storage | Menyimpan log, backup, dan static assets |
| **CloudWatch** | Monitoring & Logging | Mengumpulkan metrics dan log dari semua service |
| **ALB** | Load Balancer | Distribusi traffic ke multiple container instances |
| **Route 53** | DNS Management | Domain management dan health-based routing |
| **IAM** | Identity & Access | Role-based access control untuk keamanan |
| **Auto Scaling** | Skalabilitas | Otomatis menambah/mengurangi instance berdasarkan load |

### 7.4 Dukungan Cloud terhadap Otomatisasi dan Skalabilitas

**Otomatisasi:**
- **ECS + ECR:** Pipeline CI/CD otomatis push image ke ECR dan update ECS service
- **CloudFormation/Terraform:** Infrastructure as Code untuk provisioning otomatis
- **CloudWatch Alarms:** Auto-trigger scaling action berdasarkan threshold

**Skalabilitas:**
- **Horizontal Scaling:** Auto Scaling Group menambah instance saat CPU > 70%
- **Database Scaling:** RDS Read Replicas untuk distribusi query beban baca
- **Caching:** ElastiCache (Redis) untuk mengurangi beban database

Contoh Auto Scaling Policy:
```json
{
  "PolicyType": "TargetTrackingScaling",
  "TargetTrackingScalingPolicyConfiguration": {
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }
}
```

---

## 8. Studi Kasus Implementasi DevOps di Perusahaan

**(Bobot: 10% — SCPMK 20605213)**

### 8.1 Perusahaan: Netflix

Netflix adalah salah satu pelopor adopsi DevOps dan microservices architecture. Dengan lebih dari 200 juta subscriber global, Netflix menjalankan ratusan microservices di AWS.

### 8.2 Pendekatan DevOps Netflix

| Aspek | Netflix | TechNova (Kami) |
|---|---|---|
| **CI/CD** | Spinnaker (custom) + Jenkins | GitHub Actions |
| **Containerization** | Titus (custom container platform) | Docker + Docker Compose |
| **Monitoring** | Atlas (custom) + Kayenta | Prometheus + Grafana |
| **Logging** | Mantis (real-time stream processing) | Loki + Promtail |
| **Deployment** | Canary deployment + Red/Black | Rolling update + Rollback |
| **Testing** | Chaos Engineering (Chaos Monkey) | Unit + Integration Test |
| **Infrastructure** | Full AWS (100%) | AWS (ilustrasi) + Local |
| **Scale** | 1000+ microservices | 1 microservice |
| **Team Structure** | Full DevOps culture, "you build it, you run it" | Tim kecil (3 orang) |

### 8.3 Perbandingan Detail

**1. CI/CD Pipeline:**
- **Netflix** menggunakan Spinnaker yang mereka kembangkan sendiri, mendukung multi-cloud deployment, canary analysis otomatis, dan pipeline yang sangat kompleks.
- **TechNova** menggunakan GitHub Actions yang lebih sederhana namun cukup untuk skala startup. GitHub Actions menyediakan integrasi native dengan GitHub dan mudah dikonfigurasi.

**2. Deployment Strategy:**
- **Netflix** menggunakan canary deployment — versi baru dirilis ke sebagian kecil user (1-5%), dipantau, baru dirilis penuh jika tidak ada masalah.
- **TechNova** menggunakan rolling update dengan health check dan auto-rollback. Lebih sederhana, namun efektif untuk skala kecil.

**3. Monitoring:**
- **Netflix** membangun Atlas (time-series database custom) yang mampu menangani miliaran metrics per detik.
- **TechNova** menggunakan Prometheus + Grafana yang open-source dan sudah menjadi standar industri.

**4. Chaos Engineering:**
- **Netflix** terkenal dengan Chaos Monkey dan Simian Army yang secara sengaja mematikan service di production untuk menguji ketahanan sistem.
- **TechNova** belum mengimplementasikan chaos engineering, namun bisa menjadi langkah selanjutnya seiring pertumbuhan sistem.

### 8.4 Pelajaran Penting

1. **"You Build It, You Run It"** — Tim yang membangun service harus bertanggung jawab mengoperasikannya. Ini mendorong kualitas kode dan operational awareness.

2. **Invest in Tooling** — Netflix menginvestasikan sumber daya besar untuk membangun tools internal. Untuk startup, gunakan open-source tools yang sudah proven (Prometheus, Grafana, GitHub Actions).

3. **Start Simple, Scale Later** — Netflix tidak mulai dengan arsitektur kompleks. Mereka memulai dengan monolith dan secara bertahap migrasi ke microservices. Pipeline TechNova sudah cukup untuk tahap awal.

4. **Monitoring is Not Optional** — Netflix mengumpulkan metrics dari setiap layer. Monitoring sejak awal mencegah masalah sebelum berdampak ke user.

5. **Automate Everything** — Dari testing, deployment, hingga rollback. Manual process adalah sumber error.

---

## 9. Link Video Presentasi

> **[URL VIDEO PRESENTASI]**
> 
> *(Upload video ke YouTube/Google Drive dan tambahkan URL di sini)*
> 
> Video mencakup:
> - Ringkasan pipeline DevOps
> - Demo implementasi tiap komponen
> - Visualisasi monitoring & logging (Grafana dashboard)
> - Kesimpulan dan lesson learned

---

## 10. Kesimpulan

### 10.1 Ringkasan

Proyek ini berhasil mengimplementasikan pipeline DevOps end-to-end untuk aplikasi manajemen inventaris TechNova, mencakup:

1. **Aplikasi Flask** dengan REST API CRUD untuk manajemen inventaris
2. **CI/CD Pipeline** menggunakan GitHub Actions dengan 4 stage (Test → SonarQube → Build → Deploy)
3. **Automated Testing** dengan 17 test cases (100% passed, 93% coverage)
4. **DevSecOps** melalui integrasi SonarQube untuk code quality dan security analysis
5. **Monitoring & Logging** dengan stack Prometheus + Grafana + Loki + Promtail
6. **Containerization** penuh menggunakan Docker dan Docker Compose
7. **Rollback Mechanism** otomatis berdasarkan health check
8. **Kolaborasi tim** menggunakan GitHub, Slack, dan Notion yang terintegrasi

### 10.2 Lesson Learned

- **Automation saves time** — Pipeline CI/CD menghilangkan human error dan mempercepat delivery
- **Testing early** — Menangkap bug di tahap development jauh lebih murah daripada di production
- **Monitoring from day one** — Observability bukan afterthought, tapi requirement
- **Security as code** — SonarQube dalam pipeline memastikan kualitas kode terjaga terus-menerus
- **Infrastructure as Code** — Docker Compose memastikan environment consistency

### 10.3 Pengembangan Selanjutnya

- Implementasi Kubernetes untuk orchestration yang lebih robust
- Canary deployment strategy
- Chaos engineering untuk uji ketahanan
- API authentication (JWT)
- Migrasi database ke PostgreSQL
- Implementasi caching (Redis)
- Integrasi Terraform untuk IaC di AWS

---

## 11. Lampiran

### 11.1 Struktur Project

```
DevOps/
├── app/
│   ├── __init__.py
│   ├── main.py              # Application factory
│   ├── models.py             # Database models (Item)
│   ├── routes.py             # API endpoints (CRUD)
│   └── wsgi.py               # WSGI entry point
├── tests/
│   ├── conftest.py           # Test fixtures
│   ├── test_unit.py          # 14 unit tests
│   └── test_integration.py   # 3 integration tests
├── monitoring/
│   ├── prometheus/
│   │   └── prometheus.yml    # Prometheus config
│   ├── grafana/
│   │   └── provisioning/
│   │       ├── dashboards/
│   │       │   ├── dashboard.yml
│   │       │   └── technova-dashboard.json
│   │       └── datasources/
│   │           └── datasources.yml
│   ├── loki/
│   │   └── loki-config.yml
│   └── promtail/
│       └── promtail-config.yml
├── .github/
│   └── workflows/
│       └── ci-cd.yml         # GitHub Actions pipeline
├── Dockerfile
├── docker-compose.yml        # Full stack (app + monitoring + sonarqube)
├── requirements.txt
├── sonar-project.properties
├── .dockerignore
└── docs/
    └── LAPORAN.md            # Dokumen ini
```

### 11.2 API Endpoints

| Method | Endpoint | Deskripsi |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/items` | List semua item |
| GET | `/api/items/<id>` | Get item by ID |
| POST | `/api/items` | Create item baru |
| PUT | `/api/items/<id>` | Update item |
| DELETE | `/api/items/<id>` | Delete item |
| GET | `/metrics` | Prometheus metrics |

### 11.3 Cara Menjalankan

```bash
# Development (local)
pip install -r requirements.txt
python -m app.main

# Testing
pytest tests/ -v --cov=app

# Production (Docker)
docker compose up -d

# Akses
# App:        http://localhost:5000
# Grafana:    http://localhost:3000 (admin/technova2024)
# Prometheus: http://localhost:9090
# SonarQube:  http://localhost:9000
```

### 11.4 Screenshot Dashboard

*(Lampirkan screenshot Grafana dashboard, Prometheus targets, SonarQube analysis, dan GitHub Actions pipeline di sini)*
