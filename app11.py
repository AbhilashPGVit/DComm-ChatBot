import streamlit as st
import os
import pandas as pd
import base64
import sys
import matplotlib.pyplot as plt
from io import StringIO
from dotenv import load_dotenv
from httpx import Client, Limits
from openai import AzureOpenAI
from typing import TypedDict, Annotated, List
import operator
from langgraph.graph import StateGraph, END
import datetime
import html
import openpyxl
import numpy as np
# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Data Analysis Agent",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
    /* Main background gradient */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');

    h1 {
        font-family: 'Inter', sans-serif;
    }
    .stApp {
        /*background: linear-gradient(135deg, #e6f3ff 0%, #cce7ff 25%, #b3daff 50%, #99ccff 75%, #80bfff 100%) !important;*/
        background: linear-gradient(135deg, #D6FAF3 0%, #F3F7FF 51%, #D4E1FE 100%) !important;
        background-attachment: fixed !important;
    }
    
    /* Top header bar styling */
    header[data-testid="stHeader"] {
        background: linear-gradient(135deg, #D6FAF3 0%, #F3F7FF 51%, #D4E1FE 100%) !important;
        border-bottom: 2px solid #b3daff !important;
    }
    
    /* Bottom block container (chat input area) */
    div[data-testid="stBottomBlockContainer"] {
        background: linear-gradient(135deg, #D6FAF3 0%, #F3F7FF 51%, #D4E1FE 100%) !important;

        border-top: 2px solid #cce7ff !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%) !important;
        border-right: 2px solid #b3daff !important;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        background: rgba(255, 255, 255, 0.8) !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
        margin: 1rem !important;
    }
    
    /* Headers styling */
    h1, h2, h3 {
        color: #1e3a5f !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }
    
/* 1. Base style for ALL chat message wrappers */
.stChatMessage {
    background: transparent !important; /* Keep outer container transparent */
    border: 1px solid #e0e0e0 !important;
    border-radius: 12px !important;
    margin: 0.5rem 0 !important;
}

/* --- USER MESSAGE STYLING --- */
/* Method 1: If you can identify user messages by avatar or other means */
.stChatMessage:has([data-testid="stChatMessageAvatarUser"]) {
    background: #FFFFFF !important; /* Make the entire outer container white */
    border-left: 5px solid #4da6ff !important;
    border: 1px solid #e0e0e0 !important; /* Keep the border */
    /* Dynamic width and right alignment */
    max-width: 70% !important; /* Limit max width to 70% of container */
    width: fit-content !important; /* Dynamic width based on content */
    margin-left: auto !important; /* Push to the right */
    margin-right: 0 !important; /* Align to right edge */
}

.stChatMessage:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
    background-color: transparent !important; /* Inner content transparent since outer is white */
    border-radius: 12px;
    padding: 1rem;
}

/* --- ASSISTANT MESSAGE STYLING --- */
/* Method 1: If you can identify assistant messages by avatar */
.stChatMessage:has([data-testid="stChatMessageAvatarAssistant"]) {
    border-left: 5px solid #66b3ff !important;
}

.stChatMessage:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
    background: transparent !important; /* Keep assistant messages transparent */
}

    
    /* Chat message text color fix */
    .stChatMessage p, .stChatMessage div, .stChatMessage span {
        color: #1e3a5f !important;
    }
    
    /* Chat input styling - revert to original appearance */
    .stChatInput {
        background: transparent !important;
        border: none !important;
    }
    
    div[data-testid="stChatInput"] {
        background: transparent !important;
        border: none !important;
    }
    
    /* Chat input text area - keep original dark styling */
/* Replace your existing chat input CSS section with this updated version */

/* --- CHAT INPUT AREA STYLING (UPDATED) --- */
/* Target the main chat input container */
.stChatInput > div {
    background-color: #FFFFFF !important;
    border-radius: 12px !important;
    border: 1px solid #e0e0e0 !important;
    max-width: 600px !important; /* Limit the width */
    margin: 0 auto !important; /* Center it */
}

/* Target the textarea wrapper */
.stChatInput textarea {
    background-color: #FFFFFF !important;
    color: #333333 !important; /* Dark text for better readability */
    border: none !important;
    border-radius: 12px !important;
}

/* Specifically target the textarea by its data-testid */
[data-testid="stChatInputTextArea"] {
    background-color: #FFFFFF !important;
    color: #333333 !important;
    border: none !important;
    border-left: none !important; /* Explicitly remove left border */
    border-right: none !important;
    border-top: none !important;
    border-bottom: none !important;
    box-shadow: none !important; /* Remove any box shadow */
    outline: none !important; /* Remove outline on focus */
}

/* Target specific emotion cache classes for chat input */
.st-emotion-cache-1c7y2kd {
    background-color: #FFFFFF !important;
    border-radius: 12px !important;
}

/* Additional fallback selectors for chat input */
[data-testid="stChatInput"] {
    background-color: #FFFFFF !important;
}

[data-testid="stChatInput"] > div {
    background-color: #FFFFFF !important;
    border: none !important; /* Remove border completely */
    border-radius: 12px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important; /* Add subtle shadow instead */
}

/* Target the parent container to ensure it has white background */
[data-testid="stChatInput"] {
    background-color: #FFFFFF !important;
    border-radius: 12px !important;
    max-width: 600px !important;
    margin: 0 auto !important;
}

/* Target any intermediate containers */
[data-testid="stChatInput"] > div > div {
    background-color: #FFFFFF !important;
    border-radius: 12px !important;
    border: none !important; /* Remove border from nested containers too */
}




/* Also target the textarea focus state directly */
[data-testid="stChatInputTextArea"]:focus {
    outline: none !important;
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] textarea {
    background-color: #FFFFFF !important;
    color: #333333 !important;
    border: none !important;
}

/* Style placeholder text */
[data-testid="stChatInput"] textarea::placeholder {
    color: #9e9e9e !important;
}

/* Target the chat input button area */
.stChatInput button {
    background-color: #FFFFFF !important;
    border: none !important;
}

/* More specific targeting for newer Streamlit versions */
div[data-testid="stChatInput"] div[data-baseweb="input"] {
    background-color: #FFFFFF !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 12px !important;
}

div[data-testid="stChatInput"] div[data-baseweb="input"] textarea {
    background-color: #FFFFFF !important;
    color: #333333 !important;
}


    /* Buttons styling */
    .stButton > button {
        background: linear-gradient(135deg, #4da6ff 0%, #3399ff 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(77, 166, 255, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #3399ff 0%, #2d8cff 100%) !important;
        box-shadow: 0 4px 12px rgba(77, 166, 255, 0.4) !important;
        transform: translateY(-2px) !important;
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px dashed #b3daff !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    
    /* Expandable sections styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%) !important;
        border: 1px solid #cce7ff !important;
        border-radius: 8px !important;
        color: #1e3a5f !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid #e6f3ff !important;
        border-radius: 0 0 8px 8px !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background: white !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
    }
    

    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #4da6ff 0%, #66b3ff 100%) !important;
    }
    
    /* Info, success, error boxes styling */
    .stAlert {
        border-radius: 8px !important;
        border: none !important;
    }
    
    .stAlert[data-baseweb="notification-info"] {
        background: linear-gradient(135deg, #e6f3ff 0%, #cce7ff 100%) !important;
        border-left: 4px solid #4da6ff !important;
    }
    
    .stAlert[data-baseweb="notification-success"] {
        background: linear-gradient(135deg, #e6ffe6 0%, #ccffcc 100%) !important;
        border-left: 4px solid #4da64d !important;
    }
    
    .stAlert[data-baseweb="notification-error"] {
        background: linear-gradient(135deg, #ffe6e6 0%, #ffcccc 100%) !important;
        border-left: 4px solid #ff4d4d !important;
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #4da6ff !important;
    }
    
    /* Code blocks styling */
    .stCodeBlock {
        background: rgba(248, 249, 250, 0.95) !important;
        border: 1px solid #e6f3ff !important;
        border-radius: 8px !important;
    }
    
    /* Selectbox and multiselect styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid #cce7ff !important;
        border-radius: 8px !important;
    }
    
    /* Metric styling */
    .metric-container {
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid #e6f3ff !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px !important;
    }
    
    ::-webkit-scrollbar-track {
        background: #f0f8ff !important;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #4da6ff 0%, #66b3ff 100%) !important;
        border-radius: 4px !important;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #3399ff 0%, #4da6ff 100%) !important;
    }
    
    /* Text area styling */

    
    /* Container borders and shadows */
    .element-container {
        background: transparent !important;
    }
    
    /* Caption and small text styling */
    .caption {
        color: #4a6fa5 !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid #cce7ff !important;
        border-radius: 8px 8px 0 0 !important;
        color: #1e3a5f !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(240, 248, 255, 0.9) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #e6f3ff 0%, #cce7ff 100%) !important;
        border-bottom: 2px solid #4da6ff !important;
    }
    
    /* Fix text colors in all components */
    p, div, span, label {
        color: #1e3a5f !important;
    }
    
    /* Ensure readability in all text elements */
    .stMarkdown p, .stMarkdown div, .stMarkdown span {
        color: #1e3a5f !important;
    }
            
        /* Sidebar content */

    div[data-testid="stSidebarContent"] {

        background: #ffffff !important;

    }

    

    /* Sidebar user content */

    div[data-testid="stSidebarUserContent"] {

        background: #ffffff !important;

    }

    

    /* Sidebar header */

    div[data-testid="stSidebarHeader"] {

        background: #ffffff !important;

    }

    

    /* Sidebar collapse button */

    div[data-testid="stSidebarCollapseButton"] button {

        color: #1e3a5f !important;

    }

    

    /* Sidebar text color */

    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar p, .stSidebar div, .stSidebar span, .stSidebar label {

        color: #1e3a5f !important;

    }

    

    /* Sidebar file uploader */

    .stSidebar .stFileUploader {

        background: rgba(230, 243, 255, 0.5) !important;

        border: 2px dashed #4da6ff !important;

        border-radius: 12px !important;

    }

    

    .stSidebar .stFileUploader * {

        color: #1e3a5f !important;

    }

    

    /* Sidebar buttons */

    .stSidebar .stButton > button {

        background: linear-gradient(135deg, #4da6ff 0%, #3399ff 100%) !important;

        color: white !important;

        border: none !important;

        border-radius: 8px !important;

        box-shadow: 0 2px 8px rgba(77, 166, 255, 0.3) !important;

    }

    

    /* Sidebar expandable sections */

    .stSidebar .streamlit-expanderHeader {

        background: linear-gradient(135deg, #e6f3ff 0%, #cce7ff 100%) !important;

        border: 1px solid #b3daff !important;

        border-radius: 8px !important;

        color: #1e3a5f !important;

    }

    

    .stSidebar .streamlit-expanderContent {

        background: rgba(255, 255, 255, 0.95) !important;

        border: 1px solid #e6f3ff !important;

        color: #1e3a5f !important;

    }

    

    /* Sidebar expander styling */

    .stSidebar .stExpander details summary {

        background: linear-gradient(135deg, #e6f3ff 0%, #cce7ff 100%) !important;

        color: #1e3a5f !important;

    }

    

    .stSidebar .stExpander div[data-testid="stExpanderDetails"] {

        background: rgba(255, 255, 255, 0.95) !important;

    }

    

    /* Sidebar dataframes */

    .stSidebar .stDataFrame {

        background: white !important;

        border: 1px solid #e6f3ff !important;

        border-radius: 8px !important;

    }

    

    /* Sidebar alerts */

    .stSidebar .stAlert[data-baseweb="notification-info"] {

        background: linear-gradient(135deg, #e6f3ff 0%, #cce7ff 100%) !important;

        border-left: 4px solid #4da6ff !important;

        color: #1e3a5f !important;

    }

    

    .stSidebar .stAlert[data-baseweb="notification-success"] {

        background: linear-gradient(135deg, #e6ffe6 0%, #ccffcc 100%) !important;

        border-left: 4px solid #4da64d !important;

        color: #1e3a5f !important;

    }

    

    /* Sidebar progress bar */

    .stSidebar .stProgress > div > div > div > div {

        background: linear-gradient(90deg, #4da6ff 0%, #66b3ff 100%) !important;

    }

    

    /* Sidebar markdown containers */

    .stSidebar div[data-testid="stMarkdownContainer"] {

        color: #1e3a5f !important;

    }

    

    .stSidebar div[data-testid="stMarkdownContainer"] p,

    .stSidebar div[data-testid="stMarkdownContainer"] strong,

    .stSidebar div[data-testid="stMarkdownContainer"] li {

        color: #1e3a5f !important;

    }
    
    /* Main dropzone container */
    .st-emotion-cache-1gm87a1 {
        background-color: #fafafa;
        border: 2px dashed #e0e0e0;
        color: #333;
        border-radius: 12px;
    }

    /* Instructions container */
    .st-emotion-cache-u8hs99 {
        color: #555;
    }

    /* "Drag and drop file here" text */
    .st-emotion-cache-ysg2um {
        color: #111;
    }

    /* File limit and type text */
    .st-emotion-cache-b1errp {
        color: #666;
    }

    /* SVG upload icon */
    .st-emotion-cache-6rlrad {
        fill: #555;
    }

    /* "Browse files" button */
    .st-emotion-cache-jszdd5 {
        background-color: #f0f2f6;
        color: #333;
        border: 1px solid #dcdcdc;
    }

    /* Button hover effect */
    .st-emotion-cache-jszdd5:hover {
        background-color: #e6e6e6;
        border-color: #c4c4c4;
    }
    .st-emotion-cache-1v6pjqr,
    .st-emotion-cache-1ah0apa {
        border: 1px solid #e6e6e6 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
        padding: 10px !important;
        transition: box-shadow 0.3s ease-in-out !important;
    }

    /* Apply the same hover effect to both classes */
    .st-emotion-cache-1v6pjqr:hover,
    .st-emotion-cache-1ah0apa:hover {
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15) !important;
    }
    .st-emotion-cache-55l0h8 {
        background-color: #DBDBDB !important; /* A very light gray, almost white */
        border: 1px solid #e0e0e0 !important;   /* A subtle light border */
        border-radius: 8px !important;            /* Smoother, rounded corners */
        padding: 1rem !important;                 /* Add some internal spacing */
    }

    /* Target the code element inside to ensure the text color is dark */
    .st-emotion-cache-55l0h8 code {
        color: #333333 !important; /* Dark gray text for high contrast and readability */
        background-color: transparent !important; /* Ensure no conflicting background on the code itself */
    }
    .st-emotion-cache-sy324q, 
    .st-emotion-cache-176n945 {
        background-color: #DBDBDB !important;
    }



</style>
""", unsafe_allow_html=True)
# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'df' not in st.session_state:
    st.session_state.df = None
if 'workflow_steps' not in st.session_state:
    st.session_state.workflow_steps = []
if 'llm_reasoning' not in st.session_state:
    st.session_state.llm_reasoning = []
if 'conversation_context' not in st.session_state:
    st.session_state.conversation_context = []
if 'all_dataframes' not in st.session_state:
    st.session_state.all_dataframes = {}
if 'sheet_info' not in st.session_state:
    st.session_state.sheet_info = {}

# Define AgentState
class AgentState(TypedDict):
    dataframe_str: str
    query: str
    code_string: str
    execution_result: any
    insights: str
    error: bool
    conversation_context: str

# Initialize LLM
@st.cache_resource
def initialize_llm():
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    llm = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=subscription_key,
        api_version="2025-01-01-preview",
        http_client=Client(verify=False, limits=Limits(max_connections=100, max_keepalive_connections=20))
    )
    
    return llm, deployment

def get_conversation_context():
    """Get the conversation context from chat history"""
    if not st.session_state.conversation_context:
        return ""
    
    context = "Previous conversation context:\n"
    for i, ctx in enumerate(st.session_state.conversation_context[-20:]):  # Keep last 3 interactions
        context += f"\nPrevious Query {i+1}: {ctx['query']}\n"
        context += f"Previous Analysis: {ctx['summary']}\n"
    
    return context

# Agent functions (keeping original logic intact)
def get_df_info_multi_sheet() -> str:
    """Returns comprehensive information about all loaded dataframes."""
    if not st.session_state.all_dataframes:
        return "No dataframes loaded."
    
    info_str = "MULTI-SHEET DATASET INFORMATION:\n\n"
    
    for sheet_name, df in st.session_state.all_dataframes.items():
        info_str += f"=== SHEET: {sheet_name} ===\n"
        info_str += f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n"
        info_str += f"Columns: {', '.join(df.columns)}\n"
        
        # Add sample data
        info_str += f"\nSample data from {sheet_name}:\n"
        info_str += df.head(2).to_string() + "\n\n"
        
        # Add column types
        info_str += f"Column types in {sheet_name}:\n"
        for col, dtype in df.dtypes.items():
            info_str += f"  {col}: {dtype}\n"
        info_str += "\n" + "="*50 + "\n\n"
    
    return info_str


# Update the execute_code function to provide access to all dataframes:

def execute_code_multi_sheet(state: AgentState):
    st.session_state.workflow_steps.append("⚙️ Executing generated code...")
    
    code = state['code_string']
    
    # Prepare local variables with all dataframes
    local_vars = {
        "plt": plt, 
        "pd": pd,
        "np": np
    }
    
    # Add all dataframes to local variables
    if st.session_state.all_dataframes:
        # Add individual dataframes by sheet name
        for sheet_name, df in st.session_state.all_dataframes.items():
            # Clean sheet name for variable naming
            clean_name = sheet_name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
            local_vars[f"df_{clean_name}"] = df
        
        # Add a dictionary of all dataframes
        local_vars["dataframes"] = st.session_state.all_dataframes
        
        # For backward compatibility, set main df
        local_vars["df"] = list(st.session_state.all_dataframes.values())[0]
    
    output_stream = StringIO()
    
    # Log code execution reasoning
    st.session_state.llm_reasoning.append({
        "step": "Code Execution",
        "icon": "⚙️",
        "prompt": f"**Executing Code with Multi-Sheet Access:**\n```python\n{code}\n```",
        "reasoning": "Running the generated Python code against all loaded Excel sheets to produce results...",
        "response": "",
        "status": ""
    })
    
    try:
        original_stdout = sys.stdout
        sys.stdout = output_stream
        exec(code, {}, local_vars)
        sys.stdout = original_stdout
        result = output_stream.getvalue()
        
        if os.path.exists('plot.png'):
            with open("plot.png", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            result += f"\nPLOT_BASE64:{encoded_string}"
            os.remove('plot.png')
        
        # Log execution result
        execution_output = result.split("PLOT_BASE64:")[0].strip() if "PLOT_BASE64:" in result else result
        plot_info = "\n**Plot generated and saved**" if "PLOT_BASE64:" in result else ""
        st.session_state.llm_reasoning[-1]["response"] = f"**Execution Output:**\n{execution_output}{plot_info}"
        st.session_state.llm_reasoning[-1]["status"] = "✅ Success"
        
        st.session_state.workflow_steps.append("✅ Code execution completed")
        return {"execution_result": result, "error": False}
    except Exception as e:
        sys.stdout = original_stdout
        st.session_state.llm_reasoning[-1]["response"] = f"**Execution Error:**\n{str(e)}"
        st.session_state.llm_reasoning[-1]["status"] = "❌ Failed"
        st.session_state.workflow_steps.append(f"❌ Code execution failed: {str(e)}")
        return {"execution_result": str(e), "error": True}


# Update the generate_code function to be aware of multiple sheets:

def generate_code_multi_sheet(state: AgentState, llm, deployment):
    """
    Generates Python code to answer the user's query using multiple dataframes.
    """
    st.session_state.workflow_steps.append("🔧 Generating Python code for multi-sheet analysis...")
    
    df_info = state['dataframe_str']
    query = state['query']
    conversation_context = state.get('conversation_context', '')

    # Create sheet access information
    sheet_info = ""
    if st.session_state.all_dataframes:
        sheet_names = list(st.session_state.all_dataframes.keys())
        sheet_info = f"""
Available Dataframes:
- dataframes: Dictionary containing all sheets - dataframes['{sheet_names[0]}'], dataframes['{sheet_names[1]}'], etc.
- df: Main dataframe (first sheet for backward compatibility)
- Individual sheet variables: {', '.join([f"df_{name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')}" for name in sheet_names])}

Sheet Names: {', '.join(sheet_names)}
"""

    system_prompt = f"""
    You are an expert in pandas and matplotlib. Your task is to write Python code to answer a user's question about multiple dataframes from different Excel sheets.

    {sheet_info}

    Instructions:
    1. Generate Python code to perform the required analysis across multiple sheets.
    2. Import necessary libraries such as pandas and matplotlib and numpy if needed.
    3. You have access to multiple dataframes:
       - Use `dataframes['SheetName']` to access specific sheets
       - Use individual sheet variables like `df_Sheet1`, `df_Sheet2`, etc.
       - Use `df` for the main/first sheet (backward compatibility)
    4. If the user asks for analysis across all sheets, iterate through `dataframes.items()`
    5. If the user asks for a plot, use matplotlib or seaborn to generate it.
       - **IMPORTANT:** After creating a plot, you MUST save it to a file named 'plot.png'.
       - Also, ensure you call `plt.show()` to display the plot.
    6. Use `print()` statements to output any textual results or dataframes.
    7. **IMPORTANT:** When printing numerical results, use formatting to avoid scientific notation.
    8. **IMPORTANT:** If the sales (Shipped Revenue) is on Y-Axis please show the numbers with a M (for million) or K (for thousand) suffix for better readability. For example, 2500000 should be printed as 2.5M and 45000 should be printed as 45K.
    9. Return ONLY the Python code, enclosed in ```python...```. Do not add explanations.

    **Multi-Sheet Examples:**
    Example 1 - Top SKUs contributing to revenue dip:
    Query: "Out of the category seeing the maximum drop in absolute sales (or for a specific week if provided), which are the top SKUs contributing to this dip and what is their contribution %?"
    Good Code:
        ```python
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt    
        # Take the first uploaded dataframe
        keys = list(dataframes.keys())
        df = dataframes[keys[0]].copy()

        # Ensure datetime and week
        df['date'] = pd.to_datetime(df['date'])
        df['week'] = df['date'].dt.isocalendar().week

        # --- Step 1: Category-level weekly revenue ---
        cat_week = df.groupby(['week','category'])['revenue'].sum().reset_index()
        cat_week['WoW_abs_change'] = cat_week.groupby('category')['revenue'].diff()

        # --- Step 2: Focus on the latest week ---
        last_week = cat_week['week'].max()
        week_data = cat_week[cat_week['week'] == last_week]

        # Category with max dip
        target_row = week_data.loc[week_data['WoW_abs_change'].idxmin()]
        target_cat = target_row['category']
        target_week = target_row['week']

        # --- Step 3: SKU-level revenue for that category ---
        sku_week = (
            df[df['category'] == target_cat]
            .groupby(['week','asin','product'])['revenue']
            .sum()
            .reset_index()
        )

        # Compute WoW change per SKU (treat missing prev week as 0)
        sku_week['WoW_change'] = (
            sku_week.groupby('asin')['revenue'].diff()
            .fillna(-sku_week['revenue'])
        )

        # --- Step 4: Filter SKUs that dipped in target week ---
        target_skus = sku_week[sku_week['week'] == target_week].copy()
        target_skus = target_skus[target_skus['WoW_change'] < 0]

        # Contribution % relative to category dip
        category_total_dip = abs(target_row['WoW_abs_change'])
        target_skus['Contribution_%'] = (
            abs(target_skus['WoW_change']) / category_total_dip * 100
        )

        # --- Step 5: Rank and select top 5 ---
        result = target_skus.sort_values('WoW_change').head(5)[
            ['asin','product','WoW_change','Contribution_%']
        ]
        ```

    
    Example 4 - Combine data from all sheets:
    ```python
    # Combine all sheets into one dataframe
    combined_df = pd.concat([df.assign(Sheet=sheet_name) for sheet_name, df in dataframes.items()], ignore_index=True)
    print(f"Combined dataset shape: {{combined_df.shape}}")
    print(combined_df.groupby('Sheet').size())
    ```

    Example 5 - Compare metrics across sheets:
    ```python
    # Compare revenue across different sheets
    for sheet_name, df in dataframes.items():
        if 'ShippedRevenue' in df.columns:
            total_revenue = df['ShippedRevenue'].sum()
            print(f"{sheet_name}: ${{total_revenue:,.2f}}")
    ```

    Example 6 - Analyze specific sheet:
    ```python
    # If user asks about a specific sheet
    sheet_of_interest = 'Sheet1'  # Or parse from user query
    if sheet_of_interest in dataframes:
        df_target = dataframes[sheet_of_interest]
        print(f"Analysis for {{sheet_of_interest}}:")
        print(df_target.describe())
    ```


    {conversation_context}
    """

    user_prompt = f"""
    Here is information about all the dataframes you are working with:
    {df_info}

    User's query: "{query}"
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        # Log the LLM reasoning for code generation
        st.session_state.llm_reasoning.append({
            "step": "Code Generation",
            "icon": "🔧",
            "prompt": f"**System Prompt:**\n{system_prompt}\n\n**User Query:**\n{user_prompt}",
            "reasoning": "Analyzing the user's query and multi-sheet dataset structure to generate appropriate Python code..."
        })
        
        completion = llm.chat.completions.create(
            model=deployment,
            messages=messages,
            max_tokens=2000,  # Increased for multi-sheet code
            temperature=0.0,
        )

        code = completion.choices[0].message.content.strip()
        if code.startswith("```python"):
            code = code[9:]
        if code.endswith("```"):
            code = code[:-3]

        # Log LLM response
        st.session_state.llm_reasoning[-1]["response"] = f"**Generated Code:**\n```python\n{code}\n```"
        st.session_state.llm_reasoning[-1]["status"] = "✅ Success"
        
        st.session_state.workflow_steps.append("✅ Multi-sheet code generation completed")
        return {"code_string": code, "error": False}
    except Exception as e:
        st.session_state.llm_reasoning[-1]["response"] = f"**Error:**\n{str(e)}"
        st.session_state.llm_reasoning[-1]["status"] = "❌ Failed"
        st.session_state.workflow_steps.append(f"❌ Code generation failed: {str(e)}")
        return {"code_string": "", "execution_result": str(e), "error": True}

def generate_insights(state: AgentState, llm, deployment):
    """
    Analyzes all available data to provide actionable insights with direct dataframe access.
    """
    st.session_state.workflow_steps.append("💡 Generating insights and analysis...")
    
    query, code, result = state['query'], state['code_string'], state['execution_result']
    conversation_context = state.get('conversation_context', '')
    dataframe_str = state.get('dataframe_str', '')

    result_text = result.split("PLOT_BASE64:")[0].strip()
    plot_exists = "A plot was also generated to visualize this data." if "PLOT_BASE64:" in result else ""

    # Get actual dataframe statistics and key information for context
    df_context = ""
    if st.session_state.df is not None:
        df = st.session_state.df
        
        # Generate comprehensive dataframe context
        df_context = f"""
**COMPLETE DATASET CONTEXT:**

Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns

Available Columns: {', '.join(df.columns)}

Key Statistics:
"""
        
        # Add statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            stats_summary = df[numeric_cols].describe()
            df_context += f"\nNumeric Column Statistics:\n{stats_summary.to_string()}\n"
        
        # Add categorical column info
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            df_context += "\nCategorical Columns Unique Values:\n"
            for col in categorical_cols[:10]:  # Limit to first 10 to avoid huge prompts
                unique_count = df[col].nunique()
                sample_values = df[col].unique()[:5] if unique_count <= 5 else df[col].unique()[:3]
                df_context += f"- {col}: {unique_count} unique values (sample: {', '.join(map(str, sample_values))}{'...' if unique_count > 5 else ''})\n"
        
        # Add date range if Date column exists
        date_cols = [col for col in df.columns if 'date' in col.lower() or 'Date' in col]
        if date_cols:
            for date_col in date_cols[:2]:  # Limit to first 2 date columns
                try:
                    if pd.api.types.is_datetime64_any_dtype(df[date_col]):
                        df_context += f"\n{date_col} Range: {df[date_col].min()} to {df[date_col].max()}\n"
                    else:
                        # Try to convert and get range
                        temp_date = pd.to_datetime(df[date_col], errors='coerce')
                        if not temp_date.isna().all():
                            df_context += f"\n{date_col} Range: {temp_date.min()} to {temp_date.max()}\n"
                except:
                    pass
        
        # Add sample data rows (first 3 rows)
        df_context += f"\nSample Data (First 3 rows):\n{df.head(3).to_string()}\n"

    analyst_prompt = f"""You are an expert e-commerce and retail data analyst. Your task is to provide data-driven insights based on retail performance metrics, focusing strictly on the available data.

{conversation_context}

{df_context}

**CRITICAL: You have complete access to the dataset shown above. Use this data to provide specific, calculated insights.**

**Analysis Framework - Priority Order:**
1. **Primary Factors (Data-Driven):** Always analyze these metrics first when explaining performance changes:
   - Conversion rate changes (views to sales efficiency)
   - GlanceView trends (traffic/visibility) 
   - ASP changes (pricing impact)
   - ShippedUnits vs ShippedRevenue relationship
   
2. **Secondary Factors:** Category, Brand, Retailer, Country, ASIN, Product performance

3. **External Factors (Only if data patterns suggest):** Market conditions, seasonality, competition

**Few-Shot Examples with Specific Data:**

Example 1 - SKU Performance Analysis:
Query: "Which SKU contributed most to the revenue decline in Category A?"
Good Response: "SKU0051 was the biggest contributor to Category A's revenue decline, with ShippedRevenue dropping by $15,847 (23.4% decline). The root causes were:
- Conversion rate fell from 4.2% to 2.8% (-33% decline)  
- GlanceView dropped from 12,450 to 9,200 (-26% decline)
- ASP remained stable at $6.23, so pricing wasn't the issue
This SKU needs immediate attention on both traffic generation and conversion optimization."

Example 2 - Category Comparison:
Query: "Compare performance between Category A and Category B last week"
Good Response: "Category A outperformed Category B significantly:
- Category A: $245K ShippedRevenue (3.2% Conversion rate, 156K GlanceView, $7.85 ASP)
- Category B: $180K ShippedRevenue (2.1% Conversion rate, 142K GlanceView, $6.15 ASP)
Category A's superior performance stems from a 52% higher conversion rate, indicating better product-market fit or content quality."

Example 3 - Traffic Drop Analysis:
Query: "SKU0051 is showing a dip in Glance Views. Why is this happening?"
Good Response: "The dip in Glance Views may be linked to digital shelf gaps (e.g., fewer images, shorter titles, insufficient bullets). These deficiencies reduce visibility in search results and customer engagement, driving down views@
**Your Analysis Task:**
**IMPORTANT:** Use the complete dataset context provided above. When analyzing specific SKUs, categories, or brands mentioned in the query, reference their actual performance metrics from the data.

You have been given:
1. **The Original User Query:** "{query}"
2. **The Python Code Used for Analysis:** 
```python
{code}
```
3. **The Analysis Results:**
{result_text}
{plot_exists}
4. **Complete Dataset Access:** Use the dataset statistics and sample data provided above for additional context

**Response Structure:**
**Summary:**
- Lead with the key finding using EXACT numbers from the results
- Reference specific SKUs, categories, or products by name when mentioned in the query
- Based on the query, decide which insights to prioritize:

        1. If the query is descriptive or generic just give generic insights

        2. If the query is sales or revnue related then go ahead with the following insights:
            **Key Insights (Use Actual Data Values):**
            - Insight 1: Conversion rate analysis with specific percentages and SKU/category names
            - Insight 2: GlanceView trends with actual view counts and affected products  
            - Insight 3: ASP analysis with precise dollar amounts and product details
            - Insight 4: ShippedRevenue/ShippedUnits relationship with real figures

        3. If the query is traffic or GlanceView related then go ahead with the following insights:
            **Key Insights (Use Actual Data Values):**
            - Insight 1: Bullet Count analysis
            - Insight 2: Title word count analysis 
            - Insight 3: Image count analysis
            - Insight 4: Word count analysis

**Root Cause Analysis:**
- Not needed for generic/descriptive queries
- Show it when asked for reasons for traffic decline or sales drop
- Identify which specific products/categories are driving the trends
- Use actual metric values to explain performance changes

**Actionable Recommendations:**
- Not needed for generic/descriptive queries
- Provide specific recommendations for the actual SKUs/categories identified
- Reference real performance gaps found in the data

**Critical Rules:**
- **IMPORTANT:** If the user has sent just a greeting just reply with a Hi back. No need to do any analysis.
- Do not show Root Cause Analysis and Actionable Recommendations until explicitly mentioned in the Query
- Use EXACT product names, SKUs, categories, and metric values from the analysis results
- When the query mentions specific entities (SKUs, categories, brands), analyze their actual performance using the dataset
- Reference real conversion rates, GlanceView counts, ASP values, and revenue figures
- Don't use hypothetical examples - use the actual data provided
- If analyzing trends, compare actual before/after values from the results

**Format your response with markdown formatting to avoid display issues.**"""
    
    # Log insights generation reasoning
    st.session_state.llm_reasoning.append({
        "step": "Insights Generation",
        "icon": "💡",
        "prompt": f"**Analysis Synthesis Prompt (with full dataset context):**\n{analyst_prompt}",
        "reasoning": "Synthesizing data analysis results with complete dataset access to generate specific, data-driven business insights...",
        "response": "",
        "status": ""
    })
    
    messages = [
        {"role": "system", "content": "You are an expert e-commerce data analyst with complete access to the dataset. Provide specific insights using actual data values, product names, and performance metrics from the analysis results. Focus on real numbers and identified entities, not hypothetical examples."}, 
        {"role": "user", "content": analyst_prompt}
    ]
    
    completion = llm.chat.completions.create(model=deployment, messages=messages, max_tokens=15000, temperature=0.3)  # Lower temperature for more precise analysis
    
    insights = completion.choices[0].message.content
    
    # Log insights response
    st.session_state.llm_reasoning[-1]["response"] = f"**Generated Insights:**\n{insights}"
    st.session_state.llm_reasoning[-1]["status"] = "✅ Specific insights generated using actual data"
    
    st.session_state.workflow_steps.append("✅ Insights generation completed")
    return {"insights": insights}

def get_df_info(dataframe: pd.DataFrame) -> str:
    """Returns a string with the head and info of the dataframe."""
    buffer = StringIO()
    dataframe.info(buf=buffer)
    info_str = buffer.getvalue()
    return f"Dataframe Head:\n{dataframe.head().to_markdown()}\n\nDataframe Info:\n{info_str}"

def add_to_conversation_context(query, insights, result):
    """Add the current interaction to conversation context"""
    # Create a summary of the current interaction
    summary = f"Analysis: {insights[:2000]}..."  # Keep first 200 chars
    
    st.session_state.conversation_context.append({
        'query': query,
        'summary': summary,
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Keep only last 5 interactions to manage context size
    if len(st.session_state.conversation_context) > 5:
        st.session_state.conversation_context = st.session_state.conversation_context[-40:]

# Streamlit UI


# 2. Your centered title with the new font applied
# Combine both headers into a single st.markdown call
st.markdown(
    """
    <h1 style="
        color: #022A3E;
        text-align: center;
        font-family: 'Inter', sans-serif;
        font-size: 24px;
        font-style: normal;
        font-weight: 600;
        line-height: 32px;
        letter-spacing: -0.48px;
        margin-bottom: -6px; /* Adjust this value to control the space */
    ">
    🤖 Digital Commerce AI Assistant
    </h1>

    <h3 style="
        color: #5D5D5D;
        text-align: center;
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        font-style: normal;
        font-weight: 500;
        line-height: 24px;
        letter-spacing: -0.32px;
        margin-top: 0px; /* Set top margin to 0 or a small value */
    ">
    Upload your data and chat with your dataset to get AI-powered insights!
    </h3>
    """,
    unsafe_allow_html=True
)


# Sidebar
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>Dataset Info</h2>", unsafe_allow_html=True)
    st.header("📁 Upload Dataset")
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file", 
        type=["csv", "xlsx", "xls"],
        help="Upload CSV files or Excel files with multiple sheets"
    )
    
    if uploaded_file is not None:
        try:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'csv':
                # Handle CSV files
                df = pd.read_csv(uploaded_file)
                st.session_state.df = df
                st.session_state.all_dataframes = {'main': df}  # Store as single sheet
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
                st.success(f"CSV loaded! Shape: {df.shape}")
                
                with st.expander("Preview Data"):
                    st.dataframe(df.head())
            
            elif file_extension in ['xlsx', 'xls']:
                # Handle Excel files - Load ALL sheets
                excel_file = pd.ExcelFile(uploaded_file)
                sheet_names = excel_file.sheet_names
                
                st.info(f"Loading all {len(sheet_names)} sheets: {', '.join(sheet_names)}")
                
                # Load all sheets into session state
                all_sheets = {}
                sheet_info = {}
                total_rows = 0
                
                progress_bar = st.progress(0)
                for i, sheet_name in enumerate(sheet_names):
                    try:
                        df_sheet = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                        
                        # Handle Date columns
                        if 'Date' in df_sheet.columns:
                            df_sheet['Date'] = pd.to_datetime(df_sheet['Date'], dayfirst=True, errors='coerce')
                        
                        # Store sheet data
                        all_sheets[sheet_name] = df_sheet
                        sheet_info[sheet_name] = {
                            'rows': df_sheet.shape[0],
                            'columns': df_sheet.shape[1],
                            'column_names': list(df_sheet.columns)
                        }
                        total_rows += df_sheet.shape[0]
                        
                        progress_bar.progress((i + 1) / len(sheet_names))
                        
                    except Exception as e:
                        st.error(f"Error loading sheet '{sheet_name}': {str(e)}")
                
                # Store in session state
                st.session_state.all_dataframes = all_sheets
                st.session_state.sheet_info = sheet_info
                
                # For backward compatibility, set the first sheet as main df
                if all_sheets:
                    st.session_state.df = list(all_sheets.values())[0]
                
                st.success(f"✅ All sheets loaded! Total: {total_rows:,} rows across {len(all_sheets)} sheets")
                
                # Show summary of all sheets
                with st.expander("📊 All Sheets Summary"):
                    for sheet_name, info in sheet_info.items():
                        st.write(f"**{sheet_name}:**")
                        st.write(f"  - {info['rows']:,} rows × {info['columns']} columns")
                        st.write(f"  - Columns: {', '.join(info['column_names'][:5])}{'...' if len(info['column_names']) > 5 else ''}")
                        st.write("")
                
                # Show preview of each sheet
                with st.expander("👀 Preview All Sheets"):
                    for sheet_name, df_sheet in all_sheets.items():
                        st.subheader(f"Sheet: {sheet_name}")
                        st.dataframe(df_sheet.head(3))
                        st.write("---")
                
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            st.info("Please ensure your file is a valid CSV or Excel file.")
    
    st.header("⚙️ Chat Controls")
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state.chat_history = []
        st.session_state.conversation_context = []
        st.rerun()
    
    st.header("📊 Dataset Info")
    if st.session_state.all_dataframes:
        total_sheets = len(st.session_state.all_dataframes)
        total_rows = sum(df.shape[0] for df in st.session_state.all_dataframes.values())
        
        st.write(f"**Total Sheets:** {total_sheets}")
        st.write(f"**Total Rows:** {total_rows:,}")
        
        # Show each sheet info
        for sheet_name, df in st.session_state.all_dataframes.items():
            st.write(f"**{sheet_name}:** {df.shape[0]:,} rows × {df.shape[1]} cols")


# Main content
if st.session_state.df is not None:
    # Initialize LLM
    try:
        llm, deployment = initialize_llm()
        
        
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            if st.session_state.chat_history:
                for i, chat in enumerate(st.session_state.chat_history):
                    # User message
                    with st.chat_message("user"):
                        st.write(f"**Query {i+1}:** {chat['query']}")
                        st.caption(f"Time: {chat['timestamp']}")
                    
                    # Assistant response
                    with st.chat_message("assistant"):
                        if 'insights' in chat:
                            raw_insights = chat["insights"]

                            #    These are characters that should be displayed literally and not as Markdown formatting.
                            chars_to_escape = ['$', '%', '_', '{', '}'] # Add any other characters here

                            # 3. Loop through the characters and apply the .replace() method for each
                            safe_insights = raw_insights
                            for char in chars_to_escape:
                                safe_insights = safe_insights.replace(char, f'\\{char}')

                            # 4. Render the final, safe text
                            st.markdown(safe_insights)
                                                                               
                        # Show plot if exists
                        if 'plot' in chat:
                            st.image(base64.b64decode(chat['plot']))
                        
                        # Expandable sections for code and reasoning
                        if 'code' in chat:
                            with st.expander("View Generated Code"):
                                st.code(chat['code'], language='python')
                        
                        # if 'raw_result' in chat and chat['raw_result'].strip():
                        #     with st.expander("View Raw Results"):
                        #         st.markdown(chat['raw_result'])
                        
                        if 'reasoning' in chat:
                            with st.expander("View LLM Reasoning"):
                                for i, reasoning in enumerate(chat['reasoning']):
                                    with st.expander(f"{reasoning['icon']} {reasoning['step']} - {reasoning['status']}", expanded=False):
                                        st.markdown(f"**🎯 Objective:** {reasoning['reasoning']}")
                                        
                                        col1, col2 = st.columns([1, 1])
                                        
                                        with col1:
                                            st.markdown("**📝 Input/Prompt:**")
                                            st.text_area("", reasoning['prompt'], height=150, key=f"chat_{chat['timestamp'].replace(' ', '').replace(':', '').replace('-', '')}_{i}_prompt", disabled=True)
                                        
                                        with col2:
                                            st.markdown("**🤖 LLM Response:**")
                                            st.text_area("", reasoning['response'], height=150, key=f"chat_{chat['timestamp'].replace(' ', '').replace(':', '').replace('-', '')}_{i}_response", disabled=True)
                                        
                                        st.markdown(f"**Status:** {reasoning['status']}")
            else:
                st.info("Start chatting with your data! Ask questions about patterns, statistics, or request visualizations.")
        
        # Chat Input
        st.subheader("Ask a Question")
        query = st.chat_input("Type your question here...")
        
        if query:
            # Add user message to chat history immediately
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Reset workflow steps and reasoning for new query
            st.session_state.workflow_steps = []
            st.session_state.llm_reasoning = []
            
            # Show progress
            with st.spinner("Analyzing your query across all sheets..."):
                # Create workflow
                workflow = StateGraph(AgentState)
                
                # Add nodes with partial functions for multi-sheet processing
                workflow.add_node("generate_code", lambda state: generate_code_multi_sheet(state, llm, deployment))
                workflow.add_node("execute_code", lambda state: execute_code_multi_sheet(state))
                workflow.add_node("generate_insights", lambda state: generate_insights(state, llm, deployment))
                
                # Define the flow
                workflow.set_entry_point("generate_code")
                workflow.add_edge("generate_code", "execute_code")
                workflow.add_edge("execute_code", "generate_insights")
                workflow.add_edge("generate_insights", END)
                
                # Compile and run
                app = workflow.compile()
                
                df_info_str = get_df_info_multi_sheet()
                conversation_context = get_conversation_context()
                inputs = {
                    "query": query, 
                    "dataframe_str": df_info_str,
                    "conversation_context": conversation_context
                }
                
                try:
                    final_state = app.invoke(inputs)
                    
                    # Process results
                    chat_entry = {
                        'query': query,
                        'timestamp': timestamp,
                        'code': final_state['code_string'],
                        'reasoning': st.session_state.llm_reasoning.copy()
                    }
                    
                    if final_state['error']:
                        chat_entry['insights'] = f"❌ An error occurred during execution: {final_state['execution_result']}"
                        chat_entry['raw_result'] = final_state['execution_result']
                    else:
                        chat_entry['insights'] = final_state['insights']
                        
                        result_text = final_state['execution_result']
                        if "PLOT_BASE64:" in result_text:
                            parts = result_text.split("PLOT_BASE64:")
                            chat_entry['raw_result'] = parts[0].strip()
                            chat_entry['plot'] = parts[1]
                        else:
                            chat_entry['raw_result'] = result_text.strip()
                        
                        # Add to conversation context
                        add_to_conversation_context(query, final_state['insights'], result_text)
                    
                    # Add to chat history
                    st.session_state.chat_history.append(chat_entry)
                    
                    # Rerun to show the new message
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
                    # Still add error to chat history
                    error_entry = {
                        'query': query,
                        'timestamp': timestamp,
                        'insights': f"❌ An error occurred: {str(e)}",
                        'reasoning': st.session_state.llm_reasoning.copy()
                    }
                    st.session_state.chat_history.append(error_entry)
                    st.rerun()
                
    except Exception as e:
        st.error(f"Error initializing LLM: {str(e)}")
        st.info("Please check your environment variables and API keys.")

else:
    st.info("👆 Please upload a CSV file in the sidebar to get started!")
    
    # Show sample data format
    with st.expander("📋 Sample Data Format"):
        sample_data = pd.DataFrame({
            'Column1': [1, 2, 3, 4, 5],
            'Column2': ['A', 'B', 'C', 'D', 'E'],
            'Column3': [10.5, 20.3, 15.7, 8.9, 12.1]
        })
        st.dataframe(sample_data)
        st.info("Your CSV should have column headers in the first row.")