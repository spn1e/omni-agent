# 🚀 Streamlit Cloud Deployment Guide

Deploy your OmniAgent to Streamlit Community Cloud for free and make it accessible worldwide!

## 📋 Prerequisites

1. **GitHub Account**: Your code must be in a GitHub repository
2. **Streamlit Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **API Keys**: At least one of these:
   - OpenAI API Key (recommended)
   - Anthropic API Key
   - OpenRouter API Key

## 🎯 Step 1: Prepare Your Repository

Your repository should contain:
```
omni-agent/
├── app_cloud.py              # Cloud-optimized version
├── requirements_cloud.txt    # Cloud dependencies
├── .streamlit/
│   └── secrets.toml.example  # Secrets template
└── DEPLOYMENT.md            # This guide
```

## 🌐 Step 2: Deploy to Streamlit Cloud

### 2.1 Access Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**

### 2.2 Configure Your App
Fill in the deployment form:

**Repository**: `spn1e/omni-agent` (your GitHub username/repo)
**Branch**: `main` 
**Main file path**: `app_cloud.py`
**App URL**: `https://omni-agent-yourname.streamlit.app` (customize as desired)

### 2.3 Advanced Settings
Click **"Advanced settings"** and set:

**Python version**: `3.11`
**Requirements file**: `requirements_cloud.txt`

## 🔐 Step 3: Configure Secrets (API Keys)

### 3.1 Add Secrets in Streamlit Cloud
1. After creating the app, go to **"Secrets"** in the app settings
2. Add your API keys in TOML format:

```toml
# Choose ONE of these API providers:

# Option A: OpenAI (Recommended)
OPENAI_API_KEY = "sk-your-actual-openai-key-here"

# Option B: Anthropic Claude
ANTHROPIC_API_KEY = "sk-ant-your-actual-anthropic-key-here"

# Option C: OpenRouter (Multiple models)
OPENROUTER_API_KEY = "sk-or-your-actual-openrouter-key-here"

# Optional Settings
LITELLM_TIMEOUT = "60"
PRIVACY_DEFAULT = "Normal"
```

### 3.2 Get API Keys

#### OpenAI API Key (Recommended)
1. Visit [platform.openai.com](https://platform.openai.com)
2. Sign up/Sign in
3. Go to API Keys section
4. Create a new key
5. **Important**: Add billing information for usage

#### Anthropic API Key
1. Visit [console.anthropic.com](https://console.anthropic.com)
2. Sign up for Claude API access
3. Generate an API key
4. Add credits to your account

#### OpenRouter API Key
1. Visit [openrouter.ai](https://openrouter.ai)
2. Sign up and get API access
3. Add credits to your account
4. Generate an API key

## 🚀 Step 4: Deploy!

1. Click **"Deploy!"** in Streamlit Cloud
2. Wait for the app to build (2-3 minutes)
3. Your app will be live at: `https://your-app-name.streamlit.app`

## 🎉 Step 5: Test Your Deployment

### 5.1 Basic Functionality
- ✅ App loads without errors
- ✅ Sidebar shows API status (green checkmarks)
- ✅ Can send text messages
- ✅ Can upload and analyze images
- ✅ Privacy mode toggle works

### 5.2 Model Routing Test
1. **Simple Query**: "What is the capital of France?" → Should use fast model
2. **Complex Query**: "Write a detailed business plan for an AI startup" → Should use advanced model
3. **Image Analysis**: Upload an image and ask "What do you see?" → Should use vision model

## 🔧 Troubleshooting

### App Won't Start
- Check logs in Streamlit Cloud dashboard
- Verify `requirements_cloud.txt` format
- Ensure `app_cloud.py` has no syntax errors

### API Errors
- Verify API keys are correctly set in Secrets
- Check API key format (OpenAI: `sk-...`, Anthropic: `sk-ant-...`)
- Ensure you have credits/billing set up

### Model Not Available
- Check API provider status
- Verify your API plan includes the model
- Try switching to a different provider in Privacy settings

## 💡 Cost Management

### Free Tier Limits
- **Streamlit Cloud**: Unlimited (free forever)
- **OpenAI**: $5 free credit for new accounts
- **Anthropic**: $5 free credit for new accounts
- **OpenRouter**: Varies by model

### Cost Optimization Tips
1. Use **Privacy Mode: High** for cheaper models
2. Set usage limits in your API provider dashboard
3. Monitor usage in the app sidebar
4. Consider switching between providers based on cost

## 🔄 Updates and Maintenance

### Update Your App
1. Push changes to your GitHub repository
2. Streamlit Cloud will auto-redeploy
3. Changes appear within 1-2 minutes

### Monitor Usage
- Check the sidebar metrics for model usage
- Monitor API costs in provider dashboards
- Set up billing alerts if needed

## 🎯 Production Tips

### Custom Domain (Optional)
- Streamlit Cloud provides: `your-app.streamlit.app`
- For custom domains, consider upgrading to Streamlit Cloud for Teams

### Performance Optimization
- Image uploads work best under 5MB
- Complex queries may take 10-30 seconds
- Use Privacy Mode: High for faster responses

### Security Best Practices
- Never commit API keys to GitHub
- Regularly rotate API keys
- Monitor usage for unexpected spikes
- Use environment-specific keys for testing

## 📞 Support

### Get Help
- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Community Forum**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub Issues**: Report bugs in your repository

### Common Resources
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Anthropic Claude Docs](https://docs.anthropic.com)
- [LiteLLM Docs](https://docs.litellm.ai)

---

🎉 **Congratulations!** Your OmniAgent is now live and accessible to users worldwide!

Share your app URL and let people experience the power of intelligent AI routing! 🤖✨
