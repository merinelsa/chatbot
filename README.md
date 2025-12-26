.A high-performance Retrieval-Augmented Generation (RAG) application that allows users to upload, index, and converse with multiple PDF documents simultaneously.
Instead of just searching for keywords, this tool understands the context of your documents to provide cited, accurate answers using the Google Gemini large language model.

* Key Features
.Executive Briefing: Upon processing, the system automatically generates a comprehensive 4-point summary of the corpus by sampling key segments (beginning, middle, and end) to give you instant value before you even ask a question.
.Vectorized Persistence: Uses ChromaDB to store document embeddings locally. This ensures fast retrieval even with large datasets.
.Source-Backed Answers: Every response from the AI includes specific source citations (Filename and Page Number), allowing for easy fact-checking.
.Intelligent Model Fallback: Includes a robust model-picker that automatically detects and uses the latest available Gemini Flash models for optimized speed and reasoning.
.Clean UX/UI: Built with a professional, high-contrast Streamlit interface featuring custom CSS, status progress logs, and a dedicated executive summary box.

* Technical Stack
Language: Python
LLM: Google Gemini (1.5 Flash / 2.0 Flash)
Vector Database: ChromaDB
Frontend: Streamlit
PDF Parsing: PyPDF

* Getting Started
1. Installation
Clone the repository and install the necessary dependencies:

Bash
git clone https://github.com/merinelsa/chatbot.git
cd chatbot
pip install -r requirements.txt

2. Set Up Environment Variables
Create a .env file in the root directory and add your Google API Key:

Plaintext
GOOGLE_API_KEY=your_actual_api_key_here

3. Run the Application
Bash
streamlit run app.py

* Security & Privacy
This project is configured with a .gitignore to protect your data. Local vector storage (/rag_storage) and your environment secrets (.env) are never uploaded to GitHub, ensuring your API keys and private documents remain on your local machine.

* Project Structure
.app.py: The core application logic, including PDF indexing, RAG retrieval, and the Streamlit UI.
.rag_storage/: Local directory where the ChromaDB vector database resides (excluded from Git).
.requirements.txt: List of Python libraries required to run the project.
