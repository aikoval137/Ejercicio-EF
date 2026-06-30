# PDF Analytics Platform — EF HPC

App Streamlit para búsqueda semántica y chatbot sobre PDFs.

## Stack
- **Frontend:** Streamlit
- **Embeddings:** Cohere (`embed-english-v3.0`)
- **Vector Store:** MongoDB Atlas
- **Chatbot:** Gemini 1.5 Flash
- **Deploy:** Azure Web App for Container + GitHub Actions

## Setup local

```bash
pip install -r requirements.txt
# Edita las variables en app.py (COHERE_API_KEY, GEMINI_API_KEY, MONGO_URI, USER)
streamlit run app.py
```

## Docker local

```bash
docker build -t pdf-app .
docker run -p 8501:8501 pdf-app
```

## Secrets de GitHub Actions necesarios

| Secret | Descripción |
|--------|-------------|
| `ACR_LOGIN_SERVER` | ej: `turegistro.azurecr.io` |
| `ACR_USERNAME` | Usuario del ACR |
| `ACR_PASSWORD` | Password del ACR |
| `AZURE_WEBAPP_NAME` | Nombre de tu Web App en Azure |
| `AZURE_PUBLISH_PROFILE` | Publish profile descargado desde Azure Portal |
