import json
import re
import streamlit as st
from google import genai
from google.genai import types
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioRestException
from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE, SUMMARY_REQUEST_PROMPT

# Configure page metadata and layout
st.set_page_config(
    page_title="PantryRescue",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for polished, modern aesthetics
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .main-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 1.5rem;
    }
    .header-title-container {
        display: flex;
        flex-direction: column;
    }
    .app-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(135deg, #FF9900 0%, #FF5E36 50%, #4EBA6F 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .app-subtitle {
        font-size: 0.95rem;
        color: #8C9BAE;
        margin-top: 0.2rem;
    }
    .user-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(78, 186, 111, 0.12);
        color: #4EBA6F;
        padding: 0.35rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        border: 1px solid rgba(78, 186, 111, 0.25);
    }
    .onboarding-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .whatsapp-btn button {
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(37, 211, 102, 0.3);
    }
    .whatsapp-btn button:hover:not(:disabled) {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(37, 211, 102, 0.45);
    }
    .feature-tag {
        display: inline-block;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 6px;
        padding: 0.2rem 0.5rem;
        margin: 0.2rem;
        font-size: 0.78rem;
        color: #A0AEC0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Cached API clients to avoid reconnecting on Streamlit reruns
@st.cache_resource
def get_gemini_client(api_key: str) -> genai.Client:
    """Instantiate and cache the Google GenAI SDK client."""
    return genai.Client(api_key=api_key)

@st.cache_resource
def get_twilio_client(account_sid: str, auth_token: str) -> TwilioClient:
    """Instantiate and cache the Twilio REST client."""
    return TwilioClient(account_sid, auth_token)

def check_secrets_configured() -> tuple[bool, list[str]]:
    """Verify that all required secrets are present in st.secrets."""
    required_keys = [
        "GEMINI_API_KEY",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_WHATSAPP_FROM",
        "TWILIO_CONTENT_SID",
    ]
    missing = [key for key in required_keys if key not in st.secrets or not str(st.secrets[key]).strip()]
    return len(missing) == 0, missing

def normalize_phone_number(number: str) -> str:
    """Normalize phone numbers to international E.164 format with country code."""
    raw = str(number).strip()
    digits = re.sub(r"[^\d]", "", raw)
    
    if raw.startswith("+"):
        return f"+{digits}"
    if len(digits) == 10:
        return f"+91{digits}"
    if len(digits) == 12 and digits.startswith("91"):
        return f"+{digits}"
    return f"+{digits}"

def format_whatsapp_recipient(number: str) -> str:
    """Format phone number to E.164 with whatsapp: prefix."""
    normalized = normalize_phone_number(number)
    if not normalized.startswith("whatsapp:"):
        return f"whatsapp:{normalized}"
    return normalized

def send_whatsapp_summary(user_name: str, phone_number: str):
    """Summarize conversation via Gemini chat and dispatch via Twilio WhatsApp API."""
    if "chat" not in st.session_state:
        st.error("No active chef session found.")
        return

    with st.spinner("🍳 Preparing zero-waste recipe card & sending to WhatsApp..."):
        try:
            # 1. Ask Gemini chat session for the WhatsApp summary
            summary_response = st.session_state.chat.send_message(SUMMARY_REQUEST_PROMPT)
            raw_summary = summary_response.text or ""
            clean_summary = raw_summary.strip()

            if not clean_summary:
                st.error("Received an empty recipe summary from the AI model.")
                return

            # Append the summary to the chat stream for user visibility
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"📱 **WhatsApp Recipe Card Generated:**\n\n{clean_summary}",
            })

            # 2. Get Twilio client and format destination address
            twilio_client = get_twilio_client(
                account_sid=st.secrets["TWILIO_ACCOUNT_SID"],
                auth_token=st.secrets["TWILIO_AUTH_TOKEN"],
            )
            to_address = format_whatsapp_recipient(phone_number)
            
            # Message body containing the actual recipe card
            wa_text = f"🍳 *Hi {user_name}, here is your PantryRescue Recipe:*\n\n{clean_summary}"
            summary_for_wa = clean_summary[:950] + "..." if len(clean_summary) > 950 else clean_summary
            content_payload = json.dumps({"1": user_name, "2": summary_for_wa})

            # 3. Dispatch actual recipe card to WhatsApp
            try:
                # Direct message dispatch delivers the full recipe text immediately
                message = twilio_client.messages.create(
                    from_=st.secrets["TWILIO_WHATSAPP_FROM"],
                    to=to_address,
                    body=wa_text,
                )
            except TwilioRestException:
                # Fallback to Content SID template if required by sandbox state
                message = twilio_client.messages.create(
                    from_=st.secrets["TWILIO_WHATSAPP_FROM"],
                    to=to_address,
                    content_sid=st.secrets["TWILIO_CONTENT_SID"],
                    content_variables=content_payload,
                )

            st.toast(f"✅ Recipe dispatched to {to_address}!", icon="📱")
            st.success(
                f"🎉 **WhatsApp message sent successfully!**\n\n"
                f"- **Recipient:** `{to_address}`\n"
                f"- **Message SID:** `{message.sid}`\n"
                f"- **Status:** `{message.status}`"
            )

        except TwilioRestException as exc:
            st.error(f"❌ Twilio WhatsApp Error ({exc.code}): {exc.msg}")
        except Exception as exc:
            st.error(f"❌ Failed to send WhatsApp summary: {str(exc)}")

