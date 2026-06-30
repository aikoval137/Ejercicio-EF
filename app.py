import streamlit as st
import cohere
import google.generativeai as genai
from pymongo import MongoClient
import pymupdf  # PyMuPDF
import numpy as np

# ─── CONFIG ───────────────────────────────────────────────────────────────────
COHERE_API_KEY  = "5zDSEx5sEm543Q895Kope54ewQCH2GlNI4ba34Mv"
GEMINI_API_KEY  = "gen-lang-client-0123265654"
MONGO_URI       = "mongodb+srv://aikomasaki:aikoA137@am.kgsz3rt.mongodb.net/"
USER            = "Masaki, Aiko"

DB_NAME         = "pdf_analytics"
COLLECTION_NAME = "embeddings"
# ──────────────────────────────────────────────────────────────────────────────

# Clients
co     = cohere.Client(COHERE_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
gemini = genai.GenerativeModel("gemini-1.5-flash")
mongo  = MongoClient(MONGO_URI)
col    = mongo[DB_NAME][COLLECTION_NAME]

st.set_page_config(page_title="PDF Analytics", page_icon="📄", layout="wide")
st.title("📄 PDF Analytics Platform")
st.caption(f"Usuario: {USER}")

# ─── UPLOAD & PROCESS ─────────────────────────────────────────────────────────
uploaded = st.file_uploader("Sube un PDF", type="pdf")

if uploaded:
    # Extract text
    doc   = pymupdf.open(stream=uploaded.read(), filetype="pdf")
    pages = [page.get_text() for page in doc]
    full_text = "\n".join(pages)
    st.success(f"PDF cargado: {len(pages)} páginas")

    # Embed & store
    if st.button("Procesar e indexar"):
        with st.spinner("Generando embeddings con Cohere..."):
            # Chunk by page
            col.delete_many({})  # clear previous
            for i, page_text in enumerate(pages):
                if not page_text.strip():
                    continue
                response = co.embed(
                    texts=[page_text],
                    model="embed-english-v3.0",
                    input_type="search_document"
                )
                col.insert_one({
                    "page": i + 1,
                    "text": page_text,
                    "embedding": response.embeddings[0]
                })
        st.success("✅ Documento indexado en MongoDB Atlas")

    # ─── CHATBOT ──────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("💬 Chatbot")
    query = st.text_input("Haz una pregunta sobre el documento:")

    if query:
        with st.spinner("Buscando contexto relevante..."):
            # Embed query
            q_embed = co.embed(
                texts=[query],
                model="embed-english-v3.0",
                input_type="search_query"
            ).embeddings[0]

            # Cosine similarity search
            docs = list(col.find({}, {"text": 1, "embedding": 1, "page": 1}))
            if docs:
                scores = []
                for d in docs:
                    a, b = np.array(q_embed), np.array(d["embedding"])
                    sim = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
                    scores.append((sim, d))
                top = sorted(scores, key=lambda x: x[0], reverse=True)[:3]
                context = "\n\n".join([d["text"] for _, d in top])

                # Gemini response
                prompt = f"""Eres un asistente que responde preguntas sobre documentos PDF.
Contexto relevante del documento:
{context}

Pregunta: {query}
Responde en español, de forma clara y concisa."""
                response = gemini.generate_content(prompt)
                st.markdown("**Respuesta:**")
                st.write(response.text)
            else:
                st.warning("Primero indexa el documento.")
