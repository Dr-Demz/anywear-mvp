import streamlit as st
import pandas as pd
import requests
import time
import base64
import io
from PIL import Image

# --- CONFIGURATION & STATE ---
st.set_page_config(page_title="Anywear™ Africa", layout="wide", initial_sidebar_state="collapsed")

if 'view' not in st.session_state:
    st.session_state.view = 'Home'
if 'protagonist_data' not in st.session_state:
    st.session_state.protagonist_data = {}

def switch_view(new_view):
    st.session_state.view = new_view

# --- CORE UTILITIES ---
def compress_image(uploaded_file):
    """Compresses large iPhone/Android images to prevent n8n timeouts."""
    img = Image.open(uploaded_file)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize keeping aspect ratio, max 1024x1024
    img.thumbnail((1024, 1024))
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()

def trigger_n8n_workflow(image_bytes, brand, q1, q2, q3):
    """Fires the compressed data to the n8n backend."""
    # INSERT YOUR N8N WEBHOOK URL HERE
    N8N_WEBHOOK_URL = "https://your-n8n-instance.com/webhook/anywear-intake" 
    
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    
    payload = {
        "brand_context": brand,
        "protagonist_image": encoded_image,
        "psychographics": {
            "drive": q1,
            "weekends": q2,
            "destination": q3
        }
    }
    
    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=45)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Network error linking to Anywear servers. Check your connection.")
        return False

