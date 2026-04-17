# Promptwars-Project
# 🚀 CrowdSense AI – Smart Crowd Anomaly Detection System

## 📌 Overview

**CrowdSense AI** is an intelligent real-time crowd monitoring system designed to improve physical event experiences in large-scale venues such as stadiums, concerts, and public gatherings.

It uses **machine learning (Isolation Forest)** to detect anomalies in crowd movement and density, helping reduce congestion, waiting time, and safety risks.

---

## 🎯 Problem Statement

Large events often face:

* Overcrowding in specific zones
* Long waiting times
* Poor crowd coordination
* Safety risks due to unexpected surges

👉 This project provides a **data-driven solution** to monitor and manage crowd behavior efficiently.

---

## 💡 Solution

CrowdSense AI:

* Collects crowd data (simulated or real-time)
* Analyzes patterns using anomaly detection
* Identifies unusual crowd behavior
* Displays insights via an interactive dashboard

---

## ⚙️ Tech Stack

* **Frontend/UI:** Streamlit
* **Backend:** Python
* **Machine Learning:** Scikit-learn (Isolation Forest)
* **Visualization:** Plotly
* **Deployment:** Google Cloud Run
* **Containerization:** Docker

---

## 🧠 Features

* 📊 Real-time crowd monitoring dashboard
* 🚨 Anomaly detection using ML
* 📍 Zone-wise crowd analysis (Gate A, Gate B, Food Court, Exit)
* 📈 Interactive graphs and visualizations
* ☁️ Cloud deployment (scalable & accessible)

---

## 🏗️ Project Structure

```
CrowdSense-AI/
│
├── app.py                  # Main Streamlit app
├── requirements.txt        # Dependencies
├── Dockerfile              # Container config
├── .streamlit/
│   └── config.toml         # Streamlit config
└── README.md               # Project documentation
```

---

## ▶️ How to Run Locally

### 1. Clone the repository

```
git clone https://github.com/your-username/crowdsense-ai.git
cd crowdsense-ai
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Run the app

```
streamlit run app.py
```

---

## ☁️ Deployment (Google Cloud Run)

```
gcloud run deploy crowdsense-ai \
--source . \
--port 8080 \
--region us-central1 \
--allow-unauthenticated \
--project YOUR_PROJECT_ID
```

---

## 🌐 Live Demo

👉 https://crowdsense-ai-294690858332.us-central1.run.app

---

## 📊 Use Cases

* Stadium crowd management
* Smart city monitoring
* Event safety systems
* Airport / railway station crowd control

---

## 🔮 Future Enhancements

* 🔗 Real-time IoT sensor integration
* 📱 Mobile alerts for authorities
* 🧭 Heatmaps for crowd movement
* 🤖 AI-based crowd prediction

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork this repo and submit a pull request.

---

## 📄 License

This project is for educational and research purposes.

---

## 👨‍💻 Author

Developed as part of an AI-based smart event management solution.

---
