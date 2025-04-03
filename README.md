# 🎧 Music and Podcast Analytics Platform

A full-stack Flask web application for tracking, analyzing, and visualizing real-time music and podcast streaming metrics with Spotify integration. Built with PostgreSQL, SQLAlchemy, Plotly.js, and Flask.

![screenshot](https://raw.githubusercontent.com/bini1995/music-and-podcast-analytics-platform/main/screenshot.png)

---

## 🚀 Features

- 🔐 **User Authentication**: Register, login, logout, and 2FA support.
- 📊 **Dashboard**: Interactive analytics using Plotly.js for top songs and artists.
- 🧠 **Spotify API Integration**: Live querying and data sync with Spotify's public API.
- 🗃️ **PostgreSQL Storage**: Tracks plays, likes, shares, saves per track.
- 🧩 **Blueprint Architecture**: Modularized for scalability.
- 👤 **Admin Portal**: View users, moderate content, and analytics.
- 🌐 **REST API Endpoints**: `/spotify/visuals`, `/register`, `/login`, etc.

---

## 🛠️ Tech Stack

- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **Frontend**: Plotly.js, HTML5, JavaScript
- **Auth**: Flask-Login, Flask-WTF, pyotp (2FA)
- **Deploy**: Render.com (live link coming soon)
- **DevOps**: .env + Gunicorn for production

---

## 🔧 Setup Instructions

### 1. Clone the repo

```bash
git clone git@github.com:bini1995/music-and-podcast-analytics-platform.git
cd music-and-podcast-analytics-platform
```
