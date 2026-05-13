import streamlit as st
import google.generativeai as genai
import os

# 1. Page Configuration
st.set_page_config(page_title="AI CAD Assistant", page_icon="✨", layout="centered")

# 2. Sidebar for Settings
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password")
    st.markdown("*(To make this public without asking for a key, you can hide your key in Streamlit Secrets later!)*")
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

st.title("✨ AI CAD Assistant")
st.markdown("Chat with me to generate mechanical `.dxf` files.")

# 3. Initialize Chat History
# This keeps the messages on screen even after the page reloads
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Display past chat messages
for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If this message generated a file, show the download button again
        if "file_path" in message and os.path.exists(message["file_path"]):
            with open(message["file_path"], "rb") as file:
                st.download_button(
                    label="⬇️ Download .dxf",
                    data=file,
                    file_name=f"part_{index}.dxf",
                    mime="application/dxf",
                    key=f"dl_{index}" # Unique key required by Streamlit
                )

# 5. Chat Input (The message box at the bottom)
if prompt := st.chat_input("E.g., Draw a 100x100mm plate with a 20mm hole..."):
    
    # Show user message in chat
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Save user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Show assistant thinking and responding
    with st.chat_message("assistant"):
        if not api_key:
            st.error("⚠️ Please enter your API key in the sidebar first.")
        else:
            with st.spinner("Drafting geometry..."):
                try:
                    # Connect to AI
                    genai.configure(api_key=api_key)
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
                    
                    # Generate Code
                    response = model.generate_content(prompt)
                    ai_code = response.text.strip()
                    
                    if ai_code.startswith("```python"):
                        ai_code = ai_code[9:-3].strip()
                        
                    # Execute Code
                    exec(ai_code)
                    
                    if os.path.exists("output.dxf"):
                        reply_text = "✅ I have finished drafting your part. Here is your file!"
                        st.markdown(reply_text)
                        
                        # Show download button
                        with open("output.dxf", "rb") as file:
                            st.download_button(
                                label="⬇️ Download .dxf File",
                                data=file,
                                file_name="ai_generated_part.dxf",
                                mime="application/dxf",
                                key=f"dl_new_{len(st.session_state.messages)}"
                            )
                        
                        # Save the assistant's success response to history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": reply_text,
                            "file_path": "output.dxf"
                        })
                
                except Exception as e:
                    error_msg = "❌ I encountered an error with that geometry. Please try being more specific."
                    st.error(error_msg)
                    with st.expander("View Error"):
                        st.write(e)
                    
                    # Save error to history
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
