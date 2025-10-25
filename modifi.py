# clinic_chatbot_modern_ui.py
import streamlit as st
import re
from typing import Tuple, Dict, Any

# ---------------------------
# Knowledge Base
# ---------------------------
KB = {
    "clinic": {
        "name": "Serenity Health Clinic",
        "location": "Pune, India",
        "contact_phone": "+91-9876543210",
        "contact_email": "info@serenityclinic.in",
        "overview": "Serenity Health Clinic in Pune offers outpatient services across general medicine, cardiology, and pediatrics with diagnostic facilities and online booking."
    },
    "opd_timings": {
        "general physician": "9:00 AM–1:00 PM, 5:00 PM–9:00 PM",
        "pediatrician": "10:00 AM–2:00 PM",
        "cardiologist": "6:00 PM–8:00 PM"
    },
    "facilities": ["ECG", "Diagnostic Lab", "Vaccination", "Physiotherapy", "Online Booking"],
    "doctors": {
        "dr. meera patil": {"name": "Dr. Meera Patil", "specialty": "General Physician", "experience": "10 years"},
        "dr. arjun rao": {"name": "Dr. Arjun Rao", "specialty": "Cardiologist", "experience": "12 years"},
        "dr. sneha kulkarni": {"name": "Dr. Sneha Kulkarni", "specialty": "Pediatrician", "experience": "8 years"}
    }
}

# ---------------------------
# Helper functions
# ---------------------------
def normalize(text): return text.strip().lower()

def extract_doctor(text):
    text = normalize(text)
    for key, v in KB["doctors"].items():
        if key in text or v["name"].split()[-1].lower() in text:
            return v["name"]
    return ""

def extract_specialty(text):
    text = normalize(text)
    for s in KB["opd_timings"].keys():
        if s in text: return s
    if "cardio" in text: return "cardiologist"
    if "pedi" in text or "child" in text: return "pediatrician"
    if "general" in text or "physician" in text: return "general physician"
    return ""

def extract_facility(text):
    text = normalize(text)
    for f in KB["facilities"]:
        if f.lower() in text: return f
    return ""

# ---------------------------
# Intent classification
# ---------------------------
def classify_intent(text):
    t = normalize(text)
    if re.search(r"\b(hi|hello|hey|good morning|good evening)\b", t): return "greeting", {}
    if re.search(r"\b(contact|phone|call|email|reach)\b", t): return "contact", {}
    if re.search(r"\b(book|appointment|schedule|reserve)\b", t):
        return "book", {"doctor": extract_doctor(t), "specialty": extract_specialty(t)}
    if re.search(r"\b(time|timings|available|availability|visit)\b", t):
        return "ask_timings", {"doctor": extract_doctor(t), "specialty": extract_specialty(t)}
    if re.search(r"\b(dr\.?|doctor|physician|cardiologist|pediatrician)\b", t):
        return "ask_doctor_info", {"doctor": extract_doctor(t), "specialty": extract_specialty(t)}
    if re.search(r"\b(facility|facilities|ecg|lab|vaccination|physiotherapy|diagnostic)\b", t):
        return "ask_facilities", {"facility": extract_facility(t)}
    return "unknown", {}

# ---------------------------
# Response logic
# ---------------------------
def generate_response(intent, entities, context):
    if intent == "greeting":
        return "👋 Hello! I’m the Serenity Clinic assistant. How may I help you today?"

    if intent == "contact":
        c = KB["clinic"]
        return f"📞 {c['name']} — Phone: {c['contact_phone']}, Email: {c['contact_email']}"

    if intent == "ask_facilities":
        f = entities.get("facility")
        if f:
            return f"✅ Yes, we provide {f}. Other facilities: {', '.join(KB['facilities'])}."
        return f"Our facilities include: {', '.join(KB['facilities'])}. Which one would you like more details about?"

    if intent == "ask_doctor_info":
        d = entities.get("doctor")
        s = entities.get("specialty")
        if d:
            for v in KB["doctors"].values():
                if v["name"].lower() == d.lower():
                    return f"👨‍⚕️ {v['name']} — {v['specialty']}, {v['experience']} experience. OPD: {KB['opd_timings'][v['specialty'].lower()]}"
        if s:
            docs = [v for v in KB["doctors"].values() if v["specialty"].lower() == s]
            if docs:
                return "\n".join([f"{d['name']} — {d['experience']}" for d in docs])
        return "Our doctors: " + ", ".join([v["name"] for v in KB["doctors"].values()])

    if intent == "ask_timings":
        d = entities.get("doctor")
        s = entities.get("specialty")
        if d:
            for v in KB["doctors"].values():
                if v["name"].lower() == d.lower():
                    spec = v["specialty"].lower()
                    return f"🕒 {d} ({spec.title()}) is available: {KB['opd_timings'][spec]}."
        if s:
            return f"🕒 The OPD timings for {s.title()} are: {KB['opd_timings'][s]}"
        return "Which doctor or department do you want timings for?"

    if intent == "book":
        d = entities.get("doctor")
        s = entities.get("specialty")
        if d: return f"✅ Booking request noted for {d}. Please provide your preferred date & time."
        if s: return f"Which doctor from {s.title()} department would you like to book?"
        return "Sure — which department or doctor would you like to book with?"

    return "Sorry, I didn’t get that. You can ask about doctors, timings, facilities, or booking an appointment."

# ---------------------------
# Streamlit Chat Interface
# ---------------------------
st.set_page_config(page_title="Serenity Clinic Chatbot", page_icon="🏥", layout="centered")

# --- Custom CSS for modern look ---
st.markdown("""
    <style>
        body {
            background-color: #f7f9fc;
        }
        .chat-container {
            background-color: white;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            max-width: 700px;
            margin: auto;
        }
        .user-msg {
            background-color: #DCF8C6;
            color: black;
            padding: 10px 15px;
            border-radius: 20px;
            max-width: 80%;
            margin-left: auto;
            margin-bottom: 10px;
        }
        .bot-msg {
            background-color: #E8EAF6;
            color: black;
            padding: 10px 15px;
            border-radius: 20px;
            max-width: 80%;
            margin-right: auto;
            margin-bottom: 10px;
        }
        .banner {
            text-align: center;
            padding: 15px;
            background: linear-gradient(90deg, #0072ff 0%, #00c6ff 100%);
            color: white;
            border-radius: 12px;
            margin-bottom: 15px;
            font-size: 22px;
            font-weight: 600;
        }
        .footer {
            text-align: center;
            color: #555;
            font-size: 13px;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="banner">🏥 Serenity Health Clinic — Virtual Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg">{msg["text"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-msg">{msg["text"]}</div>', unsafe_allow_html=True)

# Chat input area
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "text": prompt})
    st.markdown(f'<div class="user-msg">{prompt}</div>', unsafe_allow_html=True)

    intent, entities = classify_intent(prompt)
    response = generate_response(intent, entities, {})
    st.session_state.messages.append({"role": "assistant", "text": response})
    st.markdown(f'<div class="bot-msg">{response}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="footer">© 2025 Serenity Health Clinic</div>', unsafe_allow_html=True)
