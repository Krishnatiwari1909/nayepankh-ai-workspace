import streamlit as st
import google.generativeai as genai
import sqlite3
from datetime import datetime

st.set_page_config(
    page_title="NayePankh Sahayak",
    page_icon="🕊️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR A TIGHTER UI ---
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.5rem; }
    
    /* 1. Makes recent chat buttons inside the expander look like flat, compact links */
    div[data-testid="stExpanderDetails"] button[kind="secondary"] {
        border: none;
        background-color: transparent;
        text-align: left;
        justify-content: flex-start;
        padding: 0px 5px;
        min-height: 25px; /* Brings them much closer together */
        margin-bottom: -10px; 
    }
    div[data-testid="stExpanderDetails"] button[kind="secondary"]:hover {
        color: #2D7CBE;
        background-color: transparent;
    }
    
    /* 2. Tightens the gap between form elements */
    [data-testid="stForm"] {
        padding: 10px 15px; 
    }
    </style>
""", unsafe_allow_html=True)

# --- DB SETUP ---
conn = sqlite3.connect('impact.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS activities (date TEXT, volunteer_name TEXT, activity_type TEXT, people_impacted INTEGER, notes TEXT)''')
conn.commit()

# --- MULTI-SESSION MEMORY INIT ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"New Chat": [{"role": "assistant", "content": "Namaste! I am your **NayePankh Sahayak**. Need a Hinglish campaign blueprint, lesson ideas for the kids, or social media copies? Ask away!"}]}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New Chat"

# --- TIGHTER SIDEBAR ---
with st.sidebar:
    # 1. New Chat Button
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        chat_id = f"New Chat {len(st.session_state.all_chats) + 1}"
        st.session_state.all_chats[chat_id] = [{"role": "assistant", "content": "Namaste! How can I help you today?"}]
        st.session_state.current_chat = chat_id
        st.rerun()
        
    # 2. Recent Chats (Now a clickable Expander Button!)
    with st.expander("🕒 Recent Chats", expanded=True):
        for chat_name in reversed(list(st.session_state.all_chats.keys())):
            # Shows only the first 22 characters of the name so it fits cleanly
            if st.button(f"💬 {chat_name[:22]}", key=f"btn_{chat_name}", use_container_width=True):
                st.session_state.current_chat = chat_name
                st.rerun()
    
    # Custom tight divider to save space
    st.markdown("<hr style='margin: 10px 0; border-top: 1px solid rgba(49, 51, 63, 0.2);'>", unsafe_allow_html=True)
    
    # 3. Volunteer Impact Form (Logo and text side-by-side)
    # 3. Volunteer Impact Form 
    st.markdown("<h4 style='margin-top: 5px; margin-bottom: 10px;'>📝 Log Impact</h4>", unsafe_allow_html=True)
        
    with st.form("impact_form", clear_on_submit=True):
        name = st.text_input("Volunteer Full Name")
        activity = st.selectbox("Primary Activity", ["Teaching/Education", "Awareness Campaign", "Food Distribution", "Other"])
        impact_number = st.number_input("People Benefited", min_value=1, step=1, value=1)
        notes = st.text_input("Field Notes (Short)") # Changed to text_input to save vertical space
        
        submitted = st.form_submit_button("🚀 Commit to Database", use_container_width=True)
        if submitted and name.strip() != "":
            c.execute("INSERT INTO activities VALUES (?, ?, ?, ?, ?)", (datetime.now().strftime("%Y-%m-%d"), name, activity, impact_number, notes))
            conn.commit()
            st.success("✨ Contribution recorded!")

# --- MAIN INTERFACE HERO ---
header_col1, header_col2 = st.columns([1, 15])
with header_col1:
    st.image("logo.png", width=65) 
with header_col2:
    st.markdown("<div class='main-header'>NayePankh Sahayak Workspace</div>", unsafe_allow_html=True)

# --- API CONFIG ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    system_prompt = """
    You are 'NayePankh Sahayak', an enthusiastic and helpful AI assistant for the NayePankh Foundation, an Indian NGO focused on education, youth empowerment, and social awareness. 
    Your tone is encouraging, professional, and highly actionable. 
    By default, generate social campaigns and posts in 'Hinglish'. HOWEVER, you are fully multilingual. If requested in Kannada, Hindi, Marathi, etc., you MUST fluently generate content in that language.
    """
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)
except Exception as e:
    st.error("Configuration Key Missing.")
    st.stop()

# --- CHAT RENDERING ---
chat_container = st.container(height=550, border=False)

with chat_container:
    for message in st.session_state.all_chats[st.session_state.current_chat]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- CHAT INPUT ---
if prompt := st.chat_input("Type a prompt (e.g., 'Draft a Hinglish Instagram reel script')..."):
    
    if st.session_state.current_chat.startswith("New Chat"):
        new_title = prompt[:20] + "..." 
        st.session_state.all_chats[new_title] = st.session_state.all_chats.pop(st.session_state.current_chat)
        st.session_state.current_chat = new_title
        
    st.session_state.all_chats[st.session_state.current_chat].append({"role": "user", "content": prompt})
    
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    with chat_container:
        with st.chat_message("assistant"):
            with st.spinner("Compiling insights..."):
                try:
                    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.all_chats[st.session_state.current_chat]])
                    response = model.generate_content(history_text)
                    st.markdown(response.text)
                    st.session_state.all_chats[st.session_state.current_chat].append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Execution Error: {e}")
    
    st.rerun()