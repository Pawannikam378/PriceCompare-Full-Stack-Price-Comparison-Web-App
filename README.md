# 🛒 PriceCompare — Multi-Platform Price Comparison Web App

A full-stack web application that compares product prices across multiple e-commerce platforms.

Built using **React (Frontend)** and **FastAPI (Backend)**, this project aggregates product data and helps users find the best deal instantly.

---

## 🚀 Live Demo

Frontend: _(Add Vercel link)_  
Backend API: _(Add Render link)_

---

## 🎯 Features

- 🔍 Search products across platforms
- 💰 Compare prices (Amazon, Flipkart, Croma)
- ⭐ View ratings
- 🏆 Highlight cheapest option
- ⚡ Fast API response
- 🎨 Clean and responsive UI

---

## 🏗 Architecture

```
User → React Frontend → FastAPI Backend → Scrapers → Aggregated Results
```

---

## 🛠 Tech Stack

### Frontend
- React (Vite)
- Axios
- CSS

### Backend
- FastAPI
- Python
- Uvicorn

---

## 📂 Project Structure

```
price_compare/
│── backend/
│   │── main.py
│   │── scrapers.py
│   │── aggregator.py
│   │── requirements.txt
│
│── frontend/
│   │── src/
│   │── package.json
│
│── README.md
```

---

## ⚙️ Setup Instructions

### 🔹 Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs on:
```
http://localhost:8000
```

---

### 🔹 Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on:
```
http://localhost:5173
```

---

## 🔌 API Endpoint

### GET /search

```
/search?query=iphone
```

### Response:

```json
{
  "product": "iphone",
  "results": [
    {
      "platform": "Amazon",
      "price": 74999,
      "rating": 4.5,
      "link": "..."
    }
  ]
}
```

---

## 💡 How It Works

1. User enters product name
2. React sends request to FastAPI
3. Backend fetches data (simulated/scraped)
4. Aggregates results
5. Sorts by price
6. Returns response
7. UI displays comparison

---

## 🚀 Future Improvements

- Price history tracking
- Price drop alerts
- Real API integration
- User accounts
- Wishlist system
- ML-based price prediction

---

## ⚠ Disclaimer

This project uses simulated or limited scraping for educational purposes.  
Real-world applications should use official APIs and comply with platform policies.

---

## 👤 Author

Your Name  
Final Year Engineering Student  
Focused on Full Stack & AI Systems