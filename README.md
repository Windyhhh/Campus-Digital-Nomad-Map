<div align="center">

# 🗺️ Campus-Digital-Nomad-Map

### Real-time campus map with AI crowd-flow prediction.

A Flask full-stack campus map with ML-based crowd prediction, reservations and achievements — V3.0.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)

</div>

---

**Campus-Digital-Nomad-Map** is a Flask full-stack campus map that layers real-time campus data with **AI crowd-flow prediction**. It includes authentication, reservations, achievements, and a trained crowding model served through REST APIs.

> [!NOTE]
> 中文项目：校园数字游民地图——Flask 全栈 + AI 人流预测，实时校园地图 V3.0。

---

## Quickstart

```bash
git clone https://github.com/Windyhhh/Campus-Digital-Nomad-Map.git
cd Campus-Digital-Nomad-Map

pip install -r requirements.txt

# Init database
python init_db.py

# Run server
python run.py
# or app.py for the WSGI entry
```

On Windows use `start.bat`, on Linux `start.sh`.

---

## Features

- **Real-time campus map** — Flask front + REST API (`api_v1`, `api_v2`).
- **AI crowd prediction** — trained `crowding_model.pkl` served by `ml/predictor.py`.
- **Reservations & achievements** — full user flows with auth.

---

## Project Structure

```
Campus-Digital-Nomad-Map/
├── app.py / run.py           # entry points
├── campus_map/
│   ├── ml/predictor.py       # crowding prediction
│   ├── routes/               # api_v1, api_v2, auth, pages, predictions, reservations
│   └── utils/                # achievements, sample_data
├── models/crowding_model.pkl # trained model
├── init_db.py, deploy.py
└── requirements.txt
```

---

## License

MIT — free to use, modify and distribute.
