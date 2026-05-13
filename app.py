import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="AI CAD Assistant", page_icon="✨", layout="centered")

# 1. Sidebar is now just for tools, no API key needed!
with st.sidebar:
    st.title("⚙️ Engineering Tools")
    st.info("This AI is configured for Mechanical Engineering CAD generation.")
    
    if st.button("🗑️ Clear Workspace"):
        st.session_state.messages = []
        st.rerun()

st.title("✨ AI CAD Assistant")
st.markdown("Chat with me to generate mechanical `.dxf` files.")

# 2. Fetch the hidden API Key from Streamlit Secrets
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
except KeyError:
    st.error("⚠️ System Error: API Key not found in server secrets.")
    st.stop()

# 3. Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Display past chat messages
for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "file_path" in message and os.path.exists(message["file_path"]):
            with open(message["file_path"], "rb") as file:
                st.download_button(
                    label="⬇️ Download .dxf",
                    data=file,
                    file_name=f"part_{index}.dxf",
                    mime="application/dxf",
                    key=f"dl_{index}"
                )

# 5. Chat Input
if prompt := st.chat_input("E.g., Draw a 100x100mm plate with a 20mm hole..."):
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("Drafting geometry..."):
            try:
                # The model is pre-configured with your secret key now!
                model = genai.GenerativeModel(
                    model_name='gemini-2.5-flash',
                    system_instruction="""
                    You are an expert mechanical design engineer and Python programmer.
                    Your ONLY job is to output a Python script using the 'ezdxf' library based on the user's request.
                    - Save the file EXACTLY as 'output.dxf'.
                    - Output ONLY the raw Python code. Do not include markdown formatting.
                    - Do not explain the code.
                    """
                )
                
                response = model.generate_content(prompt)
                ai_code = response.text.strip()
                
                if ai_code.startswith("```python"):
                    ai_code = ai_code[9:-3].strip()
                    
                exec(ai_code)
                
                if os.path.exists("output.dxf"):
                    reply_text = "✅ I have finished drafting your part. Here is your file!"
                    st.markdown(reply_text)
                    
                    with open("output.dxf", "rb") as file:
                        st.download_button(
                            label="⬇️ Download .dxf File",
                            data=file,
                            file_name="ai_generated_part.dxf",
                            mime="application/dxf",
                            key=f"dl_new_{len(st.session_state.messages)}"
                        )
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": reply_text,
                        "file_path": "output.dxf"
                    })
            
            except Exception as e:
                error_msg = "❌ I encountered an error with that geometry. Please try being more specific."
                st.error(error_msg)
                with st.expander("View Developer Error"):
                    st.write(e)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
