# Wise 🦉 - Your AI Thought Partner

Wise is an AI companion designed to be a second brain, helping you connect ideas, analyze data, and spark new insights. Built for the **Google Cloud + ADK Hackathon**.

Our goal is to create an AI that doesn't just answer questions, but thinks *with* you, adapting its "vibe" to match your cognitive state.

### Core Features

*   **🧠 Dual Cognitive Lenses:** Switch between an **Analytical 🔬** lens for factual, data-driven reasoning and a **Creative 🎨** lens for imaginative, metaphorical brainstorming.
*   **📈 Agentic Tool-Use:** Ask the AI to "plot the trading volume" and our `ConversationalAgent` will use its internal tools to write Python code, generate a Plotly graph, and display it directly in the chat.
*   **💡 Proactive & On-Demand Sparks:** A `DaydreamAgent` proactively analyzes a sample dataset to provide data-driven insights on startup, while on-demand sparks can be generated to overcome mental blocks.
*   **🤖 Adaptive Vibe Detection:** A `VibeDetectionAgent` analyzes your prompts to understand your intent and suggest the appropriate cognitive lens, creating a seamless user experience.

### How We Built It: The "SageMind Architecture"

For this hackathon, we chose to build our own **custom, lightweight agentic framework** from first principles, which we call the **SageMind Architecture**. This approach allowed us to demonstrate a deep understanding of agent orchestration by building the core logic from the ground up, rather than using a high-level toolkit.

*   **Application & Frontend:** A unified **Streamlit** application provides a polished, multi-stage user interface.
*   **Agentic Core:** Our system is powered by a set of custom agents built in **Python**, using the **Google Gemini API** directly for reasoning and generation.
    *   The `ConversationalAgent` acts as our central orchestrator.
    *   The agents use tools like **Pandas** for data manipulation and **Plotly** for visualization.
*   **Deployment:** The application is containerized with **Docker** and deployed on **Google Cloud Run** for scalability and reliability.

### How to Run Locally

Follow these steps to get a local instance of Wise running.

**1. Prerequisites:**
*   Python 3.9+
*   Git

**2. Clone the Repository:**
```bash
git clone https://github.com/daveAnalyst/wise-adk-hackathon.git
cd wise-adk-hackathon
Use code with caution.
Markdown
3. Set Up a Virtual Environment:
Generated bash
# Create the environment
python -m venv venv

# Activate on Windows (Git Bash)
source venv/Scripts/activate

# Activate on macOS / Linux
# source venv/bin/activate
Use code with caution.
Bash
4. Install Dependencies:
Generated bash
pip install -r requirements.txt
Use code with caution.
Bash
5. Set Up Your API Key:
Create a file named .env in the root of the project directory.
Add your Google Gemini API key to this file:
Generated code
GOOGLE_API_KEY="AIzaSy...your-key-here"
Use code with caution.
Important: The .env file is listed in .gitignore and should never be committed to version control.
6. Run the Application:
Generated bash
python -m streamlit run main.py
Use code with caution.
Bash
The application will open automatically in your browser at http://localhost:8501.
What's Next for Wise (Our V2 Vision)
The current prototype is a solid foundation that proves our architectural concept. Our vision is to evolve Wise into a true operating system for thought.
Multimodal & Enterprise Data Input: From a single CSV, Wise will evolve to connect to any data source. This includes connecting directly to enterprise data warehouses like Google BigQuery, allowing users to upload their own custom datasets, and embracing multimodality by giving Wise the ability to analyze and reason from images and documents.
Advanced Agentic Tools: We will give our ConversationalAgent more tools, starting with a live web search for real-time information and a Wolfram Alpha-powered calculator for guaranteed mathematical accuracy.
Persistent "Second Brain": We will move from session-based memory to a real database (like Firestore or a Vector DB) to create a true 'second brain' that learns and builds a knowledge graph of a user's ideas over time.
Scalable Architecture: The core logic will be migrated to a FastAPI backend to handle more complex, asynchronous agentic workflows at enterprise scale.

