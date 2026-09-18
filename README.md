# NYC Taxi Analytics Dashboard 🚕📊

An interactive analytics dashboard for exploring **NYC Yellow Taxi Trip Records** using Flask, PostgreSQL, SQLAlchemy, Tailwind CSS, and Apache ECharts.

The dashboard provides interactive trip, revenue, payment, and location analytics with dynamic filters that update the visualizations automatically.

---

## 🚀 Features

* 📊 Interactive dashboard with KPI cards
* 🚕 NYC Yellow Taxi trip analysis
* 💰 Revenue analytics
* 🕐 Trips and revenue by hour
* 📅 Trips and revenue by day
* 💳 Payment type analysis
* 📍 Pickup and dropoff zone analysis
* 🔄 Interactive Pickup/Dropoff zone chart toggle
* 🔎 Dynamic multi-filter system
* ⚡ Automatic dashboard updates when filters change
* 📈 Interactive Apache ECharts visualizations
* 🗄️ PostgreSQL database with SQLAlchemy ORM
* 🔌 REST-style Flask APIs

### Available Filters

* Date range
* Payment type
* Pickup zone
* Dropoff zone

All filter options are populated dynamically from the database.

---

## 🛠️ Tech Stack

| Technology     | Purpose                   |
| -------------- | ------------------------- |
| Python         | Backend development       |
| Flask          | Web framework & REST APIs |
| PostgreSQL     | Database                  |
| SQLAlchemy     | ORM & database queries    |
| Pandas         | Data processing           |
| Parquet        | Dataset storage           |
| Tailwind CSS   | UI styling                |
| Apache ECharts | Data visualization        |
| JavaScript     | Frontend logic            |

---

## 🏗️ Architecture

```text
NYC Taxi Dataset
       ↓
    Pandas
       ↓
Data Cleaning
       ↓
   PostgreSQL
       ↓
   SQLAlchemy
       ↓
  Flask Services
       ↓
    Flask APIs
       ↓
   JavaScript
       ↓
  Apache ECharts
       ↓
 Interactive Dashboard
```

---

## 📁 Project Structure

```text
nyc-taxi-ai-dashboard/
│
├── app/
│   ├── db/
│   │   └── database.py
│   │
│   ├── models/
│   │   └── taxi_trip.py
│   │
│   ├── routes/
│   │   └── api.py
│   │
│   ├── services/
│   │   └── taxi_service.py
│   │
│
```
