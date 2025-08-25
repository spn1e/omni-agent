#!/usr/bin/env python3
"""
OmniAgent - Local-First Multi-Modal AI Assistant with Privacy-Aware Dynamic Routing

Requirements (save as requirements.txt):
    streamlit>=1.33.0
    pillow>=10.3.0
    litellm>=1.41.10

Setup:
    1. Install Ollama from https://ollama.ai
    2. Run: ollama serve
    3. Pull models: ollama pull llama3:8b && ollama pull llava
    4. Optional: set OPENAI_API_KEY environment variable
    5. Run: streamlit run app.py
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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Ollama base URL
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Configure LiteLLM for Ollama
import litellm
litellm.set_verbose = os.getenv("LITELLM_LOG", "info") == "debug"

# Set Ollama base URL for LiteLLM
os.environ["OLLAMA_API_BASE"] = OLLAMA_BASE_URL

# Set OpenRouter API key if available
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key and openai_api_key.startswith("sk-or-"):
    os.environ["OPENROUTER_API_KEY"] = openai_api_key

# Page configuration
st.set_page_config(
    page_title="OmniAgent - Privacy-First AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Base CSS for both themes
st.markdown("""
<style>
    .hero-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    
    .hero-description {
        font-size: 1rem;
        opacity: 0.8;
        line-height: 1.6;
    }
    
    /* Status Indicators */
    .health-good { 
        color: #28a745; 
        font-weight: 600;
    }
    .health-bad { 
        color: #dc3545; 
        font-weight: 600;
    }
    
    /* Theme Toggle Button */
    .theme-toggle {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 999;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: none;
        border-radius: 50px;
        padding: 0.5rem 1rem;
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .theme-toggle:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# Data structures
class EnvStatus(NamedTuple):
    """Environment status for health checks"""
    openai_available: bool
    ollama_available: bool
    ollama_error: Optional[str] = None

class ModelCall(NamedTuple):
    """Result of a model call"""
    content: str
    model_used: str
    is_fallback: bool = False
    error: Optional[str] = None

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "privacy_mode" not in st.session_state:
        st.session_state.privacy_mode = os.getenv("PRIVACY_DEFAULT", "Normal")
    if "show_welcome" not in st.session_state:
        st.session_state.show_welcome = len(st.session_state.get("messages", [])) == 0
    if "theme" not in st.session_state:
        st.session_state.theme = "light"  # Default to light theme
    
    # Metrics for telemetry
    st.session_state.setdefault("metrics", {
        "llava": 0,
        "llama3": 0, 
        "gpt4o": 0,
        "openrouter": 0,
        "fallbacks": 0
    })

def apply_theme_styling():
    """Apply ultra-modern theme-specific CSS styling with glassmorphism and animations"""
    if st.session_state.theme == "dark":
        # Dark theme with glassmorphism and modern effects
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            /* Dark Theme Variables */
            :root {
                --bg-primary: #0f0f23;
                --bg-secondary: #1a1a2e;
                --bg-tertiary: #16213e;
                --bg-glass: rgba(26, 26, 46, 0.7);
                --text-primary: #ffffff;
                --text-secondary: #a0a9c0;
                --text-tertiary: #6b7280;
                --accent-primary: #8b5cf6;
                --accent-secondary: #a855f7;
                --accent-glow: rgba(139, 92, 246, 0.4);
                --success: #10b981;
                --warning: #f59e0b;
                --error: #ef4444;
                --border: rgba(255, 255, 255, 0.1);
                --glass-bg: rgba(255, 255, 255, 0.05);
                --glass-border: rgba(255, 255, 255, 0.1);
            }
            
            /* Global Styles */
            * {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            /* Animated Background */
            .stApp {
                background: 
                    radial-gradient(circle at 20% 80%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(168, 85, 247, 0.15) 0%, transparent 50%),
                    radial-gradient(circle at 40% 40%, rgba(99, 102, 241, 0.1) 0%, transparent 50%),
                    linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
                background-attachment: fixed;
                color: var(--text-primary);
                min-height: 100vh;
                animation: backgroundShift 20s ease-in-out infinite;
            }
            
            @keyframes backgroundShift {
                0%, 100% { background-position: 0% 0%, 100% 100%, 50% 50%; }
                50% { background-position: 100% 100%, 0% 0%, 25% 75%; }
            }
            
            /* Glassmorphism Sidebar */
            .css-1d391kg, .css-1544g2n, .stSidebar > div {
                background: var(--glass-bg) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                border-right: 1px solid var(--glass-border) !important;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
            }
            
            /* Ultra-Modern Hero Section */
            .hero-section {
                background: linear-gradient(135deg, 
                    rgba(139, 92, 246, 0.9) 0%, 
                    rgba(99, 102, 241, 0.8) 50%,
                    rgba(168, 85, 247, 0.9) 100%);
                backdrop-filter: blur(20px) saturate(180%);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
                padding: 3rem 2rem;
                border-radius: 24px;
                text-align: center;
                margin-bottom: 2rem;
                box-shadow: 
                    0 20px 60px rgba(139, 92, 246, 0.3),
                    0 8px 32px rgba(0, 0, 0, 0.2),
                    inset 0 1px 0 rgba(255, 255, 255, 0.2);
                position: relative;
                overflow: hidden;
                animation: heroFloat 6s ease-in-out infinite;
            }
            
            .hero-section::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, 
                    transparent, 
                    rgba(255, 255, 255, 0.1), 
                    transparent);
                animation: shimmer 3s infinite;
            }
            
            @keyframes heroFloat {
                0%, 100% { transform: translateY(0px) rotate(0deg); }
                50% { transform: translateY(-5px) rotate(0.5deg); }
            }
            
            @keyframes shimmer {
                0% { left: -100%; }
                100% { left: 100%; }
            }
            
            /* Glassmorphism Model Badges */
            .model-badge {
                background: linear-gradient(135deg, 
                    rgba(139, 92, 246, 0.8), 
                    rgba(168, 85, 247, 0.9));
                backdrop-filter: blur(10px) saturate(180%);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
                display: inline-block;
                margin: 0.2rem 0.2rem;
                box-shadow: 
                    0 4px 20px rgba(139, 92, 246, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.2);
                transform: translateY(0);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .model-badge:hover {
                transform: translateY(-2px) scale(1.05);
                box-shadow: 
                    0 8px 30px rgba(139, 92, 246, 0.6),
                    inset 0 1px 0 rgba(255, 255, 255, 0.3);
            }
            
            .fallback-badge {
                background: linear-gradient(135deg, 
                    rgba(245, 158, 11, 0.8), 
                    rgba(249, 115, 22, 0.9));
                backdrop-filter: blur(10px) saturate(180%);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
                display: inline-block;
                margin: 0.2rem 0.2rem;
                box-shadow: 
                    0 4px 20px rgba(245, 158, 11, 0.4),
                    inset 0 1px 0 rgba(255, 255, 255, 0.2);
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.8; }
            }
            
            /* Enhanced Privacy Badge */
            .privacy-high { 
                background: linear-gradient(135deg, 
                    rgba(168, 85, 247, 0.2), 
                    rgba(139, 92, 246, 0.3));
                backdrop-filter: blur(10px);
                border: 1px solid rgba(168, 85, 247, 0.4);
                color: #a855f7;
                font-weight: 600;
                padding: 0.5rem 1rem;
                border-radius: 12px;
                display: inline-block;
                box-shadow: 0 4px 15px rgba(168, 85, 247, 0.2);
                position: relative;
                overflow: hidden;
            }
            
            .privacy-high::before {
                content: '🔒';
                margin-right: 0.5rem;
                animation: lockPulse 2s infinite;
            }
            
            @keyframes lockPulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
            
            /* Glassmorphism Chat Messages */
            .stChatMessage {
                background: var(--glass-bg) !important;
                backdrop-filter: blur(15px) saturate(180%) !important;
                border: 1px solid var(--glass-border) !important;
                border-radius: 20px !important;
                margin-bottom: 1.5rem !important;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                transform: translateY(0) !important;
            }
            
            .stChatMessage:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3) !important;
                border-color: rgba(139, 92, 246, 0.3) !important;
            }
            
            /* Enhanced Buttons */
            .stButton > button {
                background: linear-gradient(135deg, 
                    rgba(139, 92, 246, 0.8), 
                    rgba(168, 85, 247, 0.9)) !important;
                backdrop-filter: blur(10px) !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                color: white !important;
                border-radius: 16px !important;
                padding: 0.75rem 1.5rem !important;
                font-weight: 600 !important;
                font-size: 0.9rem !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4) !important;
                position: relative !important;
                overflow: hidden !important;
            }
            
            .stButton > button:hover {
                transform: translateY(-2px) scale(1.02) !important;
                box-shadow: 0 8px 30px rgba(139, 92, 246, 0.6) !important;
                background: linear-gradient(135deg, 
                    rgba(139, 92, 246, 0.9), 
                    rgba(168, 85, 247, 1)) !important;
            }
            
            .stButton > button:active {
                transform: translateY(0) scale(0.98) !important;
            }
            
            /* Loading Animations */
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            /* Smooth Page Load */
            .stApp > div {
                animation: fadeInUp 0.8s ease-out;
            }
            
            /* Text Enhancements */
            .stMarkdown, .stText, p {
                color: var(--text-primary) !important;
                line-height: 1.6 !important;
            }
            
            h1, h2, h3 {
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-weight: 700;
            }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Light theme with glassmorphism and modern effects
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            /* Light Theme Variables */
            :root {
                --bg-primary: #ffffff;
                --bg-secondary: #f8fafc;
                --bg-tertiary: #f1f5f9;
                --bg-glass: rgba(255, 255, 255, 0.7);
                --text-primary: #1e293b;
                --text-secondary: #64748b;
                --text-tertiary: #94a3b8;
                --accent-primary: #667eea;
                --accent-secondary: #764ba2;
                --accent-glow: rgba(102, 126, 234, 0.4);
                --success: #10b981;
                --warning: #f59e0b;
                --error: #ef4444;
                --border: rgba(0, 0, 0, 0.1);
                --glass-bg: rgba(255, 255, 255, 0.8);
                --glass-border: rgba(0, 0, 0, 0.1);
            }
            
            /* Global Styles */
            * {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            /* Animated Background */
            .stApp {
                background: 
                    radial-gradient(circle at 20% 80%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(118, 75, 162, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 40% 40%, rgba(16, 185, 129, 0.05) 0%, transparent 50%),
                    linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #f1f5f9 100%);
                background-attachment: fixed;
                color: var(--text-primary);
                min-height: 100vh;
                animation: backgroundShift 20s ease-in-out infinite;
            }
            
            @keyframes backgroundShift {
                0%, 100% { background-position: 0% 0%, 100% 100%, 50% 50%; }
                50% { background-position: 100% 100%, 0% 0%, 25% 75%; }
            }
            
            /* Glassmorphism Sidebar */
            .css-1d391kg, .css-1544g2n, .stSidebar > div {
                background: var(--glass-bg) !important;
                backdrop-filter: blur(20px) saturate(180%) !important;
                border-right: 1px solid var(--glass-border) !important;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
            }
            
            /* Ultra-Modern Hero Section */
            .hero-section {
                background: linear-gradient(135deg, 
                    rgba(102, 126, 234, 0.9) 0%, 
                    rgba(118, 75, 162, 0.8) 50%,
                    rgba(16, 185, 129, 0.9) 100%);
                backdrop-filter: blur(20px) saturate(180%);
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 3rem 2rem;
                border-radius: 24px;
                text-align: center;
                margin-bottom: 2rem;
                box-shadow: 
                    0 20px 60px rgba(102, 126, 234, 0.2),
                    0 8px 32px rgba(0, 0, 0, 0.1),
                    inset 0 1px 0 rgba(255, 255, 255, 0.3);
                position: relative;
                overflow: hidden;
                animation: heroFloat 6s ease-in-out infinite;
            }
            
            .hero-section::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, 
                    transparent, 
                    rgba(255, 255, 255, 0.2), 
                    transparent);
                animation: shimmer 3s infinite;
            }
            
            @keyframes heroFloat {
                0%, 100% { transform: translateY(0px) rotate(0deg); }
                50% { transform: translateY(-5px) rotate(0.5deg); }
            }
            
            @keyframes shimmer {
                0% { left: -100%; }
                100% { left: 100%; }
            }
            
            /* Rest of light theme styles... */
            .model-badge {
                background: linear-gradient(135deg, 
                    rgba(102, 126, 234, 0.9), 
                    rgba(118, 75, 162, 0.9));
                backdrop-filter: blur(10px) saturate(180%);
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
                display: inline-block;
                margin: 0.2rem 0.2rem;
                box-shadow: 
                    0 4px 20px rgba(102, 126, 234, 0.3),
                    inset 0 1px 0 rgba(255, 255, 255, 0.3);
                transform: translateY(0);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            .model-badge:hover {
                transform: translateY(-2px) scale(1.05);
                box-shadow: 
                    0 8px 30px rgba(102, 126, 234, 0.5),
                    inset 0 1px 0 rgba(255, 255, 255, 0.4);
            }
            
            /* Modern Chat Interface with Avatars */
            .chat-container {
                display: flex;
                align-items: flex-start;
                margin-bottom: 2rem;
                gap: 1rem;
                padding: 1rem;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
            }
            
            .user-message {
                flex-direction: row-reverse;
                background: linear-gradient(135deg, 
                    rgba(102, 126, 234, 0.1), 
                    rgba(118, 75, 162, 0.05));
                border: 1px solid rgba(102, 126, 234, 0.2);
                margin-left: 2rem;
            }
            
            .assistant-message {
                background: linear-gradient(135deg, 
                    rgba(255, 255, 255, 0.1), 
                    rgba(255, 255, 255, 0.05));
                border: 1px solid rgba(255, 255, 255, 0.1);
                margin-right: 2rem;
            }
            
            .chat-avatar {
                flex-shrink: 0;
                position: relative;
            }
            
            .avatar-circle {
                width: 48px;
                height: 48px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                backdrop-filter: blur(20px);
                border: 2px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                position: relative;
                overflow: hidden;
            }
            
            .user-avatar .avatar-circle {
                background: linear-gradient(135deg, 
                    rgba(102, 126, 234, 0.8), 
                    rgba(118, 75, 162, 0.9));
            }
            
            .assistant-avatar .avatar-circle {
                background: linear-gradient(135deg, 
                    rgba(16, 185, 129, 0.8), 
                    rgba(52, 211, 153, 0.9));
            }
            
            .llama-bubble .avatar-circle {
                background: linear-gradient(135deg, 
                    rgba(245, 158, 11, 0.8), 
                    rgba(251, 191, 36, 0.9));
            }
            
            .llava-bubble .avatar-circle {
                background: linear-gradient(135deg, 
                    rgba(139, 92, 246, 0.8), 
                    rgba(168, 85, 247, 0.9));
            }
            
            .gpt-bubble .avatar-circle {
                background: linear-gradient(135deg, 
                    rgba(16, 185, 129, 0.8), 
                    rgba(52, 211, 153, 0.9));
            }
            
            .claude-bubble .avatar-circle {
                background: linear-gradient(135deg, 
                    rgba(99, 102, 241, 0.8), 
                    rgba(124, 58, 237, 0.9));
            }
            
            .chat-bubble {
                flex: 1;
                padding: 1.5rem;
                border-radius: 20px;
                backdrop-filter: blur(15px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                position: relative;
                overflow: hidden;
            }
            
            .user-bubble {
                background: linear-gradient(135deg, 
                    rgba(102, 126, 234, 0.15), 
                    rgba(118, 75, 162, 0.1));
                margin-left: 1rem;
            }
            
            .assistant-bubble {
                background: linear-gradient(135deg, 
                    rgba(255, 255, 255, 0.08), 
                    rgba(255, 255, 255, 0.04));
                margin-right: 1rem;
            }
            
            .chat-content {
                font-size: 1rem;
                line-height: 1.6;
                margin-bottom: 0.5rem;
                color: var(--text-primary);
            }
            
            .chat-timestamp {
                font-size: 0.75rem;
                color: var(--text-secondary);
                opacity: 0.7;
            }
            
            .model-info {
                margin-bottom: 1rem;
            }
            
            /* Enhanced typing animation */
            .typing-indicator {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                padding: 1rem;
                background: var(--glass-bg);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                margin: 1rem 0;
                border: 1px solid var(--glass-border);
            }
            
            .typing-dots {
                display: flex;
                gap: 0.25rem;
            }
            
            .typing-dot {
                width: 8px;
                height: 8px;
                background: var(--accent-primary);
                border-radius: 50%;
                animation: typingBounce 1.4s infinite ease-in-out;
            }
            
            .typing-dot:nth-child(1) { animation-delay: -0.32s; }
            .typing-dot:nth-child(2) { animation-delay: -0.16s; }
            
            @keyframes typingBounce {
                0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
                40% { transform: scale(1.2); opacity: 1; }
            }
            
            /* Mobile-First Responsive Design */
            @media (max-width: 768px) {
                .hero-section {
                    padding: 2rem 1rem;
                    margin-bottom: 1rem;
                }
                
                .hero-title {
                    font-size: 2rem;
                }
                
                .hero-subtitle {
                    font-size: 1rem;
                }
                
                .chat-container {
                    padding: 0.75rem;
                    margin-bottom: 1rem;
                    margin-left: 0.5rem !important;
                    margin-right: 0.5rem !important;
                }
                
                .avatar-circle {
                    width: 36px;
                    height: 36px;
                    font-size: 1.2rem;
                }
                
                .chat-bubble {
                    padding: 1rem;
                }
                
                .user-bubble {
                    margin-left: 0.5rem;
                }
                
                .assistant-bubble {
                    margin-right: 0.5rem;
                }
                
                .model-badge, .fallback-badge {
                    padding: 0.3rem 0.6rem;
                    font-size: 0.7rem;
                }
                
                .stApp {
                    background-attachment: scroll;
                }
            }
            
            /* Tablet Responsive */
            @media (min-width: 769px) and (max-width: 1024px) {
                .chat-container {
                    margin-left: 1rem !important;
                    margin-right: 1rem !important;
                }
                
                .hero-section {
                    padding: 2.5rem 1.5rem;
                }
            }
            
            /* Touch Enhancements */
            @media (hover: none) and (pointer: coarse) {
                .stButton > button {
                    padding: 1rem 1.5rem !important;
                    font-size: 1rem !important;
                }
                
                .model-badge:hover {
                    transform: none;
                }
                
                .chat-container:hover {
                    transform: none;
                }
            }
            
            /* Enhanced Accessibility */
            @media (prefers-reduced-motion: reduce) {
                * {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                }
                
                .backgroundShift {
                    animation: none;
                }
                
                .heroFloat {
                    animation: none;
                }
            }
            
            /* High Contrast Mode */
            @media (prefers-contrast: high) {
                .hero-section,
                .chat-bubble,
                .model-badge {
                    border: 2px solid;
                }
                
                .glass-bg {
                    background: rgba(255, 255, 255, 0.95) !important;
                }
            }
        </style>
        """, unsafe_allow_html=True)



def get_env_status() -> EnvStatus:
    """Check environment status for health monitoring"""
    # Check OpenAI API key  
    openai_key_present = bool(os.getenv("OPENAI_API_KEY")) and os.getenv("OPENAI_API_KEY") != "REPLACE_ME"
    
    # Check Ollama availability - simplified approach
    ollama_ok = False
    ollama_error = None
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            ollama_ok = True
        else:
            ollama_error = f"HTTP status: {response.status_code}"
    except requests.exceptions.ConnectionError:
        ollama_error = "Connection refused - Ollama not running"
    except requests.exceptions.Timeout:
        ollama_error = "Connection timeout - Ollama may be starting"
    except Exception as e:
        ollama_error = f"HTTP error: {str(e)[:50]}"
    
    return EnvStatus(
        openai_available=openai_key_present,
        ollama_available=ollama_ok,
        ollama_error=ollama_error
    )

def b64_image(uploaded_file) -> str:
    """Convert uploaded file to base64 encoded PNG"""
    # Open and convert to RGB to ensure compatibility
    image = Image.open(uploaded_file)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert to base64
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    img_bytes = buffer.getvalue()
    return base64.b64encode(img_bytes).decode('utf-8')

def sanitize_user_text(text: str) -> str:
    """Sanitize user input for security with prompt injection guards"""
    if not text or not text.strip():
        return ""
    
    # Strip control characters (keep newlines and tabs)
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    
    # Trim whitespace
    text = text.strip()
    
    # Basic prompt-injection guard: remove suspicious lines
    lines = text.split('\n')
    filtered_lines = []
    for line in lines:
        # Remove lines that start with common injection patterns
        if re.match(r'(?i)^(system:|ignore previous|you are now|forget everything|new instructions)', line.strip()):
            continue  # Skip this line
        filtered_lines.append(line)
    
    text = '\n'.join(filtered_lines)
    
    # Cap length at 4000 characters
    if len(text) > 4000:
        text = text[:4000] + "..."
    
    return text

def is_creative_or_complex(text: str) -> bool:
    """
    Determine if text requires creative/complex reasoning per spec
    
    Rules:
    - len(text) > 180 OR
    - matches creative keywords OR  
    - contains \n\n (multiple paragraphs)
    """
    if len(text) > 180:
        return True
    
    if '\n\n' in text:
        return True
    
    # Exact keywords per spec
    if re.search(r'(?i)\b(poem|story|design|architecture|brainstorm|write code|generate code|strategy|research plan|product spec)\b', text):
        return True
    
    return False

def route_model(has_image: bool, text: str, privacy: str, env: EnvStatus) -> str:
    """
    Route to appropriate model per behavior contracts
    
    Rules:
    - If has_image: "ollama/llava"
    - Elif privacy=="High": "ollama/llama3:8b" 
    - Elif is_creative_or_complex(text) and env.openai_key_present: cloud model
    - Else: "ollama/llama3:8b"
    """
    if has_image:
        return "ollama/llava"
    elif privacy == "High":
        return "ollama/llama3:8b"
    elif is_creative_or_complex(text) and env.openai_available:
        # Use better model for complex tasks - supports OpenRouter
        api_key = os.getenv("OPENAI_API_KEY", "")
        if api_key.startswith("sk-or-"):
            # OpenRouter key detected - use a good model
            return "openrouter/anthropic/claude-3.5-sonnet"
        else:
            # Regular OpenAI key
            return "openai/gpt-4o"
    else:
        return "ollama/llama3:8b"

def get_content(response) -> str:
    """Extract content from LiteLLM response safely"""
    try:
        return response.choices[0].message.content
    except (AttributeError, IndexError, KeyError):
        # Fallback for dict-like responses
        if hasattr(response, 'get'):
            return response.get('content', 'No response content')
        return str(response)

def call_model(prompt: str, model: str, image_b64: Optional[str] = None) -> ModelCall:
    """
    Call a model via LiteLLM with proper error handling
    
    Returns ModelCall with content, model used, and fallback status
    """
    # Try native Ollama client for Ollama models if LiteLLM fails
    if model.startswith("ollama/") and not image_b64:
        try:
            import ollama
            model_name = model.replace("ollama/", "")
            response = ollama.chat(model=model_name, messages=[
                {"role": "user", "content": prompt}
            ])
            return ModelCall(
                content=response['message']['content'],
                model_used=model
            )
        except Exception as ollama_error:
            print(f"Native Ollama failed: {ollama_error}")
            # Fall through to LiteLLM
    
    try:
        if model == "ollama/llava" and image_b64:
            # LLaVA with image - use Ollama format
            response = litellm.completion(
                model="ollama/llava",
                messages=[{"role": "user", "content": prompt}],
                extra_body={"images": [image_b64]},
                timeout=int(os.getenv("LITELLM_TIMEOUT", "60"))
            )
        elif model == "ollama/llama3:8b":
            # Local Llama3
            response = litellm.completion(
                model="ollama/llama3:8b", 
                messages=[{"role": "user", "content": prompt}],
                timeout=int(os.getenv("LITELLM_TIMEOUT", "60"))
            )
        elif model == "openai/gpt-4o":
            # OpenAI GPT-4o
            response = litellm.completion(
                model="openai/gpt-4o", 
                messages=[{"role": "user", "content": prompt}],
                timeout=int(os.getenv("LITELLM_TIMEOUT", "60"))
            )
        elif model.startswith("openrouter/"):
            # OpenRouter models - ensure proper API key handling
            api_key = os.getenv("OPENAI_API_KEY")
            response = litellm.completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                timeout=int(os.getenv("LITELLM_TIMEOUT", "60")),
                api_key=api_key
            )
        else:
            return ModelCall(
                content=f"Unknown model: {model}",
                model_used=model,
                error=f"Unsupported model: {model}"
            )
        
        content = get_content(response)
        return ModelCall(content=content, model_used=model)
        
    except Exception as e:
        error_msg = str(e)
        return ModelCall(
            content=f"Error calling {model}: {error_msg}",
            model_used=model,
            error=error_msg
        )

def process_input(text: str, uploaded_file, privacy: str, env: EnvStatus) -> ModelCall:
    """
    Process user input and return model response with fallback handling
    
    Behavior contracts:
    - If image + text: prepend "Use the image to answer:" to prompt
    - If privacy=High: force local models only
    - If GPT-4o fails: auto-fallback to Llama3 with "(fallback)" notation
    """
    # Sanitize input
    clean_text = sanitize_user_text(text)
    if not clean_text:
        return ModelCall(
            content="Please provide a valid input.",
            model_used="system",
            error="Empty input"
        )
    
    # Handle image input
    image_b64 = None
    has_image = uploaded_file is not None
    if has_image:
        try:
            image_b64 = b64_image(uploaded_file)
            # Prepend instruction for vision model
            clean_text = f"Use the image to answer: {clean_text}"
        except Exception as e:
            return ModelCall(
                content=f"Error processing image: {str(e)}",
                model_used="system",
                error=str(e)
            )
    
    # Route to appropriate model
    selected_model = route_model(has_image, clean_text, privacy, env)
    
    # Try primary model
    result = call_model(clean_text, selected_model, image_b64)
    
    # Handle GPT-4o fallback with proper annotation
    if (result.error and 
        selected_model == "openai/gpt-4o" and 
        env.ollama_available):
        
        # Fallback to local Llama3
        fallback_result = call_model(clean_text, "ollama/llama3:8b", image_b64)
        if not fallback_result.error:
            # Increment fallback counter
            st.session_state.metrics["fallbacks"] += 1
            return ModelCall(
                content=fallback_result.content + " (fallback to local)",
                model_used="ollama/llama3:8b",
                is_fallback=True
            )
        else:
            # If fallback also fails, return error with suggestion
            return ModelCall(
                content="OpenAI quota exceeded and local fallback failed. Try setting Privacy to 'High' to use local models only.",
                model_used="system",
                error="Both cloud and fallback failed"
            )
    
    # Update metrics for successful calls
    if not result.error:
        if selected_model == "ollama/llava":
            st.session_state.metrics["llava"] += 1
        elif selected_model == "ollama/llama3:8b":
            st.session_state.metrics["llama3"] += 1
        elif selected_model == "openai/gpt-4o":
            st.session_state.metrics["gpt4o"] += 1
        elif selected_model.startswith("openrouter/"):
            st.session_state.metrics["openrouter"] += 1
    
    return result

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Apply theme-specific styling
    apply_theme_styling()
    
    # Get environment status
    env_status = get_env_status()
    
    # Sidebar
    with st.sidebar:
        # Logo and branding
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: #667eea; margin: 0;">🤖 OmniAgent</h2>
            <p style="color: #666; font-size: 0.9rem; margin: 0;">Your AI Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Theme Toggle
        st.markdown("### 🎨 Appearance")
        current_theme = st.session_state.theme
        theme_options = ["🌞 Light", "🌙 Dark"]
        theme_index = 0 if current_theme == "light" else 1
        
        selected_theme = st.selectbox(
            "Theme",
            theme_options,
            index=theme_index,
            help="Switch between light and dark themes"
        )
        
        # Update theme if changed
        new_theme = "light" if selected_theme == "🌞 Light" else "dark"
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.rerun()
        
        st.divider()
        
        # Quick Actions
        st.markdown("### ⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 Welcome", use_container_width=True):
                st.session_state.show_welcome = True
                st.rerun()
        with col2:
            if st.button("💡 Examples", use_container_width=True):
                st.session_state.show_examples = True
        
        st.divider()
        
        st.markdown("### ⚙️ Settings")
        
        # Privacy toggle with enhanced styling
        privacy_mode = st.selectbox(
            "🔒 Privacy Mode",
            ["Normal", "High"],
            index=0 if st.session_state.privacy_mode == "Normal" else 1,
            help="High: Local models only. Normal: Allow cloud models for complex tasks."
        )
        st.session_state.privacy_mode = privacy_mode
        
        if privacy_mode == "High":
            st.markdown("""
            <div class="privacy-high">
                🔒 High Privacy Mode Active<br>
                <small>All processing stays on your computer</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("🌐 Normal Mode: Best performance with cloud enhancement")
        
        st.divider()
        
        # Enhanced Health Status
        st.markdown("### 🏥 System Health")
        
        # OpenAI/OpenRouter status
        api_key = os.getenv("OPENAI_API_KEY", "")
        if env_status.openai_available:
            if api_key.startswith("sk-or-"):
                st.markdown('<span class="health-good">✅ OpenRouter: Connected</span>', 
                           unsafe_allow_html=True)
            else:
                st.markdown('<span class="health-good">✅ OpenAI: Connected</span>', 
                           unsafe_allow_html=True)
        else:
            st.markdown('<span class="health-bad">❌ Cloud API: Not configured</span>', 
                       unsafe_allow_html=True)
        
        # Ollama status with enhanced display
        if env_status.ollama_available:
            st.markdown('<span class="health-good">✅ Ollama: Online</span>', 
                       unsafe_allow_html=True)
            st.caption("🦙 Llama3 & 👁️ LLaVA ready")
        else:
            st.markdown('<span class="health-bad">❌ Ollama: Offline</span>', 
                       unsafe_allow_html=True)
            if env_status.ollama_error:
                st.error(f"Error: {env_status.ollama_error}")
        
        st.divider()
        
        # Enhanced Model Usage Statistics
        st.markdown("### 📊 Usage Analytics")
        metrics = st.session_state.metrics
        
        if any(count > 0 for count in metrics.values()):
            # Create metrics in a more visual way
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("🦙 Llama3", metrics["llama3"], help="Local text model")
                st.metric("🌟 Cloud", metrics["gpt4o"] + metrics["openrouter"], 
                         help="GPT-4o + OpenRouter")
            
            with col2:
                st.metric("👁️ LLaVA", metrics["llava"], help="Vision model")
                st.metric("🔄 Fallbacks", metrics["fallbacks"], help="Cloud→Local fallbacks")
            
            # Total queries
            total = sum(metrics.values())
            st.info(f"**Total Queries**: {total}")
            
            # Usage distribution
            if total > 0:
                local_pct = ((metrics["llama3"] + metrics["llava"]) / total) * 100
                st.progress(local_pct / 100)
                st.caption(f"🏠 {local_pct:.0f}% Local Processing")
        else:
            st.info("🌟 No queries yet - start chatting to see analytics!")
        
        st.divider()
        
        # Clear chat button with confirmation
        if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.session_state.metrics = {
                "llava": 0,
                "llama3": 0, 
                "gpt4o": 0,
                "openrouter": 0,
                "fallbacks": 0
            }
            st.session_state.show_welcome = True
            st.success("Chat cleared! 🧹")
            st.rerun()
    
    # Clean welcome message for new users
    if len(st.session_state.messages) == 0:
        theme_emoji = "🌙" if st.session_state.theme == "dark" else "🌞"
        theme_name = "Dark" if st.session_state.theme == "dark" else "Light"
        
        st.markdown(f"""
        <div class="hero-section">
            <div class="hero-title">🤖 OmniAgent</div>
            <div class="hero-subtitle">Your Intelligent Multi-Modal AI Assistant</div>
            <div class="hero-description">
                Privacy-first AI that automatically routes your queries to the best available model<br>
                Currently using {theme_emoji} {theme_name} theme • Start by typing a message or uploading an image below!
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat history with ultra-modern styling and avatars
    for i, msg in enumerate(st.session_state.messages):
        role = msg["role"]
        content = msg["content"]
        
        if role == "user":
            # User message with modern styling
            st.markdown(f"""
            <div class="chat-container user-message" style="animation-delay: {i * 0.1}s;">
                <div class="chat-avatar user-avatar">
                    <div class="avatar-circle">👤</div>
                </div>
                <div class="chat-bubble user-bubble">
                    <div class="chat-content">
                        {content}
                    </div>
                    <div class="chat-timestamp">You</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            # Assistant message with model-specific avatar and enhanced styling
            model_name = msg.get("model", "AI").split('/')[-1] if '/' in msg.get("model", "AI") else msg.get("model", "AI")
            is_fallback = msg.get("is_fallback", False)
            
            # Determine avatar and colors based on model
            if "llama" in model_name.lower():
                avatar_emoji = "🦙"
                bubble_class = "llama-bubble"
            elif "llava" in model_name.lower():
                avatar_emoji = "👁️"
                bubble_class = "llava-bubble"
            elif "gpt" in model_name.lower():
                avatar_emoji = "🤖"
                bubble_class = "gpt-bubble"
            elif "claude" in model_name.lower():
                avatar_emoji = "🧠"
                bubble_class = "claude-bubble"
            else:
                avatar_emoji = "🌟"
                bubble_class = "ai-bubble"
            
            # Model badge
            badge_class = "fallback-badge" if is_fallback else "model-badge"
            badge_text = f"🔄 {model_name} (fallback)" if is_fallback else f"{avatar_emoji} {model_name}"
            
            st.markdown(f"""
            <div class="chat-container assistant-message" style="animation-delay: {i * 0.1}s;">
                <div class="chat-avatar assistant-avatar">
                    <div class="avatar-circle {bubble_class}">
                        {avatar_emoji}
                    </div>
                </div>
                <div class="chat-bubble assistant-bubble {bubble_class}">
                    <div class="model-info">
                        <div class="{badge_class}">{badge_text}</div>
                    </div>
                    <div class="chat-content">
                        {content}
                    </div>
                    <div class="chat-timestamp">AI Assistant</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Ultra-Modern Input Area with Smooth Animations
    st.markdown("""
    <div style="
        background: var(--glass-bg);
        backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        animation: fadeInUp 0.8s ease-out;
    ">
        <h4 style="margin: 0 0 1rem 0; color: var(--text-primary); font-weight: 600;">
            💬 Start Your Conversation
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Image uploader with modern styling
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "📷 Upload an image for analysis",
            type=["png", "jpg", "jpeg"],
            help="Upload an image to analyze with LLaVA vision model",
            label_visibility="collapsed"
        )
        
    with col2:
        if uploaded_file:
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(52, 211, 153, 0.1));
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 12px;
                padding: 0.75rem;
                text-align: center;
                animation: pulse 2s infinite;
            ">
                <span style="color: #10b981; font-weight: 600;">✅ Image Ready!</span><br>
                <small style="color: #6b7280;">👁️ LLaVA Vision</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            privacy = st.session_state.privacy_mode
            if privacy == "High":
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(168, 85, 247, 0.1));
                    border: 1px solid rgba(139, 92, 246, 0.3);
                    border-radius: 12px;
                    padding: 0.75rem;
                    text-align: center;
                ">
                    <span style="color: #8b5cf6; font-weight: 600;">🔒 Private Mode</span><br>
                    <small style="color: #6b7280;">🦙 Local Only</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.1));
                    border: 1px solid rgba(102, 126, 234, 0.3);
                    border-radius: 12px;
                    padding: 0.75rem;
                    text-align: center;
                ">
                    <span style="color: #667eea; font-weight: 600;">🌟 Smart Route</span><br>
                    <small style="color: #6b7280;">⚡ Auto-select</small>
                </div>
                """, unsafe_allow_html=True)
    
    # Add context hints
    st.markdown(f"""
    <div style="
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1rem;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 1rem;
        font-size: 0.9rem;
        color: var(--text-secondary);
        flex-wrap: wrap;
        justify-content: center;
    ">
        <span>🎯 {st.session_state.privacy_mode} Privacy</span>
        <span>•</span>
        <span>⚡ Auto-routing enabled</span>
        <span>•</span>
        <span>🧠 Multi-modal ready</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Dynamic placeholder text
    if len(st.session_state.messages) == 0:
        placeholder_text = "👋 Ask anything! Try 'Explain quantum computing' or upload an image..."
    elif uploaded_file:
        placeholder_text = "🖼️ What would you like to know about this image?"
    else:
        placeholder_text = "💭 Continue the conversation... I'm listening!"
    
    if user_input := st.chat_input(placeholder_text):
        # Add user message
        st.session_state.messages.append({
            "role": "user", 
            "content": user_input,
            "timestamp": time.time()
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Process and display response with enhanced feedback
        with st.chat_message("assistant"):
            # Show processing indicator with model prediction
            if uploaded_file:
                spinner_text = "👁️ Analyzing image with LLaVA..."
            elif st.session_state.privacy_mode == "High":
                spinner_text = "🦙 Processing with local Llama3..."
            elif is_creative_or_complex(user_input):
                spinner_text = "🌟 Thinking deeply with advanced model..."
            else:
                spinner_text = "🦙 Processing with Llama3..."
                
            with st.spinner(spinner_text):
                result = process_input(user_input, uploaded_file, privacy_mode, env_status)
                
                # Display response with enhanced styling
                if result.error:
                    st.error(f"❌ {result.error}")
                    content = result.content
                    model_name = "error"
                    is_fallback = False
                else:
                    content = result.content
                    model_name = result.model_used.split('/')[-1] if '/' in result.model_used else result.model_used
                    is_fallback = result.is_fallback
                
                # Display content
                st.write(content)
                
                # Enhanced model badge
                if not result.error:
                    if is_fallback:
                        st.markdown(f'<span class="fallback-badge">🔄 {model_name} (fallback)</span>', 
                                   unsafe_allow_html=True)
                    else:
                        # Model-specific emojis and styling
                        if "llama3" in model_name.lower():
                            emoji = "🦙"
                        elif "llava" in model_name.lower():
                            emoji = "👁️"
                        elif any(x in model_name.lower() for x in ["claude", "gpt"]):
                            emoji = "🌟"
                        else:
                            emoji = "🤖"
                        
                        st.markdown(f'<span class="model-badge">{emoji} {model_name}</span>', 
                                   unsafe_allow_html=True)
                
                # Save assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": content,
                    "model": result.model_used,
                    "is_fallback": is_fallback,
                    "timestamp": time.time()
                })
    
    # Comprehensive Help Section at Bottom
    st.markdown("---")
    st.markdown("## ✨ Key Capabilities")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **💬 Smart Text Processing**
        
        Ask questions, get explanations, creative writing, code help, and more. Automatically routes simple queries to local models and complex ones to cloud AI.
        """)
        
        st.markdown("""
        **🔒 Privacy Protection**
        
        Choose between Normal mode (best performance) or High mode (local-only processing). Your data stays private with transparent model routing decisions.
        """)
    
    with col2:
        st.markdown("""
        **🖼️ Image Analysis**
        
        Upload images and ask questions about them. Describe scenes, read text, analyze compositions, and understand visual content using local LLaVA model.
        """)
        
        st.markdown("""
        **🏠 Local-First Design**
        
        Powered by local Ollama models (Llama3, LLaVA) with optional cloud enhancement. Works completely offline in High privacy mode.
        """)
    
    with col3:
        st.markdown("""
        **⚡ Intelligent Routing**
        
        Automatically selects the optimal model based on your query complexity, privacy settings, and available resources with seamless fallback protection.
        """)
        
        st.markdown("""
        **📊 Usage Analytics**
        
        Track which models you use most, monitor performance, and understand your AI assistant usage patterns with detailed metrics.
        """)
    
    st.markdown("### 🚀 Quick Start Guide")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📝 Try These Text Examples:**
        - Simple: *"What is the capital of France?"*
        - Creative: *"Write a poem about artificial intelligence"*
        - Complex: *"Explain quantum computing in simple terms"*
        - Code: *"Write a Python function to sort a list"*
        """)
        
    with col2:
        st.markdown("""
        **🖼️ Try Image Analysis:**
        1. Click "📷 Upload an image" above
        2. Choose any PNG, JPG, or JPEG file
        3. Ask: *"What do you see in this image?"*
        4. Or: *"Describe the colors and mood"*
        """)
    
    st.markdown("### 🔒 Privacy Modes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **Normal Mode** (Recommended)
        - ✅ Best performance for complex tasks
        - ✅ Automatic model selection
        - ✅ Cloud models for advanced reasoning
        - ✅ Local fallback protection
        """)
        
    with col2:
        st.success("""
        **High Privacy Mode**
        - 🔒 100% local processing
        - 🔒 No data leaves your computer
        - 🔒 Completely free to use
        - 🔒 Works offline
        """)
    
    st.markdown("### 🧠 Available Models")
    
    model_info = {
        "🦙 Llama3 (Local)": "Fast, efficient text model for everyday questions and tasks",
        "👁️ LLaVA (Local)": "Vision-language model for image analysis and description", 
        "🌟 Claude/GPT-4o (Cloud)": "Advanced reasoning for complex, creative, and analytical tasks"
    }
    
    for model, description in model_info.items():
        st.markdown(f"**{model}**: {description}")
    
    # Footer credits
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; color: #666;">
        <small>
            🤖 <strong>OmniAgent</strong> - Privacy-First AI Assistant<br>
            Powered by 🦙 Ollama • 🌟 OpenRouter/OpenAI • Built with ❤️ using Streamlit
        </small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