# Validate environment secrets
secrets_ok, missing_secrets = check_secrets_configured()
if not secrets_ok:
    st.error("⚠️ **Configuration Required: Missing Secrets**")
    st.markdown(
        f"""
        Please provide the following secrets in `.streamlit/secrets.toml`:
        
        {chr(10).join(f"- `{k}`" for k in missing_secrets)}
        
        👉 You can copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and add your real keys.
        """
    )
    with st.expander("📄 Example `.streamlit/secrets.toml` Template"):
        st.code(
            """GEMINI_API_KEY = "AIzaSy..."
TWILIO_ACCOUNT_SID = "AC..."
TWILIO_AUTH_TOKEN = "..."
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
TWILIO_CONTENT_SID = "HX..."
""",
            language="toml",
        )
    st.stop()

# Initialize Gemini client
gemini_client = get_gemini_client(api_key=st.secrets["GEMINI_API_KEY"])

# Initialize session state flags
if "onboarded" not in st.session_state:
    st.session_state.onboarded = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "whatsapp_number" not in st.session_state:
    st.session_state.whatsapp_number = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# STEP 1: ONBOARDING SCREEN
# ==========================================
if not st.session_state.onboarded:
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    _, col_form, _ = st.columns([1, 2, 1])
    with col_form:
        st.markdown(
            """
            <div style='text-align: center; margin-bottom: 1.5rem;'>
                <h1 style='font-size: 2.6rem; margin-bottom: 0.3rem;'>🍳 PantryRescue</h1>
                <p style='color: #8C9BAE; font-size: 1.05rem;'>
                    Zero-Waste Smart Cooking Companion powered by Gemini & Twilio
                </p>
                <div>
                    <span class='feature-tag'>📸 Photo Ingredient Detection</span>
                    <span class='feature-tag'>⚡ 15-Minute Zero Waste Recipes</span>
                    <span class='feature-tag'>📲 Direct WhatsApp Delivery</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("onboarding_form", clear_on_submit=False):
            st.markdown("#### 👋 Let's set up your kitchen profile")
            st.caption("Tell us your name and where to text your final recipe card & grocery lists.")

            name_input = st.text_input(
                "Your Name",
                placeholder="e.g. Alex",
                help="What should Chef PantryRescue call you?",
            )
            phone_input = st.text_input(
                "WhatsApp Number (with country code)",
                placeholder="+911234567890",
                help="Enter your WhatsApp number. 10-digit numbers automatically default to India (+91).",
            )

            submitted = st.form_submit_button("Start Cooking 🚀", use_container_width=True)

            if submitted:
                cleaned_digits = re.sub(r"[^\d]", "", phone_input.strip())
                if not name_input.strip():
                    st.warning("Please enter your name.")
                elif len(cleaned_digits) < 10:
                    st.warning("Please enter a valid phone number (at least 10 digits).")
                else:
                    norm_phone = normalize_phone_number(phone_input)
                    st.session_state.user_name = name_input.strip()
                    st.session_state.whatsapp_number = norm_phone
                    st.session_state.onboarded = True

                    # Initialize Gemini Chat Session with stable 3.5-flash
                    st.session_state.chat = gemini_client.chats.create(
                        model="gemini-3.5-flash",
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT,
                        ),
                    )

                    # Populate initial welcome greeting
                    welcome_text = WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.user_name)
                    st.session_state.messages = [
                        {
                            "role": "assistant",
                            "content": welcome_text,
                        }
                    ]
                    st.rerun()
    st.stop()

# ==========================================
# STEP 2: MAIN SCREEN
# ==========================================
col_title, col_actions = st.columns([5, 2], vertical_alignment="bottom")

with col_title:
    st.markdown(
        f"""
        <div class="main-header">
            <div class="header-title-container">
                <h1 class="app-title">🍳 PantryRescue</h1>
                <span class="app-subtitle">Zero-waste 15-minute recipes from your fridge photos</span>
            </div>
            <div class="user-badge">
                👤 {st.session_state.user_name} &nbsp;|&nbsp; 📱 {st.session_state.whatsapp_number}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_actions:
    can_send_whatsapp = len(st.session_state.get("messages", [])) >= 2
    st.markdown('<div class="whatsapp-btn">', unsafe_allow_html=True)
    if st.button(
        "📤 Send to WhatsApp",
        disabled=not can_send_whatsapp,
        help="Receive the final 15-min recipe card and grocery list via WhatsApp" if can_send_whatsapp else "Chat with PantryRescue first to generate a recipe!",
        use_container_width=True,
    ):
        send_whatsapp_summary(
            user_name=st.session_state.user_name,
            phone_number=st.session_state.whatsapp_number,
        )
    st.markdown("</div>", unsafe_allow_html=True)

# Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("photo_bytes"):
            st.image(
                msg["photo_bytes"],
                caption="📸 Uploaded pantry / fridge photo",
                use_container_width=True,
            )
        if msg.get("content"):
            st.markdown(msg["content"])

# Chat Input with image upload capability
user_input = st.chat_input(
    "Ask a cooking question or snap a photo of your fridge/pantry",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)

if user_input:
    input_text = getattr(user_input, "text", "") or ""
    input_files = getattr(user_input, "files", []) or []
    photo_bytes = None
    photo_mime = None

    if input_files:
        photo = input_files[0]
        photo_bytes = photo.getvalue()
        photo_mime = photo.type or "image/jpeg"

    display_text = input_text if input_text.strip() else ("📸 Uploaded ingredient photo" if photo_bytes else "")
    st.session_state.messages.append({
        "role": "user",
        "content": display_text,
        "photo_bytes": photo_bytes,
    })

    with st.chat_message("user"):
        if photo_bytes:
            st.image(photo_bytes, caption="📸 Uploaded pantry / fridge photo", use_container_width=True)
        if display_text:
            st.markdown(display_text)

    # Prepare multimodal payload for Gemini
    contents_payload = []
    if photo_bytes:
        contents_payload.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo_mime))

    effective_prompt = input_text.strip() if input_text.strip() else "Please inspect the ingredients in this photo and suggest a quick 15-minute zero-waste recipe."
    contents_payload.append(effective_prompt)

    with st.chat_message("assistant"):
        with st.spinner("🧑‍🍳 Chef PantryRescue is inspecting ingredients..."):
            try:
                response = st.session_state.chat.send_message(contents_payload)
                assistant_text = response.text or "I've inspected your ingredients. What would you like to prepare?"
                st.markdown(assistant_text)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_text,
                })
            except Exception as e:
                err_msg = f"Sorry, I encountered an issue inspecting the ingredients: {str(e)}"
                st.error(err_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": err_msg,
                })
    st.rerun()