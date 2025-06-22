# Wise 🦉 - Your AI Thought Partner

Wise is an AI companion designed to be a second brain, helping you connect ideas, analyze data, and spark new insights. Built for the ** Google-ADK-Hackathon **.

Our goal is to create an AI that doesn't just answer questions, but thinks *with* you, adapting its "vibe" to match your cognitive state.

### Core Features

*   **🧠 Dual Cognitive Lenses:** Switch between an **Analytical 🔬** lens for factual, data-driven reasoning and a **Creative 🎨** lens for imaginative, metaphorical brainstorming.
*   **📈 Natural Language to Data Visualization:** Ask the AI to "plot the trading volume" or "create a chart of the closing price," and it will generate and display a Plotly graph directly in the chat.
*   **💡 Proactive & On-Demand Sparks:** Wise analyzes your data to provide proactive insights on startup, and can generate random creative sparks on demand to overcome mental blocks.
*   **🤖 Adaptive Vibe Detection:** Wise analyzes your initial prompt to automatically select the appropriate cognitive lens, creating a seamless user experience.

### Tech Stack

*   **Frontend:** Streamlit
*   **AI & Agents:** Python, Google Gemini API (1.5 Pro for Code Generation, 1.5 Flash for Chat), Pandas, Plotly
*   **Deployment Target:** Google Cloud Run (Containerized with Docker)

### How to Run Locally

Follow these steps to get a local instance of Wise running.

**1. Prerequisites:**
*   Python 3.9+
*   Git

**2. Clone the Repository:**
```bash
git clone https://github.com/your-username/wise-adk-hackathon.git
cd wise-adk-hackathon

**3 setup virtual environment**
python -m venv venv
source venv/Scripts/activate

**4 install dependencies**
pip install -r requirements.txt

**5. Set Up Your API Key**
Create a file named .env in the root of the project directory.
Add your Google Gemini API key to this file

**6. Run the Application:**
python -m streamlit run main.py

### **Project Vision (V2)**
The current prototype is a solid foundation. Our vision for V2 includes:
1 A scalable FastAPI backend to handle complex, asynchronous agentic workflows.
2 Database integration (PostgreSQL & a Vector DB) to provide users with persistent memory and a true "second brain."
3 User authentication for personalized experiences.
4 Advanced multi-agent collaboration and dynamic tool use.
