# 🍳 PantryRescue: Zero-Waste Smart Cooking Companion

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://pantryrescue-aivisionchatbot.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Google GenAI SDK](https://img.shields.io/badge/Google%20GenAI-SDK-orange.svg?logo=google&logoColor=white)](https://github.com/google-gemini/generative-ai-python)
[![Twilio API](https://img.shields.io/badge/Twilio-WhatsApp%20API-red.svg?logo=twilio&logoColor=white)](https://www.twilio.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> Turn forgotten fridge leftovers and pantry staples into delicious 15-minute meals while eliminating food waste — delivered straight to your WhatsApp.

---

## 🚀 Live Demo

Experience PantryRescue live directly in your browser:  
👉 **[Launch PantryRescue Web App](https://pantryrescue-aivisionchatbot.streamlit.app)**

---

## 📌 Problem & Solution

Food waste is one of the leading contributors to global greenhouse gas emissions and household expenses. Millions of tons of edible food are thrown out every week simply because people don’t know what to cook with random leftover vegetables, open dairy cartons, or odds and ends sitting in the back of the pantry.

**PantryRescue** solves this with an AI-first kitchen assistant:
- **Zero Waste Chef Philosophy:** Suggests recipes using *strictly* the ingredients visible in your photos, supplemented only by everyday staples (oil, salt, pepper, water).
- **Perishable Prioritization:** Identifies fragile produce and expiring dairy so you cook them before they spoil.
- **Mobile Convenience:** Packages the final recipe card and shopping list directly into WhatsApp messages for easy countertop cooking.

---

## ✨ Core Features

- 📸 **Multimodal Vision Ingredient Detection**: Snap and upload a picture of your open fridge, shelf, or countertop. Powered by the Google GenAI SDK (`google-genai`), PantryRescue recognizes ingredients and quantities automatically.
- ⏱️ **Fast 15-Minute Recipe Generation**: Get instant, step-by-step zero-waste recipes tailored to your detected ingredients with minimal prep and cleanup.
- 📱 **Automated WhatsApp Recipe Dispatch**: Connect seamlessly with the Twilio WhatsApp API. Tap **"📤 Send to WhatsApp"** to get a clean, emoji-rich recipe card and shopping list delivered straight to your phone.
- 🎨 **Modern Dark Mode Experience**: Sleek, responsive Streamlit interface featuring glassmorphic accents, custom typography, and real-time streaming feedback.
- 🔄 **Stateful Multi-turn Conversations**: Ask follow-ups, substitute ingredients, adjust serving sizes, or tweak spice levels on the fly.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
|---|---|---|
| **Frontend & UI** | [Streamlit](https://streamlit.io/) | High-performance reactive web application framework |
| **Multimodal AI Engine** | [Google GenAI SDK (`google-genai`)](https://aistudio.google.com/) | Multimodal vision & reasoning using Gemini models |
| **Messaging & Notifications** | [Twilio WhatsApp API](https://www.twilio.com/whatsapp) | Direct-to-phone recipe card delivery |
| **Language Runtime** | Python 3.10+ | Robust, modern Python ecosystem |

---

## 📂 Project Structure

```
pantryrescue/
├── app.py                      # Main Streamlit application and UI logic
├── prompts.py                  # System prompts, persona definitions & message templates
├── requirements.txt            # Python dependencies (streamlit, google-genai, twilio)
├── .gitignore                  # Git ignore rules for secrets and runtime caches
└── .streamlit/
    ├── secrets.toml            # Private local credentials (git-ignored)
    └── secrets.toml.example    # Credential configuration template
```

---

## ⚙️ Getting Started & Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/jash-4/pantryrescue.git
cd pantryrescue
```

### 2. Create and Activate a Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
py -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Secrets

Copy the example configuration file:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Open `.streamlit/secrets.toml` and provide your credentials:

```toml
# Google Gemini API Key (from Google AI Studio: https://aistudio.google.com/)
GEMINI_API_KEY = "AIzaSy..."

# Twilio WhatsApp Credentials (from Twilio Console: https://console.twilio.com/)
TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
TWILIO_CONTENT_SID = "HXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

> **Note:** `.streamlit/secrets.toml` is included in `.gitignore` to prevent committing sensitive API keys.

### 5. Launch the Web Application

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 📱 How It Works

```mermaid
flowchart LR
    A[📸 Upload Fridge Photo] --> B[Gemini Vision Model]
    B --> C[Detect Ingredients & Perishables]
    C --> D[Generate 15-Min Zero-Waste Recipe]
    D --> E[Interactive Chat & Customization]
    E --> F[📤 Tap 'Send to WhatsApp']
    F --> G[Twilio WhatsApp API]
    G --> H[📲 Recipe Card on Your Phone]
```

1. **Onboarding:** Enter your name and WhatsApp number (with country code).
2. **Inspect Pantry:** Upload a photo of ingredients or ask cooking questions in natural language.
3. **Get Recipes:** Receive quick, delicious recipes tailored specifically to what needs to be cooked first.
4. **Send to WhatsApp:** Receive the summarized recipe card on your smartphone to cook hands-free.

---

## 🤝 Contributing

Contributions, feature suggestions, and pull requests are welcome!  
Feel free to open an issue or submit a pull request on GitHub.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
