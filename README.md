# Zay-G — AI Virtual Assistant

A Streamlit-based AI assistant with chat, conversation context, file uploads (PDF/DOCX/TXT/MD/CSV), voice input, and text-to-speech output.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create and activate a virtual environment (optional but recommended):
   - Windows: `py -m venv .venv` then `.venv\\Scripts\\activate`
4. Install dependencies: `python -m pip install -r requirements.txt`
5. Run: `streamlit run app.py`
6. Paste your Gemini API key in the sidebar.

Get an API key from Google AI Studio: https://aistudio.google.com/apikey

## Deploy on Streamlit Community Cloud
1. Push this folder to a GitHub repository.
2. In Streamlit Community Cloud, create an app from that repository and select `app.py`.
3. In the app's Settings / Secrets, add:
   ```toml
   GEMINI_API_KEY = "your-key-here"
   GEMINI_MODEL = "gemini-3.8-flash"
   ```
4. Save and wait for deployment.

## Security
- Never commit API keys, `.env`, or `.streamlit/secrets.toml` to GitHub.
- For public deployment, set the key in Streamlit's Secrets manager.
- Uploaded file text is sent to the configured AI model when you ask a question. Do not upload confidential or sensitive documents.

## Current limitations
- File Q&A uses extracted text; scanned/image-only PDFs need OCR and are not yet supported.
- Voice input is sent to the model for interpretation; browser microphone permission is required.
- Voice output uses gTTS and currently speaks English.
