# RAG PDF Chatbot

A small project where you can upload PDFs and chat with them.  
Behind the scenes it uses Streamlit, Google Gemini, and ChromaDB.



## What it does

- Upload one or more PDFs  
- Indexes each page into a local ChromaDB vector store  
- Creates a 4‑bullet “Executive Brief” of your documents  
- Lets you ask questions and answers using only the PDF content  
- One click to reset chat and memory



## Tech

- Streamlit (UI and chat)
- Google Gemini (LLM)
- ChromaDB (vector database)
- pypdf, python-dotenv



## Run it locally

git clone https://github.com/<your-username>/rag-chatbot.git
cd rag-chatbot

optional but recommended
python -m venv .venv
.venv\Scripts\activate # Windows

source .venv/bin/activate # mac / linux
pip install -r requirements.txt

Create a `.env` file in the project folder:

GOOGLE_API_KEY=your_real_gemini_api_key_here

Then start the app:

streamlit run app.py

Open the link Streamlit prints (usually `http://localhost:8501`), upload a PDF, click “Process Documents”, and start asking questions.



## Notes

- `.env` and `rag_storage/` are ignored by Git so you do not upload your API key or local database.
- This is a learning and portfolio project – feedback and pull requests are welcome.
