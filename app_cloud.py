#!/usr/bin/env python3
"""
OmniAgent - Cloud-Optimized Multi-Modal AI Assistant
Optimized for Streamlit Community Cloud deployment

This version works entirely with cloud APIs and doesn't require local Ollama installation.
"""

import streamlit as st
import litellm
import os
import base64
import re
import time
from PIL import Image
from typing import Optional, Dict, Any, NamedTuple
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="OmniAgent - AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class EnvStatus(NamedTuple):
    openai_available: bool
    openrouter_available: bool
    anthropic_available: bool

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "privacy_mode" not in st.session_state:
        st.session_state.privacy_mode = "Normal"
    
    if "show_welcome" not in st.session_state:
        st.session_state.show_welcome = True
    
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    
    if "metrics" not in st.session_state:
        st.session_state.metrics = {
            "gpt4o": 0,
            "claude": 0,
            "gemini": 0,
            "fallbacks": 0
        }

def apply_theme_styling():
    """Apply custom CSS styling with theme support"""
    theme = st.session_state.get("theme", "light")
    
    # Define color schemes
    if theme == "dark":
        colors = {
            "bg": "#0e1117",
            "bg_secondary": "#1e2130", 
            "text": "#ffffff",
            "text_secondary": "#a0a0a0",
            "accent": "#00d4ff",
            "glass": "rgba(255, 255, 255, 0.05)",
            "border": "rgba(255, 255, 255, 0.1)"
        }
    else:
        colors = {
            "bg": "#ffffff",
            "bg_secondary": "#f8f9fa",
            "text": "#333333", 
            "text_secondary": "#666666",
            "accent": "#0066cc",
            "glass": "rgba(255, 255, 255, 0.8)",
            "border": "rgba(0, 0, 0, 0.1)"
        }
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {{
        background: linear-gradient(135deg, {colors['bg']} 0%, {colors['bg_secondary']} 100%);
        font-family: 'Inter', sans-serif;
    }}
    
    .main-header {{
        text-align: center;
        padding: 2rem 0;
        background: {colors['glass']};
        backdrop-filter: blur(20px);
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid {colors['border']};
    }}
    
    .chat-message {{
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid {colors['border']};
    }}
    
    .user-message {{
        background: linear-gradient(135deg, {colors['accent']}20, {colors['accent']}10);
        margin-left: 2rem;
    }}
    
    .assistant-message {{
        background: {colors['glass']};
        margin-right: 2rem;
    }}
    
    .model-badge {{
        display: inline-block;
        padding: 0.2rem 0.5rem;
        background: {colors['accent']};
        color: white;
        border-radius: 10px;
        font-size: 0.8rem;
        margin-left: 0.5rem;
    }}
    </style>
    """, unsafe_allow_html=True)

def get_env_status() -> EnvStatus:
    """Check environment status for cloud deployment"""
    openai_key = os.getenv("OPENAI_API_KEY", "")
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    
    return EnvStatus(
        openai_available=bool(openai_key and openai_key != "REPLACE_ME"),
        openrouter_available=bool(openrouter_key and openrouter_key != "REPLACE_ME"),
        anthropic_available=bool(anthropic_key and anthropic_key != "REPLACE_ME")
    )

def sanitize_user_text(text: str) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    
    # Trim and limit length
    text = text.strip()[:4000]
    
    # Basic prompt injection protection
    injection_patterns = [
        r'(?i)^system:',
        r'(?i)ignore\s+previous',
        r'(?i)you\s+are\s+now',
        r'(?i)forget\s+everything',
        r'(?i)new\s+instructions'
    ]
    
    for pattern in injection_patterns:
        text = re.sub(pattern, '', text)
    
    return text

def is_creative_or_complex(text: str) -> bool:
    """Determine if text requires advanced model"""
    if len(text) > 150:
        return True
    
    if '\n\n' in text:
        return True
    
    creative_keywords = [
        'poem', 'story', 'design', 'architecture', 'brainstorm',
        'write code', 'generate code', 'strategy', 'research plan',
        'product spec', 'analysis', 'detailed', 'comprehensive'
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in creative_keywords)

def route_model(has_image: bool, text: str, privacy: str, env: EnvStatus) -> str:
    """Route to appropriate model for cloud deployment"""
    # For images, use GPT-4V or Claude 3 Vision
    if has_image:
        if env.openai_available:
            return "openai/gpt-4o"
        elif env.anthropic_available:
            return "anthropic/claude-3-sonnet-20240229"
        else:
            return "google/gemini-pro-vision"
    
    # For privacy mode, try to use smaller models
    if privacy == "High":
        if env.openai_available:
            return "openai/gpt-3.5-turbo"
        elif env.anthropic_available:
            return "anthropic/claude-3-haiku-20240307"
        else:
            return "google/gemini-pro"
    
    # For complex tasks, use advanced models
    if is_creative_or_complex(text):
        if env.openai_available:
            return "openai/gpt-4o"
        elif env.openrouter_available:
            return "openrouter/anthropic/claude-3.5-sonnet"
        elif env.anthropic_available:
            return "anthropic/claude-3-sonnet-20240229"
        else:
            return "google/gemini-pro"
    
    # Default to efficient models
    if env.openai_available:
        return "openai/gpt-3.5-turbo"
    elif env.anthropic_available:
        return "anthropic/claude-3-haiku-20240307"
    else:
        return "google/gemini-pro"

def b64_image(uploaded_file) -> str:
    """Convert uploaded file to base64"""
    try:
        image = Image.open(uploaded_file)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return ""

def call_model(prompt: str, model: str, image_b64: Optional[str] = None) -> str:
    """Call the specified model"""
    try:
        timeout = int(os.getenv("LITELLM_TIMEOUT", "60"))
        
        messages = [{"role": "user", "content": prompt}]
        
        # Handle image inputs
        if image_b64 and model in ["openai/gpt-4o", "anthropic/claude-3-sonnet-20240229"]:
            if "openai" in model:
                messages[0]["content"] = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                ]
            elif "anthropic" in model:
                messages[0]["content"] = [
                    {"type": "text", "text": prompt},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_b64}}
                ]
        
        # Set API keys based on model
        kwargs = {"timeout": timeout}
        if "openrouter" in model:
            kwargs["api_key"] = os.getenv("OPENROUTER_API_KEY")
        
        response = litellm.completion(
            model=model,
            messages=messages,
            **kwargs
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        raise Exception(f"Error calling {model}: {str(e)}")

def process_input(user_input: str, uploaded_image) -> None:
    """Process user input and generate response"""
    # Sanitize input
    user_input = sanitize_user_text(user_input)
    if not user_input:
        st.error("Please enter a valid message.")
        return
    
    # Handle image
    image_b64 = None
    if uploaded_image:
        image_b64 = b64_image(uploaded_image)
        if not image_b64:
            return
    
    # Get environment status
    env = get_env_status()
    
    # Route model
    selected_model = route_model(
        has_image=bool(image_b64),
        text=user_input,
        privacy=st.session_state.privacy_mode,
        env=env
    )
    
    # Prepare prompt
    if image_b64:
        prompt = f"Use the image to answer: {user_input}"
    else:
        prompt = user_input
    
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "image": uploaded_image.name if uploaded_image else None
    })
    
    # Generate response
    try:
        with st.spinner(f"🤖 Thinking with {selected_model.split('/')[-1]}..."):
            response = call_model(prompt, selected_model, image_b64)
            
            # Update metrics
            model_name = selected_model.split('/')[-1]
            if "gpt" in model_name:
                st.session_state.metrics["gpt4o"] += 1
            elif "claude" in model_name:
                st.session_state.metrics["claude"] += 1
            elif "gemini" in model_name:
                st.session_state.metrics["gemini"] += 1
            
            # Add assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "model": selected_model
            })
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.session_state.metrics["fallbacks"] += 1
        
        # Add error message
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Sorry, I encountered an error: {str(e)}",
            "model": "error"
        })

def main():
    """Main application"""
    initialize_session_state()
    apply_theme_styling()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 OmniAgent</h1>
        <p>Cloud-Powered Multi-Modal AI Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        # Theme toggle
        theme = st.selectbox(
            "🎨 Theme",
            ["light", "dark"],
            index=0 if st.session_state.theme == "light" else 1
        )
        if theme != st.session_state.theme:
            st.session_state.theme = theme
            st.rerun()
        
        # Privacy mode
        st.session_state.privacy_mode = st.selectbox(
            "🔒 Privacy Mode",
            ["Normal", "High"],
            index=0 if st.session_state.privacy_mode == "Normal" else 1,
            help="High: Use smaller, faster models"
        )
        
        # Environment status
        st.markdown("### 🌐 Cloud Status")
        env = get_env_status()
        
        st.write("✅ OpenAI" if env.openai_available else "❌ OpenAI")
        st.write("✅ Anthropic" if env.anthropic_available else "❌ Anthropic") 
        st.write("✅ OpenRouter" if env.openrouter_available else "❌ OpenRouter")
        
        # Metrics
        st.markdown("### 📊 Usage")
        total_queries = sum(st.session_state.metrics.values())
        st.metric("Total Queries", total_queries)
        
        for model, count in st.session_state.metrics.items():
            if count > 0:
                st.write(f"{model.title()}: {count}")
        
        # Clear chat
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.session_state.metrics = {"gpt4o": 0, "claude": 0, "gemini": 0, "fallbacks": 0}
            st.session_state.show_welcome = True
            st.rerun()
    
    # Main chat interface
    if st.session_state.show_welcome:
        st.info("👋 Welcome! Upload an image or ask me anything to get started.")
        st.session_state.show_welcome = False
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message["role"] == "assistant" and "model" in message:
                model_name = message["model"].split("/")[-1]
                st.caption(f"🤖 {model_name}")
    
    # Input area
    col1, col2 = st.columns([3, 1])
    
    with col2:
        uploaded_image = st.file_uploader(
            "📷 Upload Image",
            type=["png", "jpg", "jpeg"],
            label_visibility="collapsed"
        )
    
    # Chat input
    if prompt := st.chat_input("Type your message..."):
        process_input(prompt, uploaded_image)
        st.rerun()

if __name__ == "__main__":
    main()
