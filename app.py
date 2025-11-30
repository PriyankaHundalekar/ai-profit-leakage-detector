import streamlit as st
import boto3
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from dotenv import load_dotenv
import base64
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="AI Profit Leakage Detector",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for absolutely stunning UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    .main-header {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 25px;
        margin-bottom: 3rem;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }
    
    .feature-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        margin: 1rem;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 1px solid rgba(102, 126, 234, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
        transition: left 0.5s;
    }
    
    .feature-card:hover::before {
        left: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 25px 50px rgba(102, 126, 234, 0.2);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    .feature-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 4px 8px rgba(102, 126, 234, 0.3));
    }
    
    .upload-section {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        border: 3px dashed #667eea;
        border-radius: 25px;
        padding: 3rem;
        text-align: center;
        margin: 2rem 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .upload-section::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #667eea, #764ba2, #667eea);
        border-radius: 25px;
        z-index: -1;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .upload-section:hover::before {
        opacity: 1;
    }
    
    .upload-section:hover {
        border-color: transparent;
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
    }
    
    .analysis-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border-left: 6px solid #667eea;
        transition: all 0.3s ease;
        position: relative;
    }
    
    .analysis-card:hover {
        transform: translateX(10px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.15);
    }
    
    .critical-leak {
        border-left-color: #e74c3c;
        background: linear-gradient(135deg, #fff5f5 0%, #ffe6e6 100%);
    }
    
    .warning-leak {
        border-left-color: #f39c12;
        background: linear-gradient(135deg, #fffbf0 0%, #fff3e0 100%);
    }
    
    .opportunity-card {
        background: linear-gradient(135deg, #f0fff4 0%, #e6ffed 100%);
        border-left: 6px solid #27ae60;
        padding: 2.5rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        box-shadow: 0 10px 30px rgba(39, 174, 96, 0.1);
        transition: all 0.3s ease;
    }
    
    .opportunity-card:hover {
        transform: translateX(10px);
        box-shadow: 0 15px 40px rgba(39, 174, 96, 0.2);
    }
    
    .metric-display {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 1rem;
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-display::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        transition: all 0.3s ease;
    }
    
    .metric-display:hover {
        transform: translateY(-8px) scale(1.05);
        box-shadow: 0 25px 50px rgba(102, 126, 234, 0.4);
    }
    
    .metric-display:hover::after {
        top: -25%;
        right: -25%;
    }
    
    .big-number {
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 4px 8px rgba(0,0,0,0.2);
        background: linear-gradient(45deg, #ffffff, #f0f0f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 1rem 3rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
    }
    
    .stSelectbox > div > div {
        border-radius: 15px;
        border: 2px solid rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.2);
    }
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 15px;
        border: 2px solid rgba(102, 126, 234, 0.2);
        transition: all 0.3s ease;
        font-family: 'Poppins', sans-serif;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.2);
    }
    
    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        color: white;
        margin: 0.25rem;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .critical-badge { 
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
    }
    
    .warning-badge { 
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        box-shadow: 0 4px 15px rgba(243, 156, 18, 0.3);
    }
    
    .success-badge { 
        background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
        box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
    }
    
    .info-badge { 
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
    }
    
    .tab-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: linear-gradient(135deg, #f8f9ff 0%, #e8f0ff 100%);
        padding: 0.5rem;
        border-radius: 15px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 1rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .footer-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 4rem 2rem;
        border-radius: 25px;
        text-align: center;
        margin: 3rem 0;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .footer-section::before {
        content: '';
        position: absolute;
        top: -100%;
        left: -100%;
        width: 300%;
        height: 300%;
        background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .glass-effect {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
    }
    
    h1, h2, h3, h4 {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize AWS Bedrock client
@st.cache_resource
def init_bedrock_client():
    return boto3.client(
        'bedrock-runtime',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
    )

def analyze_profit_leakage(data_text, business_type="General"):
    """Analyze business data for profit leakage using AI"""
    client = init_bedrock_client()
    
    prompt = f"""You are a senior business analyst and profit optimization expert. Analyze this business data to identify profit leakage opportunities.

BUSINESS DATA:
{data_text}

BUSINESS TYPE: {business_type}

ANALYSIS FRAMEWORK:
Identify profit leakage in these key areas:
1. REVENUE LEAKS - Lost sales, pricing issues, discount abuse
2. COST OVERRUNS - Unnecessary expenses, inefficient processes
3. OPERATIONAL INEFFICIENCIES - Waste, delays, poor resource utilization
4. CUSTOMER ISSUES - Churn, low retention, acquisition costs
5. INVENTORY PROBLEMS - Overstocking, stockouts, obsolescence
6. PRICING OPTIMIZATION - Underpricing, missed opportunities

For each identified leak, provide:
- IMPACT: High/Medium/Low financial impact
- URGENCY: Critical/Important/Monitor priority level
- ESTIMATED_LOSS: Approximate monthly/annual loss amount
- ROOT_CAUSE: Why this leak exists
- SOLUTION: Specific actionable recommendations
- TIMELINE: How quickly this can be fixed

Format your response as:
TOTAL_ESTIMATED_MONTHLY_LOSS: $[amount]
CRITICAL_LEAKS: [number]
HIGH_IMPACT_LEAKS: [number]

LEAK_1:
CATEGORY: [Revenue/Cost/Operational/Customer/Inventory/Pricing]
TITLE: [Brief descriptive title]
IMPACT: [High/Medium/Low]
URGENCY: [Critical/Important/Monitor]
ESTIMATED_LOSS: $[amount] per month
ROOT_CAUSE: [explanation]
SOLUTION: [specific recommendation]
TIMELINE: [timeframe to fix]

LEAK_2:
[continue for all identified leaks]

TOP_OPPORTUNITIES:
1. [Highest impact opportunity with estimated savings]
2. [Second highest opportunity]
3. [Third highest opportunity]

QUICK_WINS:
- [Easy to implement solutions with immediate impact]

Be specific with numbers and actionable recommendations."""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1500,
        "messages": [{"role": "user", "content": prompt}]
    })
    
    try:
        response = client.invoke_model(
            body=body,
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get('body').read())
        return response_body['content'][0]['text'].strip()
    except Exception as e:
        return f"Error analyzing profit leakage: {str(e)}"

def parse_leakage_analysis(analysis_text):
    """Parse the AI analysis into structured data"""
    try:
        result = {
            'total_loss': 0,
            'critical_leaks': 0,
            'high_impact_leaks': 0,
            'leaks': [],
            'opportunities': [],
            'quick_wins': []
        }
        
        lines = analysis_text.split('\n')
        current_leak = {}
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if 'TOTAL_ESTIMATED_MONTHLY_LOSS:' in line:
                amount = line.split('$')[-1].replace(',', '').replace(' per month', '')
                try:
                    result['total_loss'] = float(amount)
                except:
                    pass
                    
            elif 'CRITICAL_LEAKS:' in line:
                try:
                    result['critical_leaks'] = int(line.split(':')[-1].strip())
                except:
                    pass
                    
            elif 'HIGH_IMPACT_LEAKS:' in line:
                try:
                    result['high_impact_leaks'] = int(line.split(':')[-1].strip())
                except:
                    pass
                    
            elif line.startswith('LEAK_'):
                if current_leak:
                    result['leaks'].append(current_leak)
                current_leak = {}
                current_section = 'leak'
                
            elif current_section == 'leak' and ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                current_leak[key] = value
                
            elif 'TOP_OPPORTUNITIES:' in line:
                current_section = 'opportunities'
                
            elif current_section == 'opportunities' and line.startswith(('1.', '2.', '3.')):
                result['opportunities'].append(line[2:].strip())
                
            elif 'QUICK_WINS:' in line:
                current_section = 'quick_wins'
                
            elif current_section == 'quick_wins' and line.startswith('-'):
                result['quick_wins'].append(line[1:].strip())
        
        # Don't forget the last leak
        if current_leak:
            result['leaks'].append(current_leak)
            
        return result
    except Exception as e:
        return {'error': str(e)}



def analyze_document_image(image_base64, business_type):
    """Analyze business document image using AI vision"""
    client = init_bedrock_client()
    
    prompt = f"""You are a business analyst expert. Analyze this business document image and extract all relevant financial and operational data.

BUSINESS TYPE: {business_type}

EXTRACT ALL VISIBLE DATA INCLUDING:
- Revenue figures and trends
- Cost breakdowns and expenses
- Profit margins and ratios
- Customer metrics (acquisition, retention, churn)
- Operational KPIs
- Financial ratios
- Performance indicators
- Any concerning trends or issues

IMPORTANT: Read all numbers, percentages, dates, and business metrics visible in the document.

Format your response as structured business data that can be analyzed for profit leakage."""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    })
    
    try:
        response = client.invoke_model(
            body=body,
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get('body').read())
        return response_body['content'][0]['text'].strip()
    except Exception as e:
        return f"Error analyzing document image: {str(e)}"

