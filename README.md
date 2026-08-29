<div align="center">

# 校园数字游民地图 | Campus-Digital-Nomad-Map

### Flask full-stack campus space management with AI crowd prediction.

A multi-role campus space booking system with real-time availability and ML-based crowding forecasts.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.0-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![AMap](https://img.shields.io/badge/AMap-API-FF6A00)](https://lbs.amap.com/)

</div>

---

**Campus-Digital-Nomad-Map** is a **Flask full-stack** campus space-management system. It provides multi-role booking (student / teacher / admin / visitor), interactive **AMap**-based maps, and a **random-forest** model that predicts future crowding so users can pick the best time to use a space.

> [!NOTE]
> 中文项目：校园数字游民活地图——Flask 全栈 + AI 拥挤度智能预测 + 多角色权限管理。

---

## Features

- **Multi-role access control** — RBAC with 4 roles (student, teacher, admin, visitor) built on Flask-Login and custom decorators.
- **Space booking** — online reserve / cancel / modify / review with automatic conflict detection.
- **AI crowding prediction** — random-forest model (scikit-learn) forecasts crowding for the next 6 hours.
- **Interactive map** — AMap (高德) API for campus space browsing and navigation.
- **Achievements & reports** — gamified achievements and user crowd-reporting.
- **Tested** — 67 test cases across 8 modules, all passing (100%).

---

## Architecture

```
┌──────────┐   ┌──────────────┐   ┌──────────────┐   ┌───────────┐
│  User    │──▶│ Frontend     │──▶│ Flask Backend│──▶│  Database │
│  (4 roles)│  │ Bootstrap/JS │   │  SQLAlchemy  │   │ (SQLite/MySQL)
└──────────┘   └──────────────┘   │  + ML model  │   └───────────┘
                                  └──────┬───────┘
                                         │
                                   ┌─────▼─────┐
                                   │ AMap API  │
                                   └───────────┘
```

The ML pipeline: historical data → preprocessing → feature engineering → random-forest training → evaluation → deployment; real-time data runs through the same trained model for live forecasts.

---

## Database

| Table | Purpose |
|-------|---------|
| `users` | accounts & roles |
| `spaces` | campus space info (location, capacity, type) |
| `reservations` | booking records & status |
| `crowding_data` | crowding level history |
| `reports` | user-reported crowding |
| `achievements` | gamified badges |

---

## Quickstart

```bash
git clone https://github.com/Windyhhh/Campus-Digital-Nomad-Map.git
cd Campus-Digital-Nomad-Map

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python init_db.py               # initialize database

python app.py                   # http://127.0.0.1:5000
```

For production: configure MySQL in `app.py`, run with Gunicorn (`gunicorn -w 4 -b 0.0.0.0:5000 app:app`) behind Nginx. An AMap developer key is required for map features.

---

## Project Structure

```
Campus-Digital-Nomad-Map/
├── app.py                  # Flask entry
├── init_db.py              # DB init
├── models/                 # SQLAlchemy models
├── ml/                     # random-forest model
├── templates/              # HTML views
├── static/                 # CSS / JS
└── requirements.txt
```

---

## License

MIT — free to use, modify and distribute.
