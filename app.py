import streamlit as st
from groq import Groq

# 1. Page Setup
st.set_page_config(page_title="Agentic Mock Interviewer", layout="centered")
st.title("🤖 Agentic Mock Interviewer (Free Version)")

# 2. API Setup (Groq)
# You can paste the key here temporarily, or use the sidebar
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    api_key = st.text_input("Enter Groq API Key (Free)", type="password")
    if api_key:
        client = Groq(api_key=api_key)
    else:
        st.warning("Get a free key at https://console.groq.com/keys")
        st.stop()

# 3. Input: Role
st.markdown("### Step 1: Enter the role you're preparing for")
job_role = st.text_input("Enter Role", placeholder="e.g., Data Scientist at Google")

# 4. Generate Question
st.markdown("### Step 2: Get a Question")

if st.button("Generate Interview Question"):
    if not job_role:
        st.error("Please enter a job role first.")
    else:
        with st.spinner("Thinking up a tough question..."):
            prompt = f"You're an expert interviewer. Ask a challenging and relevant interview question for the role: {job_role}."
            
            try:
                response = client.chat.completions.create(
                    model="llama3-8b-8192",  # Free Llama 3 model
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                question = response.choices[0].message.content
                st.session_state["question"] = question
            except Exception as e:
                st.error(f"Error: {e}")

# Display the question if it exists in memory
if "question" in st.session_state:
    st.info(f"**Interview Question:**\n\n{st.session_state['question']}")

    # 5. User Answer
    st.markdown("### Step 3: Write your answer below")
    user_answer = st.text_area("Your Answer", height=200)

    # 6. Generate Feedback
    if st.button("Generate Feedback"):
        if not user_answer:
            st.warning("Please write an answer first.")
        else:
            with st.spinner("Analyzing your response..."):
                # Feedback Request
                feedback_prompt = f"""
                You are a professional interviewer. 
                Question: {st.session_state['question']}
                Answer: {user_answer}
                
                Provide constructive feedback in bullet points including strengths, weaknesses, and how the answer could be improved.
                """
                
                feedback_response = client.chat.completions.create(
                    model="llama3-8b-8192", 
                    messages=[{"role": "user", "content": feedback_prompt}],
                    temperature=0.7
                )
                
                # Rating Request
                rating_prompt = f"""
                Rate this answer out of 5 based on the question: {st.session_state['question']}
                Answer: {user_answer}
                
                Format:
                Rating: X/5
                Reason: <one-line justification>
                """
                
                rating_response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": rating_prompt}],
                    temperature=0.7
                )

                # Display Results
                st.subheader("📝 AI Feedback")
                st.markdown(feedback_response.choices[0].message.content)
                
                st.subheader("⭐ Final Rating")
                st.markdown(rating_response.choices[0].message.content)
