import streamlit as st
import replicate
import os
from PIL import Image

st.set_page_config(page_title="ANYWEAR", page_icon="⚡", layout="centered")

# STYLE
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #E0E0E0; font-family: 'Courier New', monospace; }
    .stButton>button { background-color: #00FF99; color: black; border: none; width: 100%; padding: 15px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# SIDEBAR FOR KEY
with st.sidebar:
    st.header("⚡ ACCESS")
    # Tries to get key from Secrets first, otherwise asks user
    if 'REPLICATE_API_TOKEN' in st.secrets:
        os.environ["REPLICATE_API_TOKEN"] = st.secrets['REPLICATE_API_TOKEN']
        st.success("System Key Loaded")
    else:
        api_token = st.text_input("Replicate API Token", type="password")
        if api_token:
            os.environ["REPLICATE_API_TOKEN"] = api_token

# APP LOGIC
st.title("⚡ ANYWEAR")
st.caption("DISTRIBUTED TRUST NETWORK v1.0")

uploaded_file = st.file_uploader("1. UPLOAD MOLECULE (Selfie)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Subject Identified", width=200)
    
    world = st.selectbox("2. SELECT TARGET", [
        "Coca-Cola Cyber-Lagos", 
        "Gucci Afro-Luxe", 
        "Red Bull E-Sports"
    ])

    if st.button("TELEPORT ME ⚡"):
        if not os.environ.get("REPLICATE_API_TOKEN"):
            st.error("⚠️ STOP: Enter Replicate API Token in Sidebar.")
        else:
            with st.spinner("Teleporting..."):
                try:
                    # PROMPTS
                    if world == "Coca-Cola Cyber-Lagos":
                        prompt = "Cinematic shot of a person holding a glowing red Coca-Cola bottle. Background is a cyberpunk Lagos night market, neon rain. High contrast, 8k."
                    elif world == "Gucci Afro-Luxe":
                        prompt = "Vogue editorial shot of a model wearing luxury Gucci african print silk robes and gold jewelry. Background is a futuristic neo-african palace, warm lighting."
                    else:
                        prompt = "Intense action portrait of an e-sports athlete wearing a Red Bull gaming headset. Background is a futuristic stadium with blue lasers. Sweat on skin."

                    # REPLICATE CALL
                    output = replicate.run(
                        "black-forest-labs/flux-1.1-pro-ultra",
                        input={
                            "prompt": prompt + " The subject has the facial structure of the input image.",
                            "image_prompt": uploaded_file,
                            "image_prompt_strength": 0.45,
                            "aspect_ratio": "3:4",
                            "safety_tolerance": 5
                        }
                    )
                    st.image(str(output), use_column_width=True)
                    st.success("✅ REWARD UNLOCKED: NGN 500")
                except Exception as e:
                    st.error(f"Error: {e}")