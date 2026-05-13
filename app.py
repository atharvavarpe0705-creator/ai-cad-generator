import streamlit as st
import google.generativeai as genai
import os

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(
    page_title="AI CAD Draftsman",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Sidebar Layout
with st.sidebar:
    st.title("⚙️ System Config")
    api_key = st.text_input("Gemini API Key", type="password", help="Paste your Google AI Studio key here.")
    st.markdown("*(Your key is completely secure and deletes when you close the tab)*")
    
    st.markdown("---")
    st.markdown("### 💡 Prompting Tips")
    st.info("""
    To get the best geometry, be highly specific:
    - **State the origin:** e.g., 'Centered at 0,0'
    - **Define units:** e.g., '150mm x 150mm'
    - **Break it down:** e.g., 'First draw the base plate, then add four 10mm holes at the corners.'
    """)

# 3. Main Header
st.title("📐 AI Mechanical CAD Generator")
st.markdown("Describe your mechanical component below. The AI will write the mathematical logic and compile a standard **.dxf** file for AutoCAD, SolidWorks, or CATIA.")
st.divider()

# 4. Main Workspace (Split into two columns)
col1, col2 = st.columns([2, 1], gap="large")

# Left Column: User Input
with col1:
    st.subheader("1. Engineering Specifications")
    user_prompt = st.text_area(
        "Describe the part:",
        height=200,
        placeholder="Example: Draw a rectangular flange 200mm long and 150mm wide. Add a 50mm diameter central bore, and four 10mm diameter mounting holes positioned 15mm inward from each corner."
    )
    generate_btn = st.button("🚀 Generate Geometry", type="primary", use_container_width=True)

# Right Column: Output & Status
with col2:
    st.subheader("2. File Output")
    output_container = st.empty() # Creates a placeholder we can update later
    
    if not api_key:
        output_container.warning("👈 Please provide your API Key in the sidebar to unlock the generator.")
    else:
        output_container.info("Awaiting engineering specifications...")

# 5. Execution Logic
if generate_btn and api_key and user_prompt:
    with col2:
        output_container.empty() # Clear the waiting message
        
        # Creates a cool animated dropdown showing progress
        with st.status("🤖 AI is drafting your part...", expanded=True) as status:
            st.write("Connecting to Gemini 2.5 Flash...")
            try:
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
                
                st.write("Translating English to mathematical coordinates...")
                response = model.generate_content(user_prompt)
                ai_code = response.text.strip()
                
                if ai_code.startswith("```python"):
                    ai_code = ai_code[9:-3].strip()
                    
                st.write("Compiling .dxf binary file...")
                exec(ai_code)
                
                # Update the loading animation to a success state
                status.update(label="✅ Drafting Complete!", state="complete", expanded=False)
                
                if os.path.exists("output.dxf"):
                    st.success("Your CAD file is ready!")
                    
                    with open("output.dxf", "rb") as file:
                        st.download_button(
                            label="⬇️ Download .dxf File",
                            data=file,
                            file_name="ai_generated_part.dxf",
                            mime="application/dxf",
                            use_container_width=True
                        )
                    
                    # Add an expander so nerds (like us) can see the code it wrote
                    with st.expander("👀 View AI's Python Logic"):
                        st.code(ai_code, language='python')
                        
            except Exception as e:
                status.update(label="❌ Generation Failed", state="error", expanded=True)
                st.error("The AI generated invalid geometry logic. Try making your prompt more specific.")
                st.code(ai_code, language='python')
