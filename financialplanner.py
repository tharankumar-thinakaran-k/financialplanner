import streamlit as st
import google.generativeai as genai
import matplotlib.pyplot as plt
from fpdf import FPDF
import io
import base64

# Configure Gemini API with internal key
genai.configure(api_key="AIzaSyA6xMnaLxir94mpBa9mVjAfdU0X579Uths")

st.set_page_config(page_title="💰 Financial Goal Planner", layout="wide")
st.title("💰 AI Financial Goal Planner")
st.markdown("Plan your savings, investments, and future goals with AI guidance.")

# User Inputs
income = st.number_input("📥 Monthly Income (in INR)", min_value=0, step=1000)
expenses = st.number_input("📤 Monthly Expenses (in INR)", min_value=0, step=1000)
goal = st.text_area("🎯 Your Financial Goal (e.g., Buy a house, Retire early, Kids’ education)")

age = st.slider("🎂 Your Age", 18, 70, 30)
location = st.text_input("📍 Your Location (for investment suggestions)", value="India")

tone = st.radio("🎙️ Choose Tone for the Report", ["Professional", "Friendly", "Motivational"])
format_style = st.selectbox("📄 Report Format Style", ["Detailed", "Summary", "Bullet Points"])

# Save session
if 'plan_text' not in st.session_state:
    st.session_state.plan_text = ''

# Function to talk to Gemini API
def generate_financial_plan(income, expenses, goal, age, location, tone, format_style):
    prompt = f"""
You are a financial advisor AI. The user has a monthly income of INR {income} and monthly expenses of INR {expenses}. 
They are {age} years old and live in {location}. 
Their financial goal is: {goal}.

Generate a {format_style.lower()} report in a {tone.lower()} tone including:
1. Savings plan
2. Monthly/annual budget summary
3. Investment suggestions (based on age & location)
4. Timeline to achieve the goal
5. Risk assessment and tips

End with 3 practical financial tips.
Use Indian financial instruments (e.g., SIPs, PPF, FD, Mutual Funds).
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

# Function to convert text to PDF with UTF-8 support
def convert_to_pdf(text):
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, "Financial Goal Plan", 0, 1, "C")
        
        def add_text(self, text):
            self.set_font("Arial", size=12)
            # Replace problematic characters or handle encoding
            text = text.replace('\u20b9', 'INR ')  # Replace rupee symbol with 'INR'
            for line in text.split("\n"):
                try:
                    self.multi_cell(0, 10, line.encode('latin1', 'replace').decode('latin1'))
                except UnicodeEncodeError:
                    self.multi_cell(0, 10, line.encode('utf-8', 'replace').decode('utf-8'))

    pdf = PDF()
    pdf.add_page()
    pdf.add_text(text)
    # Output to bytes directly, no additional encoding needed
    pdf_bytes = pdf.output(dest="S").encode('latin1', 'replace')
    return io.BytesIO(pdf_bytes)

# Function to draw a sample pie chart (expenses vs. savings)
def show_pie_chart(income, expenses):
    savings = max(income - expenses, 0)
    labels = ['Expenses', 'Savings']
    sizes = [expenses, savings]
    colors = ['#FF9999', '#99FF99']
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

# Button to generate financial plan
if st.button("🚀 Generate Financial Plan"):
    if income == 0 or expenses == 0 or goal.strip() == "":
        st.warning("Please fill all required fields.")
    else:
        with st.spinner("Creating your personalized financial plan..."):
            plan = generate_financial_plan(income, expenses, goal, age, location, tone, format_style)
            st.session_state.plan_text = plan
            st.success("Plan generated!")

# Display the plan if available
if st.session_state.plan_text:
    st.subheader("📋 Your Financial Plan")
    st.text_area("AI-Generated Plan", value=st.session_state.plan_text, height=400)

    # Pie chart for visual insight
    st.subheader("📊 Income Breakdown")
    show_pie_chart(income, expenses)

    # Regenerate button
    if st.button("🔁 Regenerate Plan"):
        with st.spinner("Regenerating with new tone/format..."):
            plan = generate_financial_plan(income, expenses, goal, age, location, tone, format_style)
            st.session_state.plan_text = plan
            st.experimental_rerun()

    # Download button
    pdf_buffer = convert_to_pdf(st.session_state.plan_text)
    b64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
    href = f'<a href="data:application/pdf;base64,{b64}" download="financial_plan.pdf">📥 Download PDF Report</a>'
    st.markdown(href, unsafe_allow_html=True)