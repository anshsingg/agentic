import streamlit as st
from openai import OpenAI

# Page Config
st.set_page_config(page_title="AI Mock Interviewer", page_icon="👨‍💻")

st.title("🤖 Agentic Mock Interviewer")
st.caption("I am an AI agent designed to simulate a technical interview. Select your topic and let's begin.")

# 1. Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("OpenAI API Key", type="sk-...uV0A")
    
    st.divider()
    
    # Interview Settings
    role = st.selectbox("Role to Apply For", ["Software Engineer", "Data Scientist", "Product Manager", "Marketing Specialist"])
    topic = st.selectbox("Interview Topic", ["Python", "System Design", "Behavioral", "SQL", "Machine Learning"])
    difficulty = st.select_slider("Difficulty Level", options=["Junior", "Mid-Level", "Senior", "Expert"])
    
    if api_key:
        client = OpenAI(api_key=api_key)
    else:
        st.warning("Please enter your OpenAI API Key to start.")

# 2. Initialize Session State (Memory)
if "messages" not in st.session_state:
    st.session_state.messages = []

if "interview_active" not in st.session_state:
    st.session_state.interview_active = False

# 3. Start Interview Button
if st.button("Start / Restart Interview"):
    st.session_state.interview_active = True
    st.session_state.messages = []
    
    # The System Prompt (The Brain's Instructions)
    system_prompt = f"""
    You are a strict but fair technical interviewer for a {difficulty} {role} position. 
    Your topic is {topic}.
    
    RULES:
    1. Ask only ONE question at a time.
    2. Do not reveal the answer immediately. Wait for the candidate's response.
    3. If the candidate answers incorrectly, gently correct them and ask a follow-up.
    4. Keep your responses concise (under 100 words) to keep the flow moving.
    5. Start by welcoming the candidate and asking the first technical question.
    """
    
    st.session_state.messages.append({"role": "system", "content": system_prompt})
    
    # Generate first question
    if api_key:
        try:
            initial_response = client.chat.completions.create(
                model="gpt-4o-mini", # Cost-effective model
                messages=st.session_state.messages
            )
            first_q = initial_response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": first_q})
        except Exception as e:
            st.error(f"Error: {e}")

# 4. Display Chat History
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 5. User Input & Main Loop
if prompt := st.chat_input("Type your answer here..."):
    if not st.session_state.interview_active:
        st.warning("Please click 'Start Interview' first!")
    elif not api_key:
        st.warning("Please enter an API Key.")
    else:
        # Add User message to state
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI Response
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                stream=True,
            )
            response = st.write_stream(stream)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# 6. Feedback Mechanism (The "Agentic" Review)
if st.session_state.interview_active and len(st.session_state.messages) > 3:
    st.divider()
    if st.button("End Interview & Get Feedback"):
        with st.spinner("Analyzing your performance..."):
            # Create a separate "Feedback Agent" call
            feedback_prompt = "Review the conversation above. Provide specific feedback on the candidate's strengths, weaknesses, and a final Hire/No Hire recommendation."
            
            feedback_messages = st.session_state.messages.copy()
            feedback_messages.append({"role": "system", "content": feedback_prompt})
            
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=feedback_messages
            )
            
            st.success("Interview Complete!")
            st.markdown("### 📝 Interview Feedback")
            st.markdown(completion.choices[0].message.content)
            st.session_state.interview_active = False
