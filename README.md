# Gesture Controlled Subway Surfers (Computer Vision)

A real-time **gesture-based virtual controller** for Subway Surfers built using **Computer Vision**.  
This project allows controlling the game using **hand movements and gestures**, without any machine learning models.

---
## 📸 Demo

![Gesture Controlled Subway Surfers Demo](Demo.gif.gif)

## 🚀 Features

- 🖐 Open palm → **Jump**
- 🤙 Thumb + Pinky → **Slide**
- 👈 Hand on left side → **Move Left**
- 👉 Hand on right side → **Move Right**
- 📊 Live FPS & action display
- 🧠 Stable, rule-based gesture logic (No ML)

---

## 🛠 Tech Stack

- Python
- OpenCV
- MediaPipe
- Pynput

---

## ⚙️ How It Works

- MediaPipe detects hand landmarks in real-time
- Hand position determines left / right lane movement
- Specific finger combinations trigger jump & slide
- Keyboard inputs are simulated using `pynput`

This approach focuses on **stability, low latency, and simplicity**, making it suitable for real-time gameplay.

---

## ▶️ How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/gesture-controlled-subway-surfers.git
