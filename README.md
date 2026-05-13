# Project Sahayak: The Worker-Centric AI Anti-Manager

**Project Sahayak** is an autonomous, Multi-Agent System (MAS) designed to empower gig economy workers by providing them with independent, profit-maximizing, and safety-conscious intelligence. It functions as a software proxy that sits between platform algorithms (Uber, Zomato, Swiggy) and the worker, restoring agency and improving financial/physical well-being.

---

## 🌟 Key  

- **Optimizer Agent:** Calculates **Real Hourly Rate (RHR)** in real-time by analyzing incoming gig pings, accounting for fuel costs and vehicle depreciation.
- **Biometric Sentinel:** Uses **AMD Ryzen™ AI NPU** to perform on-device fatigue detection from accelerometer and gyro data, prioritizing worker safety.
- **Financial Fiduciary:** Builds a **Tamper-Proof Digital Work History** for each worker using SHA-256 hash chaining, enabling access to micro-loans.
- **Mesh-Net Demand Sync:** Leverages **Bluetooth Low Energy (BLE)** to exchange demand heatmaps between offline Sahayak devices in low-connectivity areas.
- **i-LAVA V-2-V Interface:** A low-latency (RTF 0.480x), hands-free multilingual voice interface optimized with **RVQ-16** iterations for the AMD ecosystem.
- **Acoustic Engine Diagnostics:** Samples engine audio to detect mechanical issues before they lead to a breakdown.

---

## 🛠️ Technology Stack

- **Backend Orchestration:** Python 3.11, FastAPI, CrewAI
- **Hardward Acceleration:** AMD ROCm™ (GPU), AMD Ryzen™ AI (NPU via ONNX Runtime)
- **State Management:** Redis (Shared Scratchpad logic)
- **Mobile Foundation:** Android (Accessibility Services)
- **Storage:** SQLite (Local Ledger), PostgreSQL (Synced Cloud DB)
- **Voice Intelligence:** i-LAVA (optimized audio-vision pipeline)

---

## 🚦 Getting Started (Backend)

### Prerequisites
- **Docker Desktop**
- **AMD Drivers** (ROCm/Ryzen AI)

### Quick Start
1.  **Clone this repository** (or navigate to the project directory).
2.  **Run with Docker Compose**:
    ```bash
    docker-compose up --build
    ```
    This will start the entire MAS environment including the Redis scratchpad and the FastAPI core bridge.

3.  **Check the Walkthrough**: For detailed setup steps (including Android deployment), see **[walkthrough.md](walkthrough.md)**.

---

## 💡 Hardware Synergy
Project Sahayak is purpose-built for the **AMD ecosystem**:
- **Mobile Edge:** On-device inference runs on the **Ryzen™ AI NPU** to preserve battery and privacy.
- **Backend Optimization:** Macro-demand prediction models utilize **AMD Instinct™ GPUs** via `torch.hip` for high-throughput city-wide analytics.

---

> "Empowering the workforce, one optimized ride at a time."