def main():
    # Stunning Hero Section
    st.markdown("""
    <div class="main-header">
        <h1 style="font-size: 3.5rem; font-weight: 800; margin-bottom: 1rem; text-shadow: 0 4px 8px rgba(0,0,0,0.2);">
            💰 AI Profit Leakage Detector
        </h1>
        <p style="font-size: 1.4rem; margin: 1rem 0; opacity: 0.95; font-weight: 300;">
            Discover hidden profit leaks and unlock millions in revenue opportunities
        </p>
        <p style="font-size: 1.1rem; margin-top: 1.5rem; opacity: 0.85; font-weight: 400;">
            Advanced AI analyzes your business data to identify where profits are bleeding away
        </p>
        <div style="margin-top: 2rem;">
            <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1.5rem; border-radius: 25px; font-size: 0.9rem; font-weight: 500;">
                ⚡ Instant Analysis • � Acvtionable Insights • 📈 Measurable Results
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Colorful Feature Cards with Proper Text Alignment
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 20px; text-align: center; margin: 0.5rem; box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3); height: 180px; display: flex; flex-direction: column; justify-content: center; align-items: center; overflow: hidden;">
            <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">🔍</div>
            <h3 style="margin-bottom: 0.8rem; font-weight: 600; font-size: 1rem; line-height: 1.2;">Smart Detection</h3>
            <p style="opacity: 0.9; line-height: 1.3; margin: 0; font-size: 0.8rem; text-align: center; word-wrap: break-word; max-width: 100%;">AI identifies hidden profit leaks across business areas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%); color: white; padding: 1.5rem; border-radius: 20px; text-align: center; margin: 0.5rem; box-shadow: 0 15px 35px rgba(253, 121, 168, 0.3); height: 180px; display: flex; flex-direction: column; justify-content: center; align-items: center; overflow: hidden;">
            <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">💡</div>
            <h3 style="margin-bottom: 0.8rem; font-weight: 600; font-size: 1rem; line-height: 1.2;">Actionable Insights</h3>
            <p style="opacity: 0.9; line-height: 1.3; margin: 0; font-size: 0.8rem; text-align: center; word-wrap: break-word; max-width: 100%;">Get specific recommendations with quantified savings</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%); color: white; padding: 1.5rem; border-radius: 20px; text-align: center; margin: 0.5rem; box-shadow: 0 15px 35px rgba(253, 203, 110, 0.3); height: 180px; display: flex; flex-direction: column; justify-content: center; align-items: center; overflow: hidden;">
            <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">⚡</div>
            <h3 style="margin-bottom: 0.8rem; font-weight: 600; font-size: 1rem; line-height: 1.2;">Quick Wins</h3>
            <p style="opacity: 0.9; line-height: 1.3; margin: 0; font-size: 0.8rem; text-align: center; word-wrap: break-word; max-width: 100%;">Identify immediate opportunities for rapid improvement</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #00b894 0%, #00cec9 100%); color: white; padding: 1.5rem; border-radius: 20px; text-align: center; margin: 0.5rem; box-shadow: 0 15px 35px rgba(0, 184, 148, 0.3); height: 180px; display: flex; flex-direction: column; justify-content: center; align-items: center; overflow: hidden;">
            <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">📈</div>
            <h3 style="margin-bottom: 0.8rem; font-weight: 600; font-size: 1rem; line-height: 1.2;">ROI Tracking</h3>
            <p style="opacity: 0.9; line-height: 1.3; margin: 0; font-size: 0.8rem; text-align: center; word-wrap: break-word; max-width: 100%;">Measure impact and track profit recovery progress</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📊 Data Analysis", "🔍 Leak Detection Results", "💡 Profit Opportunities"])
    
    with tab1:
        st.markdown("### 📊 Business Data Input")
        
        # Business type selection
        business_type = st.selectbox(
            "🏢 Select Your Business Type:",
            ["E-commerce", "SaaS/Software", "Retail", "Manufacturing", "Services", "Restaurant/Food", "Healthcare", "General"],
            help="This helps the AI provide more targeted analysis"
        )
        
        # Data input methods
        input_method = st.radio(
            "How would you like to provide your business data?",
            ["📝 Manual Input", "📄 Upload Document"],
            horizontal=True
        )
        
        if input_method == "📝 Manual Input":
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 15px; text-align: center; margin: 1rem 0; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">💼</div>
                <h3 style="margin-bottom: 0.5rem; font-weight: 600;">Enter Your Business Data</h3>
                <p style="opacity: 0.9; margin: 0; font-size: 0.95rem;">Input your real business metrics for AI-powered analysis</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Compact input fields with styling
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #f8f9ff 0%, #e8f0ff 100%); padding: 1.5rem; border-radius: 15px; margin: 1rem 0; border-left: 4px solid #667eea;">
                    <h4 style="color: #667eea; margin-bottom: 1rem; font-size: 1.1rem;">💰 Financial Metrics</h4>
                </div>
                """, unsafe_allow_html=True)
                monthly_revenue = st.number_input("Monthly Revenue ($)", min_value=0, value=0, step=1000)
                monthly_costs = st.number_input("Monthly Costs ($)", min_value=0, value=0, step=1000)
                gross_margin = st.number_input("Gross Margin (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                operating_expenses = st.number_input("Operating Expenses ($)", min_value=0, value=0, step=1000)
                
            with col2:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #f0fff4 0%, #e6ffed 100%); padding: 1.5rem; border-radius: 15px; margin: 1rem 0; border-left: 4px solid #27ae60;">
                    <h4 style="color: #27ae60; margin-bottom: 1rem; font-size: 1.1rem;">📊 Business Metrics</h4>
                </div>
                """, unsafe_allow_html=True)
                customer_acquisition_cost = st.number_input("Customer Acquisition Cost ($)", min_value=0, value=0, step=10)
                customer_churn_rate = st.number_input("Monthly Churn Rate (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                average_order_value = st.number_input("Average Order Value ($)", min_value=0, value=0, step=5)
                return_rate = st.number_input("Return Rate (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            
            # Compact additional data input
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fff8f0 0%, #ffe6cc 100%); padding: 1.5rem; border-radius: 15px; margin: 1rem 0; border-left: 4px solid #f39c12;">
                <h4 style="color: #f39c12; margin-bottom: 1rem; font-size: 1.1rem;">📝 Additional Information (Optional)</h4>
            </div>
            """, unsafe_allow_html=True)
            additional_data = st.text_area(
                "Additional Business Context:",
                height=150,
                placeholder="Marketing spend, inventory issues, operational challenges, specific concerns...",
                help="Any additional context that might help identify profit leaks"
            )
            
            # Real-time data validation and insights
            if monthly_revenue > 0:
                # Calculate some basic metrics
                net_profit = monthly_revenue - monthly_costs - operating_expenses
                profit_margin = (net_profit / monthly_revenue * 100) if monthly_revenue > 0 else 0
                
                # Show real-time insights
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Net Profit", f"${net_profit:,.0f}", delta=f"{profit_margin:.1f}% margin")
                with col2:
                    if customer_acquisition_cost > 0 and average_order_value > 0:
                        payback_ratio = average_order_value / customer_acquisition_cost
                        st.metric("AOV/CAC Ratio", f"{payback_ratio:.1f}x", delta="Good" if payback_ratio > 3 else "Needs improvement")
                with col3:
                    if customer_churn_rate > 0:
                        st.metric("Churn Rate", f"{customer_churn_rate:.1f}%", delta="High" if customer_churn_rate > 10 else "Acceptable")
                
                # Compile the business data
                business_data = f"""
Business Type: {business_type}
Monthly Revenue: ${monthly_revenue:,}
Monthly Costs: ${monthly_costs:,}
Net Profit: ${net_profit:,}
Profit Margin: {profit_margin:.1f}%
Gross Margin: {gross_margin}%
Operating Expenses: ${operating_expenses:,}
Customer Acquisition Cost: ${customer_acquisition_cost}
Monthly Churn Rate: {customer_churn_rate}%
Average Order Value: ${average_order_value}
Return Rate: {return_rate}%

Additional Information:
{additional_data}

Key Ratios:
- AOV to CAC Ratio: {payback_ratio:.1f}x
- Monthly Profit: ${net_profit:,}
"""
                
                # Data quality indicators
                data_quality_score = 0
                quality_issues = []
                
                if monthly_revenue > monthly_costs:
                    data_quality_score += 20
                else:
                    quality_issues.append("Revenue lower than costs - check for data accuracy")
                
                if gross_margin > 0:
                    data_quality_score += 20
                else:
                    quality_issues.append("Gross margin not specified - important for analysis")
                
                if customer_acquisition_cost > 0:
                    data_quality_score += 20
                else:
                    quality_issues.append("Customer acquisition cost missing - affects customer analysis")
                
                if average_order_value > 0:
                    data_quality_score += 20
                else:
                    quality_issues.append("Average order value missing - affects revenue analysis")
                
                if customer_churn_rate >= 0:
                    data_quality_score += 20
                
                # Show data quality feedback
                if data_quality_score >= 80:
                    st.success(f"✅ Data Quality: Excellent ({data_quality_score}%) - Ready for comprehensive analysis!")
                elif data_quality_score >= 60:
                    st.info(f"📊 Data Quality: Good ({data_quality_score}%) - Analysis will be effective")
                else:
                    st.warning(f"⚠️ Data Quality: Basic ({data_quality_score}%) - Consider adding more metrics for better insights")
                
                if quality_issues:
                    with st.expander("💡 Suggestions to improve analysis quality"):
                        for issue in quality_issues:
                            st.write(f"• {issue}")
                            
            else:
                business_data = additional_data
                if not additional_data.strip():
                    st.info("💡 Please enter your business data above to begin the profit leakage analysis.")
            
        else:  # Upload Document
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 15px; text-align: center; margin: 1rem 0; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📄</div>
                <h3 style="margin-bottom: 0.5rem; font-weight: 600;">Upload Business Document</h3>
                <p style="opacity: 0.9; margin: 0; font-size: 0.95rem;">Upload financial reports or data files for instant AI analysis</p>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Upload your business document:",
                type=['txt', 'csv', 'xlsx', 'pdf', 'png', 'jpg', 'jpeg'],
                help="Supported: Text files, CSV, Excel, PDF, or images of financial documents"
            )
            
            business_data = ""
            if uploaded_file is not None:
                if uploaded_file.type.startswith('image/'):
                    st.image(uploaded_file, caption="Uploaded Business Document", use_column_width=True)
                    st.info("📸 Image uploaded! AI will extract and analyze the business data from your document.")
                    
                    # For image analysis, we'll need to use vision capabilities
                    img_byte_arr = io.BytesIO()
                    image = Image.open(uploaded_file)
                    image.save(img_byte_arr, format='JPEG')
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    # Convert image to base64 for AI analysis
                    image_base64 = base64.b64encode(img_byte_arr).decode('utf-8')
                    business_data = f"IMAGE_DOCUMENT:{image_base64}"
                    
                else:
                    try:
                        if uploaded_file.type == 'text/plain':
                            business_data = str(uploaded_file.read(), "utf-8")
                            st.success("✅ Text document uploaded and processed!")
                        elif uploaded_file.type == 'text/csv':
                            df = pd.read_csv(uploaded_file)
                            business_data = f"CSV Data Analysis:\n{df.to_string()}"
                            st.success("✅ CSV data uploaded and processed!")
                            
                            # Show preview of the data
                            st.markdown("#### 📊 Data Preview:")
                            st.dataframe(df.head())
                            
                        elif uploaded_file.name.endswith('.xlsx'):
                            df = pd.read_excel(uploaded_file)
                            business_data = f"Excel Data Analysis:\n{df.to_string()}"
                            st.success("✅ Excel file uploaded and processed!")
                            
                            # Show preview of the data
                            st.markdown("#### 📊 Data Preview:")
                            st.dataframe(df.head())
                            
                        else:
                            # For other file types, just note the upload
                            business_data = f"Document uploaded: {uploaded_file.name} - Please provide key business metrics for analysis."
                            st.success("✅ Document uploaded! Please add key metrics below for better analysis.")
                            
                            # Allow additional input for context
                            additional_context = st.text_area(
                                "Key Business Metrics from Document:",
                                height=200,
                                placeholder="Extract and enter key metrics from your uploaded document:\n- Revenue figures\n- Cost breakdowns\n- Customer metrics\n- Operational data\n- Any concerning trends or issues",
                                help="Help the AI by highlighting the most important data from your document"
                            )
                            
                            if additional_context:
                                business_data += f"\n\nKey Metrics:\n{additional_context}"
                                
                    except Exception as e:
                        st.error(f"Error processing file: {str(e)}")
                        st.info("💡 Try uploading a different format or use manual input instead.")
                        business_data = ""
            else:
                st.markdown("""
                <div style="text-align: center; padding: 2rem; background: #f8f9ff; border-radius: 15px; margin: 1rem 0;">
                    <h4>📄 Supported Document Types:</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                        <div>
                            <p><strong>📊 Data Files:</strong></p>
                            <p>• CSV spreadsheets</p>
                            <p>• Excel files (.xlsx)</p>
                            <p>• Text files (.txt)</p>
                        </div>
                        <div>
                            <p><strong>📸 Document Images:</strong></p>
                            <p>• Financial reports (JPG, PNG)</p>
                            <p>• P&L statements</p>
                            <p>• Business dashboards</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Analysis button
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Analyze Profit Leakage", type="primary", use_container_width=True):
                if business_data.strip():
                    with st.spinner("🤖 AI is analyzing your business data for profit leaks..."):
                        # Check if it's an image document
                        if business_data.startswith("IMAGE_DOCUMENT:"):
                            image_base64 = business_data.replace("IMAGE_DOCUMENT:", "")
                            # First extract data from image
                            extracted_data = analyze_document_image(image_base64, business_type)
                            # Then analyze for profit leakage
                            analysis = analyze_profit_leakage(extracted_data, business_type)
                        else:
                            # Direct analysis of text data
                            analysis = analyze_profit_leakage(business_data, business_type)
                        
                        parsed_results = parse_leakage_analysis(analysis)
                        
                        # Store results in session state
                        st.session_state.analysis_results = {
                            'raw_analysis': analysis,
                            'parsed_results': parsed_results,
                            'business_type': business_type,
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        if 'error' not in parsed_results:
                            st.success("✅ Analysis Complete! Check the 'Leak Detection Results' tab for detailed findings.")
                        else:
                            st.error(f"❌ Analysis failed: {parsed_results['error']}")
                else:
                    st.warning("⚠️ Please provide business data to analyze!")
    
    with tab2:
        st.markdown("### 🔍 Profit Leak Detection Results")
        
        if 'analysis_results' not in st.session_state:
            st.info("📊 Analyze your business data in the first tab to see profit leak detection results here!")
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #f8f9ff 0%, #e8f0ff 100%); border-radius: 20px; margin: 2rem 0;">
                <h3>🔍 What You'll Discover:</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 2rem; text-align: left;">
                    <div>
                        <h4>💸 Revenue Leaks</h4>
                        <p>• Pricing optimization opportunities</p>
                        <p>• Lost sales and conversion issues</p>
                        <p>• Discount and promotion inefficiencies</p>
                    </div>
                    <div>
                        <h4>📊 Cost Overruns</h4>
                        <p>• Unnecessary operational expenses</p>
                        <p>• Inefficient resource allocation</p>
                        <p>• Process optimization opportunities</p>
                    </div>
                    <div>
                        <h4>👥 Customer Issues</h4>
                        <p>• High churn and retention problems</p>
                        <p>• Customer acquisition inefficiencies</p>
                        <p>• Lifetime value optimization</p>
                    </div>
                    <div>
                        <h4>📦 Inventory Problems</h4>
                        <p>• Overstocking and stockout costs</p>
                        <p>• Obsolete inventory write-offs</p>
                        <p>• Supply chain inefficiencies</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            results = st.session_state.analysis_results
            parsed = results['parsed_results']
            
            # Beautiful Summary Metrics
            st.markdown("""
            <h2 style="text-align: center; color: #2c3e50; margin: 2rem 0; font-size: 2.5rem;">
                📊 Profit Leakage Analysis
            </h2>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_loss = parsed.get('total_loss', 0)
                st.markdown(f"""
                <div class="metric-display">
                    <div class="big-number">${total_loss:,.0f}</div>
                    <h3 style="margin: 1rem 0 0.5rem 0; font-weight: 600;">Monthly Loss</h3>
                    <p style="opacity: 0.9; margin: 0;">Estimated profit leakage</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                critical_leaks = parsed.get('critical_leaks', 0)
                st.markdown(f"""
                <div class="metric-display">
                    <div class="big-number">{critical_leaks}</div>
                    <h3 style="margin: 1rem 0 0.5rem 0; font-weight: 600;">Critical Leaks</h3>
                    <p style="opacity: 0.9; margin: 0;">Immediate attention needed</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                high_impact = parsed.get('high_impact_leaks', 0)
                st.markdown(f"""
                <div class="metric-display">
                    <div class="big-number">{high_impact}</div>
                    <h3 style="margin: 1rem 0 0.5rem 0; font-weight: 600;">High Impact</h3>
                    <p style="opacity: 0.9; margin: 0;">Major opportunities</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                total_leaks = len(parsed.get('leaks', []))
                st.markdown(f"""
                <div class="metric-display">
                    <div class="big-number">{total_leaks}</div>
                    <h3 style="margin: 1rem 0 0.5rem 0; font-weight: 600;">Total Issues</h3>
                    <p style="opacity: 0.9; margin: 0;">Identified leaks</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Beautiful Detailed Leak Analysis
            if parsed.get('leaks'):
                st.markdown("""
                <h2 style="text-align: center; color: #2c3e50; margin: 3rem 0 2rem 0; font-size: 2.2rem;">
                    🚨 Identified Profit Leaks
                </h2>
                """, unsafe_allow_html=True)
                
                for i, leak in enumerate(parsed['leaks'], 1):
                    impact = leak.get('impact', 'Unknown')
                    urgency = leak.get('urgency', 'Unknown')
                    
                    # Determine card style and icon based on urgency
                    if urgency.lower() == 'critical':
                        card_class = "analysis-card critical-leak"
                        icon = "🚨"
                        urgency_badge = "critical-badge"
                    elif urgency.lower() == 'important':
                        card_class = "analysis-card warning-leak"
                        icon = "⚠️"
                        urgency_badge = "warning-badge"
                    else:
                        card_class = "analysis-card"
                        icon = "💡"
                        urgency_badge = "info-badge"
                    
                    # Impact badge styling
                    if impact.lower() == 'high':
                        impact_badge = "critical-badge"
                    elif impact.lower() == 'medium':
                        impact_badge = "warning-badge"
                    else:
                        impact_badge = "success-badge"
                    
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                            <h3 style="color: #2c3e50; margin: 0; font-size: 1.4rem;">
                                {icon} {leak.get('title', f'Profit Leak #{i}')}
                            </h3>
                            <div>
                                <span class="status-badge {urgency_badge}">{urgency}</span>
                                <span class="status-badge {impact_badge}">{impact} Impact</span>
                            </div>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2.5rem; margin-top: 1.5rem;">
                            <div style="background: rgba(102, 126, 234, 0.05); padding: 1.5rem; border-radius: 15px;">
                                <h4 style="color: #667eea; margin-bottom: 1rem;">📊 Financial Impact</h4>
                                <p style="margin: 0.5rem 0;"><strong>💰 Estimated Loss:</strong> {leak.get('estimated_loss', 'Unknown')}</p>
                                <p style="margin: 0.5rem 0;"><strong>📂 Category:</strong> {leak.get('category', 'Unknown')}</p>
                                <p style="margin: 0.5rem 0;"><strong>⏰ Timeline to Fix:</strong> {leak.get('timeline', 'Unknown')}</p>
                            </div>
                            <div style="background: rgba(39, 174, 96, 0.05); padding: 1.5rem; border-radius: 15px;">
                                <h4 style="color: #27ae60; margin-bottom: 1rem;">🔧 Solution Details</h4>
                                <p style="margin: 0.5rem 0;"><strong>🔍 Root Cause:</strong> {leak.get('root_cause', 'Not specified')}</p>
                                <p style="margin: 0.5rem 0;"><strong>💡 Recommended Solution:</strong> {leak.get('solution', 'Not specified')}</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 💡 Profit Recovery Opportunities")
        
        if 'analysis_results' not in st.session_state:
            st.info("📊 Complete the profit leakage analysis first to see optimization opportunities!")
        else:
            results = st.session_state.analysis_results
            parsed = results['parsed_results']
            
            # Top opportunities
            if parsed.get('opportunities'):
                st.markdown("#### 🎯 Top Profit Recovery Opportunities")
                for i, opportunity in enumerate(parsed['opportunities'], 1):
                    st.markdown(f"""
                    <div class="opportunity-card">
                        <h4>🎯 Opportunity #{i}</h4>
                        <p>{opportunity}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Quick wins
            if parsed.get('quick_wins'):
                st.markdown("#### ⚡ Quick Wins - Immediate Actions")
                for quick_win in parsed['quick_wins']:
                    st.markdown(f"""
                    <div class="success-box">
                        <h4>⚡ Quick Win</h4>
                        <p>{quick_win}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Action plan
            st.markdown("#### 📋 Recommended Action Plan")
            st.markdown("""
            <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.1);">
                <h4>🚀 Implementation Roadmap</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2rem; margin-top: 1rem;">
                    <div style="text-align: center; padding: 1rem; background: #ffe6e6; border-radius: 10px;">
                        <h5>Week 1-2: Critical Fixes</h5>
                        <p>Address urgent profit leaks with immediate impact</p>
                    </div>
                    <div style="text-align: center; padding: 1rem; background: #fff3e0; border-radius: 10px;">
                        <h5>Month 1-2: Major Improvements</h5>
                        <p>Implement high-impact solutions and process changes</p>
                    </div>
                    <div style="text-align: center; padding: 1rem; background: #e8f5e8; border-radius: 10px;">
                        <h5>Month 3+: Optimization</h5>
                        <p>Fine-tune operations and monitor ongoing improvements</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            


            st.markdown("### � Export Results")
            
            
            # Raw analysis (expandable)
            with st.expander("🔍 View Detailed AI Analysis", expanded=False):
                st.text(results['raw_analysis'])
    
    # Beautiful Footer Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Create footer with proper Streamlit components
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 4rem 2rem; border-radius: 25px; text-align: center; margin: 3rem 0; box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);">
        <h1 style="font-size: 2.5rem; margin-bottom: 1.5rem;">💰 Transform Your Business Profitability</h1>
        <p style="font-size: 1.2rem; margin-bottom: 2rem; opacity: 0.9;">Every minute your profits leak away costs you money. Our AI identifies exactly where and how much.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Colorful footer highlights with compact size
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%); color: white; padding: 1.8rem; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(162, 155, 254, 0.3); margin: 1rem 0; height: 220px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="font-size: 2.5rem; margin-bottom: 0.8rem;">🎯</div>
                <h3 style="margin-bottom: 0.8rem; font-weight: 600; font-size: 1.2rem;">Precision Analysis</h3>
            </div>
            <p style="opacity: 0.9; line-height: 1.4; margin: 0; font-size: 0.9rem;">AI identifies specific profit leaks with quantified financial impact</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%); color: white; padding: 1.8rem; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(253, 121, 168, 0.3); margin: 1rem 0; height: 220px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="font-size: 2.5rem; margin-bottom: 0.8rem;">⚡</div>
                <h3 style="margin-bottom: 0.8rem; font-weight: 600; font-size: 1.2rem;">Instant Implementation</h3>
            </div>
            <p style="opacity: 0.9; line-height: 1.4; margin: 0; font-size: 0.9rem;">Get actionable solutions you can implement immediately</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #00b894 0%, #55efc4 100%); color: white; padding: 1.8rem; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(0, 184, 148, 0.3); margin: 1rem 0; height: 220px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="font-size: 2.5rem; margin-bottom: 0.8rem;">📈</div>
                <h3 style="margin-bottom: 0.8rem; font-weight: 600; font-size: 1.2rem;">Measurable ROI</h3>
            </div>
            <p style="opacity: 0.9; line-height: 1.4; margin: 0; font-size: 0.9rem;">Track profit recovery progress and measure real impact</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()