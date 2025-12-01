# billing_system
A lightweight billing system built using FastAPI and PostgreSQL, designed as a short technical prototype for interview evaluation. This project demonstrates clean backend structure, simple UI integration, and end-to-end bill creation flow.


⭐ Overview

This prototype allows users to:

Create customer bills

Add multiple products with quantity & price

Calculate bill total automatically

Compute change denomination breakdown

Save bill details in PostgreSQL

Use a minimal HTML form as UI

The goal of this project is to showcase API design, data modeling, and FastAPI skills in a compact and production-style structure.

⚙️ Tech Stack

FastAPI – Backend framework

PostgreSQL – Database

Uvicorn – ASGI Server

Jinja2 – Templates for UI

Docker Compose – Optional setup


🚀 Running the Project
1️⃣ Clone
git clone https://github.com/<your-username>/fastapi-billing-system.git
cd fastapi-billing-system

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Configure Environment

Create .env:

DATABASE_URL=postgresql://postgres:password@localhost:5432/billing_db

4️⃣ Start Server
uvicorn app.main:app --reload

🧪 API Endpoints
Method	Endpoint	Description
GET	/	HTML billing UI
POST	/create-bill	Creates a new bill
🔮 Future Enhancements (Optional)

Downloadable PDF invoice

Customer & product management

Admin dashboard with analytics

Email integration

Authentication & role access

❤️ Purpose

This is a short, interview-focused prototype designed to show clean coding style, REST API development, and basic backend functionality with FastAPI.
