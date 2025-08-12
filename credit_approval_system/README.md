# Credit Approval System (Django + DRF + Celery)

## Overview
This repository is a ready-to-run skeleton for the backend assignment. It includes:
- Django 4.x + Django REST Framework
- PostgreSQL
- Celery (Redis broker) for background ingestion
- Docker & docker-compose setup

## Quickstart
1. Copy `.env.example` to `.env` and adjust values.
2. Run:
   ```bash
   docker-compose up --build
   ```
3. The API will be available at `http://localhost:8000/api/`

### Background ingestion
Place `customer_data.xlsx` and `loan_data.xlsx` inside the project root, then run a Celery task, e.g.:
```bash
# inside the web container or via manage.py shell
from credit.tasks import ingest_customers_from_excel, ingest_loans_from_excel
ingest_customers_from_excel.delay('/code/customer_data.xlsx')
ingest_loans_from_excel.delay('/code/loan_data.xlsx')
```

## Endpoints
- `POST /api/register`
- `POST /api/check-eligibility`
- `POST /api/create-loan`
- `GET /api/view-loan/{loan_id}`
- `GET /api/view-loans/{customer_id}`

See assignment PDF for exact request/response specs.
