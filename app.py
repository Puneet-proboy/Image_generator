from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
import requests
from PIL import Image
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="AI Image Generator",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }

    .stApp {
        background: linear-gradient(-45deg, #0ea5e9, #3b82f6, #6366f1, #8b5cf6);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        color: #f8fafc;
    }

    .main {
        padding: 3rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border-radius: 15px;
        padding: 0.75rem 2.5rem;
        font-size: 1.2rem;
        font-weight: bold;
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 10px 25px rgba(37, 99, 235, 0.2);
        position: relative;
        overflow: hidden;
    }

    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 15px 30px rgba(37, 99, 235, 0.3);
    }

    .stButton>button::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        animation: shimmer 3s infinite;
    }

    .stTextArea>div>div {
        background-color: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 2px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        color: white;
    }

    .stTextArea>div>div:focus-within {
        border-color: #60a5fa;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.3);
        transform: translateY(-2px);
    }

    h1 {
        text-align: center;
        background: linear-gradient(to right, #f0f9ff, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4rem !important;
        font-weight: 800 !important;
        margin-bottom: 1rem !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        animation: float 6s ease-in-out infinite;
    }

    .subtitle {
        text-align: center;
        color: #e0f2fe;
        font-size: 1.4rem;
        margin-bottom: 3rem;
        font-weight: 500;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .output-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 2.5rem;
        border-radius: 20px;
        margin-top: 2rem;
        border: 2px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
        animation: fadeIn 1s ease-out;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .output-container:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }

    .sidebar .stSelectbox {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 0.5rem;
        margin-bottom: 1rem;
    }

    /* Glass morphism effect for sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Loading animation */
    .stSpinner {
        animation: pulse 2s infinite;
    }

    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.4);
    }

    /* Add smooth scrolling */
    * {
        scroll-behavior: smooth;
    }
    </style>
""", unsafe_allow_html=True)

load_dotenv()
openai_client = OpenAI()

def image_model(prompt, size, quality, style, n=1):
    # Add style to the prompt if not Natural
    if style != "Natural":
        prompt = f"{prompt}, in the style of {style}"
    
    response = openai_client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality=quality,
        n=n,
    )
    
    # Return list of URLs if multiple images, otherwise return single URL
    if n > 1:
        return [image.url for image in response.data]
    return response.data[0].url

def display_image_from_url(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img

# Add parameters and clear chat button on the left side
with st.sidebar:
    st.markdown("### 🎨 Creation Settings")
    
    # Image size selection with visual representation
    st.markdown("#### 📐 Canvas Size")
    size_options = {
        "1024x1024": "Square (1024x1024)",
        "1024x1792": "Portrait (1024x1792)",
        "1792x1024": "Landscape (1792x1024)"
    }
    selected_size = st.selectbox(
        "Choose your canvas dimensions",
        options=list(size_options.keys()),
        format_func=lambda x: size_options[x],
        help="Select the perfect dimensions for your masterpiece"
    )
    
    # Quality selection
    st.markdown("#### 💫 Quality")
    quality = st.select_slider(
        "Image Quality",
        options=["standard", "hd"],
        value="standard",
        help="HD offers enhanced detail and clarity"
    )
    
    # Art style selection
    st.markdown("#### 🎭 Art Style")
    style = st.selectbox(
        "Choose your artistic style",
        ["Natural", "Watercolor", "Oil Painting", "Digital Art", "Pop Art", 
         "Minimalist", "Anime", "Comic Book", "Cyberpunk", "Steampunk"],
        help="Select a style to transform your image"
    )

# Create columns for better layout
col1, col2 = st.columns([2, 1])

with col1:
    # Prompt input with placeholder
    prompt = st.text_area(
        "🌟 Describe your vision",
        placeholder="Let your imagination run wild... \nE.g., 'A magical forest at twilight with glowing mushrooms and fairy lights'",
        height=100
    )

with col2:
    # Generate button
    generate_button = st.button("🎨 Generate Magic", use_container_width=True)
    
    # Add a fun random prompt generator
    if st.button("🎲 Inspire Me", use_container_width=True):
        import random
        creative_prompts = [
            "A cozy treehouse cafe floating among rainbow clouds",
            "A steampunk city where plants have taken over the machinery",
            "An underwater library visited by mermaids and sea creatures",
            "A crystal palace where time stands still",
            "A garden where musical flowers bloom under starlight"
        ]
        st.session_state.random_prompt = random.choice(creative_prompts)
        prompt = st.session_state.random_prompt
        st.text_area("Generated Prompt", value=prompt, height=100)

if generate_button and prompt:
    with st.spinner("🎨 Creating your masterpiece..."):
        try:
            image_url = image_model(prompt, selected_size, quality, style)
            
            # Display the result in a styled container
            st.markdown("<div class='output-container'>", unsafe_allow_html=True)
            st.image(
                display_image_from_url(image_url),
                caption="✨ Your creation has materialized!",
                use_column_width=True
            )
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Add download button
            st.download_button(
                label="📥 Download Creation",
                data=requests.get(image_url).content,
                file_name="ai_masterpiece.png",
                mime="image/png"
            )
            
        except Exception as e:
            st.error(f"🎨 Oops! A creative hiccup occurred: {str(e)}")