import os
import streamlit as st
import chromadb
import google.generativeai as genai
from pypdf import PdfReader
from dotenv import load_dotenv

# =========================
# 1. SETTINGS & CONFIG
# =========================
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

CHROMA_PATH = "./rag_storage"
COLLECTION_NAME = "pdf_knowledge"
SUMMARY_PROMPT = (
    "Summarize this document thoroughly in 4 detailed bullet points. "
    "Focus on the most important ideas, results, or arguments."
)

st.set_page_config(page_title="RAG-CHATBOT", page_icon="🤖", layout="wide")

st.markdown(
    """
    <style>
    .summary-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #ff4b4b;
    }
    .stChatMessage { border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# 2. MODEL PICKER
# =========================
def configure_gemini():
    if not API_KEY:
        st.error("GOOGLE_API_KEY is not set in your .env file.")
        st.stop()
    genai.configure(api_key=API_KEY)


def get_ai_model():
    """Pick a suitable Gemini model, with graceful fallback."""
    try:
        available = [
            m.name
            for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]
        for target in ["gemini-3-flash", "gemini-2.5-flash", "gemini-flash-latest"]:
            match = next((m for m in available if target in m), None)
            if match:
                return genai.GenerativeModel(match)
        return genai.GenerativeModel(available[0])
    except Exception:
        return genai.GenerativeModel("gemini-1.5-flash")


# =========================
# 3. SESSION & DATABASE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_summary" not in st.session_state:
    st.session_state.doc_summary = ""

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

configure_gemini()


# =========================
# 4. PDF PROCESSING LOGIC
# =========================
def index_pdfs(files):
    """Read PDFs, upsert chunks into Chroma, and build a text stream."""
    full_text_stream = ""
    total_pages = 0

    with st.status(
        "🛠️ System Indexing... (This may take a moment for large PDFs)",
        expanded=True,
    ) as status:

        with st.expander("View detailed progress logs"):
            for pdf in files:
                st.write(f"📖 Current File: {pdf.name}")
                reader = PdfReader(pdf)

                for i, page in enumerate(reader.pages):
                    total_pages += 1
                    text = page.extract_text()
                    if not text:
                        continue

                    clean_text = " ".join(text.split())
                    full_text_stream += clean_text + "\n"

                    collection.upsert(
                        documents=[clean_text],
                        ids=[f"{pdf.name}_{i}"],
                        metadatas=[{"source": pdf.name, "page": i + 1}],
                    )

                    if i % 10 == 0:
                        st.write(f"✅ {pdf.name}: Pg {i+1} indexed")

        status.update(
            label=f"Indexing complete ({total_pages} pages). Generating summary...",
            state="running",
            expanded=False,
        )

    return full_text_stream


def build_executive_summary(full_text_stream: str) -> str:
    """Create a quick executive summary from sampled parts of the corpus."""
    if not full_text_stream.strip():
        return "No readable text found in the uploaded PDFs."

    L = len(full_text_stream)
    seg_size = 5000
    samples = [
        full_text_stream[:seg_size],
        full_text_stream[L // 2 : L // 2 + seg_size],
        full_text_stream[-seg_size:],
    ]
    combined_context = "\n---SEGMENT---\n".join(samples)

    model = get_ai_model()
    response = model.generate_content([SUMMARY_PROMPT, combined_context])
    return response.text


# =========================
# 5. RETRIEVAL + ANSWERING
# =========================
def answer_query(query: str) -> str:
    if collection.count() == 0:
        return "I don't have any indexed documents yet. Please upload and process PDFs first."

    results = collection.query(query_texts=[query], n_results=4)
    docs = results["documents"][0]
    metas = results["metadatas"][0]

    context = "\n\n".join(
        f"Source: {m.get('source', 'unknown')} (page {m.get('page', '?')})\n{d}"
        for d, m in zip(docs, metas)
    )

    system_prompt = (
        "You are a helpful RAG assistant. "
        "Use ONLY the context below to answer the question. "
        "If the answer is not in the context, say you don't know.\n"
    )

    model = get_ai_model()
    response = model.generate_content(
        [system_prompt, f"Context:\n{context}\n\nQuestion: {query}"]
    )
    return response.text


# =========================
# 6. SIDEBAR
# =========================
with st.sidebar:
    st.title("🤖 RAG-CHATBOT")

    st.markdown(
        "Upload one or more PDF files, let the app index them, "
        "and then chat with their contents."
    )

    files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

    if st.button("🚀 Process Documents"):
        if files:
            text_stream = index_pdfs(files)
            st.write("📊 Generating Executive Brief...")
            st.session_state.doc_summary = build_executive_summary(text_stream)
            st.rerun()
        else:
            st.warning("Please upload at least one PDF.")

    if st.button("🗑️ Reset Memory"):
        st.session_state.messages = []
        st.session_state.doc_summary = ""
        try:
            chroma_client.delete_collection(name=COLLECTION_NAME)
        except Exception:
            pass
        st.rerun()


# =========================
# 7. MAIN CHAT WINDOW
# =========================
st.header("🤖 RAG-CHATBOT Intelligence")

if st.session_state.doc_summary:
    st.markdown('<div class="summary-box">', unsafe_allow_html=True)
    st.subheader("📝 Executive Brief")
    st.markdown(st.session_state.doc_summary)
    st.markdown("</div>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

query = st.chat_input("Ask a question about your documents...")
if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    answer = answer_query(query)
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
