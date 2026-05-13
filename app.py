import streamlit as st
import google.generativeai as genai
import os

# Set up the webpage title and layout
st.set_page_config(page_title="AI CAD Generator", layout="centered")
st.title("AI Mechanical CAD Scripter ⚙️")
st.write("Describe a mechanical part, and the AI will generate a standard `.dxf` file you can open in AutoCAD, CATIA, or SolidWorks.")

# Sidebar for secure API Key input
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Enter your Gemini API Key", type="password")
st.sidebar.markdown("*(Your key is not saved or stored anywhere)*")

# Main user input area
user_prompt = st.text_area("What do you want to draw?", "e.g., Draw a rectangular plate 200x100mm with a 50mm hole in the center.")

# When the user clicks the generate button
if st.button("Generate CAD File", type="primary"):
    if not api_key:
        st.warning("⚠️ Please enter your Gemini API Key in the sidebar first.")
    else:
        with st.spinner("AI is designing your part..."):
            try:
                # 1. Connect to Gemini
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name='gemini-2.5-flash',
                    system_instruction="""
                    You are an expert mechanical design engineer and Python programmer.
                    The user will ask for a 2D mechanical drawing. 
                    Your ONLY job is to output a Python script using the 'ezdxf' library.
                    - Save the file EXACTLY as 'output.dxf'.
                    - Output ONLY the raw Python code. Do not include markdown formatting.
                    - Do not explain the code.
                    """
                )
                
                # 2. Get the code from the AI
                response = model.generate_content(user_prompt)
                ai_code = response.text.strip()
                
                # Clean up formatting if necessary
                if ai_code.startswith("```python"):
                    ai_code = ai_code[9:-3].strip()
                    
                # 3. Run the AI's code to create output.dxf
                exec(ai_code)
                
                # 4. Provide a download button for the user
                if os.path.exists("output.dxf"):
                    st.success("✅ Part generated successfully!")
                    
                    with open("output.dxf", "rb") as file:
                        st.download_button(
                            label="⬇️ Download .dxf File",
                            data=file,
                            file_name="ai_generated_part.dxf",
                            mime="application/dxf"
                        )
            except Exception as e:
                st.error("❌ The AI made a mistake in the geometry logic. Try tweaking your prompt.")
                with st.expander("See technical error and AI code"):
                    st.write(e)
                    st.code(ai_code, language='python')