# --- VIEWS ---
def home_view():
    st.title("Anywear™ Africa")
    st.subheader("Scaling Word-of-mouth organically via Resonance Marketing.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("I am a Brand", on_click=switch_view, args=('Brand_Auth',), use_container_width=True)
    with col2:
        st.button("I am a Protagonist", on_click=switch_view, args=('Protagonist_Intake',), use_container_width=True)

# --- BRAND PORTAL ---
def brand_auth_view():
    st.title("Brand Portal")
    st.text_input("Email Address")
    st.text_input("Password", type="password")
    if st.button("Authenticate"):
        switch_view('Brand_Dashboard')
    if st.button("Back"):
        switch_view('Home')

def brand_dashboard_view():
    st.title("Main Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Campaigns Deployed", "3")
    col2.metric("Active Campaigns", "1")
    col3.metric("Gen Credits Purchased", "475")
    col4.metric("Gen Credits Left", "125")
    
    st.markdown("---")
    colA, colB, colC = st.columns(3)
    with colA:
        if st.button("View Campaigns", use_container_width=True): switch_view('Brand_Gallery')
    with colB:
        if st.button("Create Adventure", use_container_width=True): switch_view('Brand_Create_Adventure')
    with colC:
        if st.button("Top-Up Credits", use_container_width=True): switch_view('Brand_TopUp')

def brand_create_adventure_view():
    st.title("Adventure Builder")
    adv_title = st.text_input("Adventure Title (Required)")
    adv_desc = st.text_area("Brand Essence & Creative Direction")
    
    if adv_title and adv_desc:
        if st.button("Activate Adventure (Pay NGN 50,000)"):
            st.success("Redirecting to Paystack for NGN 50,000 setup fee...")
    else:
        st.button("Activate Adventure", disabled=True)
    if st.button("Back to Dashboard"): switch_view('Brand_Dashboard')

def brand_gallery_view():
    st.title("Adventure Gallery")
    st.markdown("### 1. Urban Odyssey")
    col1, col2, col3 = st.columns(3)
    col1.metric("Generations Left", "45")
    col2.metric("Used %", "64%")
    col3.metric("Expiry Date", "30 Days")
    if st.button("Back to Dashboard"): switch_view('Brand_Dashboard')

def brand_topup_view():
    st.title("Top-Up Generation Credits")
    tiers = {
        "Micro-Burst (50 gens)": "NGN 100,000",
        "Standard Flow (125 gens)": "NGN 175,000",
        "Growth Surge (300 gens)": "NGN 350,000",
        "Market Dominance (750 gens)": "NGN 750,000"
    }
    st.write(tiers)
    selected_tier = st.selectbox("Select Tier", list(tiers.keys()))
    if st.button("Proceed to Paystack API"):
        st.success(f"Redirecting to payment for {selected_tier}...")
    if st.button("Back to Dashboard"): switch_view('Brand_Dashboard')


# --- PROTAGONIST PORTAL ---
def protagonist_intake_view():
    # Dynamic Brand Injection via URL (e.g., ?brand=Quacktails)
    brand_name = st.query_params.get("brand", "Anywear").capitalize()
    
    st.title(f"The {brand_name} Adventure")
    st.caption("powered by Anywear Africa")
    
    st.markdown("### 1. Visual Likeness")
    capture_method = st.radio("Select Input Method", ("Camera", "Upload File"), horizontal=True)
    
    user_image = None
    if capture_method == "Camera":
        user_image = st.camera_input("Capture your face clearly")
    else:
        user_image = st.file_uploader("Upload a clear selfie", type=["jpg", "jpeg", "png", "heic"])

    st.markdown("### 2. Psychographic Profile")
    # Guided inputs instead of open text to guarantee data structure
    q1 = st.selectbox("What drives you everyday?", ["Creating Art", "Financial Freedom", "Building Community", "Exploring the World", "Mastering a Craft"])
    q2 = st.selectbox("How do you spend your free weekends?", ["Resting & Recharging", "Socializing & Events", "Learning & Reading", "Outdoor Adventures"])
    q3 = st.selectbox("Describe your ideal adventure destination.", ["Urban Metropolises", "Serene Beaches", "Futuristic Cities", "Quiet Mountains"])
    
    if user_image and q1 and q2 and q3:
        if st.button("Teleport Me into the Adventure", type="primary"):
            with st.spinner("Compressing image & compiling data..."):
                compressed_image = compress_image(user_image)
                
                # Fire the Webhook
                success = trigger_n8n_workflow(compressed_image, brand_name, q1, q2, q3)
                
                if success:
                    switch_view('Protagonist_Loading')
    else:
        st.button("Teleport Me into the Adventure", disabled=True)
        st.caption("Provide an image and answer all questions to proceed.")

def protagonist_loading_view():
    st.title("Synthesizing your Reality...")
    st.write("Our neural engines are mapping your physical and psychographic likeness.")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Simulated polling sequence (In production, this polls an Airtable DB for completion)
    stages = ["Analyzing facial topography...", "Matching brand essence...", "Rendering lighting & environment...", "Finalizing high-fidelity output..."]
    for i in range(100):
        time.sleep(0.08)
        progress_bar.progress(i + 1)
        if i % 25 == 0:
            status_text.text(stages[i // 25])
            
    st.success("Adventure Ready!")
    time.sleep(1)
    switch_view('Protagonist_Delivery')

def protagonist_delivery_view():
    st.title("Your Branded Adventure")
    
    # Placeholder for the returned n8n image URL
    st.image("https://via.placeholder.com/600x800.png?text=Your+High-Fidelity+Adventure", caption="Your Anywear Postcard")
    
    st.text_area("Copy your story:", "I just unlocked my custom adventure. The hustle is real, but so is the reward. #AnywearAfrica")
    
    st.markdown("### Claim Your Likeness")
    col1, col2 = st.columns(2)
    with col1:
        st.button("Post to Instagram Stories", use_container_width=True)
    with col2:
        st.button("Share to Snapchat", use_container_width=True)
        
    st.markdown("---")
    if st.button("Start Over"): switch_view('Home')

# --- APP ROUTING LOOP ---
if st.session_state.view == 'Home': home_view()
elif st.session_state.view == 'Brand_Auth': brand_auth_view()
elif st.session_state.view == 'Brand_Dashboard': brand_dashboard_view()
elif st.session_state.view == 'Brand_Create_Adventure': brand_create_adventure_view()
elif st.session_state.view == 'Brand_Gallery': brand_gallery_view()
elif st.session_state.view == 'Brand_TopUp': brand_topup_view()
elif st.session_state.view == 'Protagonist_Intake': protagonist_intake_view()
elif st.session_state.view == 'Protagonist_Loading': protagonist_loading_view()
elif st.session_state.view == 'Protagonist_Delivery': protagonist_delivery_view()