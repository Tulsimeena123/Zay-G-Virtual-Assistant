import io
import re
from datetime import datetime

import streamlit as st
from pypdf import PdfReader
from docx import Document
from gtts import gTTS


# -------------------------------------------------
# ZAY-G : NO API KEY DEMO VIRTUAL ASSISTANT
# -------------------------------------------------

st.set_page_config(
    page_title="Zay-G | Virtual Assistant",
    page_icon="🤖",
    layout="wide"
)

# -------------------- DESIGN --------------------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        135deg,
        #0b1020 0%,
        #111a32 55%,
        #18213d 100%
    );
    color: #f5f7ff;
}

[data-testid="stSidebar"] {
    background: #10182b;
}

.hero {
    padding: 22px 24px;
    border: 1px solid #34415f;
    border-radius: 18px;
    background: linear-gradient(120deg,#182746,#202044);
    margin-bottom: 18px;
}

.hero h1 {
    margin: 0;
    color: white;
    font-size: 2.25rem;
}

.hero p {
    color: #c5d0e8;
    margin-top: 8px;
}

.small-note {
    color: #aebbd5;
    font-size: .88rem;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
    <h1>🤖 Zay-G</h1>
    <p>
        Your smart virtual assistant —
        chat, manage tasks and work with your files.
    </p>
</div>
""", unsafe_allow_html=True)


st.info(
    "Zay-G is running in Demo Mode. "
    "No API key is required. Responses use local rule-based logic."
)


# -------------------- SESSION STATE --------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "file_context" not in st.session_state:
    st.session_state.file_context = ""

if "file_names" not in st.session_state:
    st.session_state.file_names = []

if "tasks" not in st.session_state:
    st.session_state.tasks = []


# -------------------- FILE EXTRACTION --------------------

def extract_text(uploaded_file):

    filename = uploaded_file.name.lower()
    data = uploaded_file.getvalue()

    if filename.endswith(".pdf"):

        reader = PdfReader(io.BytesIO(data))

        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    elif filename.endswith(".docx"):

        document = Document(io.BytesIO(data))

        paragraphs = [
            p.text for p in document.paragraphs
            if p.text.strip()
        ]

        for table in document.tables:
            for row in table.rows:
                paragraphs.append(
                    " | ".join(
                        cell.text for cell in row.cells
                    )
                )

        return "\n".join(paragraphs)

    elif filename.endswith((".txt", ".md", ".csv")):

        return data.decode(
            "utf-8",
            errors="ignore"
        )

    else:
        raise ValueError("Unsupported file format")


# -------------------- DOCUMENT SUMMARY --------------------

def split_sentences(text):

    cleaned = re.sub(r"\s+", " ", text).strip()

    if not cleaned:
        return []

    return [
        part.strip()
        for part in re.split(r"(?<=[.!?])\s+", cleaned)
        if part.strip()
    ]


def summarize_text(text, max_sentences=5):

    sentences = split_sentences(text)

    if not sentences:
        return "No readable text found in the document."

    return " ".join(sentences[:max_sentences])


# -------------------- DOCUMENT SEARCH --------------------

def find_relevant_sentences(text, query, limit=5):

    sentences = split_sentences(text)

    words = {
        word.lower()
        for word in re.findall(r"[A-Za-z0-9_]+", query)
        if len(word) > 2
    }

    if not words:
        return []

    scored = []

    for sentence in sentences:

        sentence_words = {
            word.lower()
            for word in re.findall(
                r"[A-Za-z0-9_]+",
                sentence
            )
        }

        score = len(
            words.intersection(sentence_words)
        )

        if score:
            scored.append((score, sentence))

    scored.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        sentence
        for score, sentence in scored[:limit]
    ]


# -------------------- TASK ASSISTANT --------------------

def manage_tasks(text):

    lower = text.lower().strip()

    if lower.startswith("add task:") or lower.startswith("add task "):

        if ":" in text:
            task = text.split(":", 1)[1].strip()
        else:
            task = text[9:].strip()

        if not task:
            return "Please enter a task name."

        st.session_state.tasks.append({
            "text": task,
            "done": False
        })

        return f"Task added successfully: **{task}**"

    if lower in [
        "show tasks",
        "my tasks",
        "list tasks",
        "show my tasks"
    ]:

        if not st.session_state.tasks:
            return "You don't have any tasks yet."

        result = []

        for index, task in enumerate(
            st.session_state.tasks,
            start=1
        ):

            status = "✅" if task["done"] else "⬜"

            result.append(
                f"{index}. {status} {task['text']}"
            )

        return "\n\n".join(result)

    if lower.startswith("done task ") or lower.startswith("complete task "):

        match = re.search(r"(\d+)", lower)

        if not match:
            return "Please mention the task number."

        index = int(match.group(1)) - 1

        if index < 0 or index >= len(st.session_state.tasks):
            return "Task number not found."

        st.session_state.tasks[index]["done"] = True

        return "Task marked as completed! ✅"

    if lower in ["clear tasks", "delete all tasks"]:

        st.session_state.tasks = []

        return "All tasks cleared successfully."

    return None


# -------------------- ZAY-G ASSISTANT --------------------

def local_reply(user_text):

    text = user_text.strip()
    lower = text.lower()

    # Task commands
    task_response = manage_tasks(text)

    if task_response:
        return task_response

    # Greetings
    if any(
        greeting in lower
        for greeting in [
            "hello",
            "hi",
            "hey",
            "namaste",
            "hii"
        ]
    ):

        return (
            "Hello! 👋 I'm **Zay-G**, your virtual assistant. "
            "I can help you manage tasks and find information "
            "in uploaded documents. Type `help` to explore my features."
        )

    # Help
    if lower in [
        "help",
        "features",
        "commands",
        "what can you do"
    ]:

        return """
        **Zay-G Features**

        1. Chat interface
        2. Document upload
        3. Document text extraction
        4. Document keyword search
        5. Basic document summary
        6. Task management
        7. Chat history
        8. Text-to-speech

        **Task Commands**

        - `Add task: Complete assignment`
        - `Show tasks`
        - `Done task 1`
        - `Clear tasks`

        Note: This is a rule-based demo, not a generative AI model.
        """

    # Introduction
    if (
        "who are you" in lower
        or "your name" in lower
        or "introduce yourself" in lower
    ):

        return (
            "I'm **Zay-G**, a virtual assistant prototype. "
            "I can manage your tasks and help you search "
            "through uploaded documents."
        )

    # Date and time
    if any(
        word in lower
        for word in ["time", "date", "today"]
    ):

        now = datetime.now().astimezone()

        return (
            "Current date and time: "
            f"**{now.strftime('%d %B %Y, %I:%M %p')}**"
        )

    # Document summary
    if any(
        word in lower
        for word in [
            "summarize",
            "summary",
            "short summary",
            "explain this file"
        ]
    ):

        if not st.session_state.file_context:
            return "Please upload and process a document first."

        summary = summarize_text(
            st.session_state.file_context,
            5
        )

        return (
            "**Document Summary:**\n\n"
            + summary
        )

    # Search uploaded documents
    if st.session_state.file_context:

        matches = find_relevant_sentences(
            st.session_state.file_context,
            text
        )

        if matches:

            result = "\n\n".join(
                f"- {sentence}"
                for sentence in matches
            )

            return (
                "**Relevant information from your files:**\n\n"
                + result
                + "\n\n"
                "*Results are based on keyword matching.*"
            )

        return (
            "I couldn't find matching information "
            "in your uploaded document. Try different keywords."
        )

    # Default response
    return (
        "I'm running in No-API Demo Mode. "
        "I can respond to supported commands and help with uploaded files. "
        "Type `help` to see available features."
    )


# -------------------- SIDEBAR --------------------

with st.sidebar:

    st.subheader("📎 Your Files")

    uploaded_files = st.file_uploader(
        "Upload PDF, DOCX, TXT, MD or CSV",
        type=["pdf", "docx", "txt", "md", "csv"],
        accept_multiple_files=True
    )

    if st.button(
        "Process Uploaded Files",
        use_container_width=True
    ):

        if not uploaded_files:

            st.warning("Please select a file first.")

        else:

            extracted_parts = []
            names = []

            for uploaded in uploaded_files:

                try:

                    extracted = extract_text(uploaded)

                    if extracted.strip():

                        extracted_parts.append(
                            f"\n--- FILE: {uploaded.name} ---\n"
                            + extracted[:30000]
                        )

                        names.append(uploaded.name)

                    else:

                        st.warning(
                            f"No readable text found in {uploaded.name}."
                        )

                except Exception as error:

                    st.error(
                        f"{uploaded.name}: {error}"
                    )

            st.session_state.file_context = (
                "\n".join(extracted_parts)[:90000]
            )

            st.session_state.file_names = names

            st.success(
                f"Processed {len(names)} file(s)."
            )

    if st.session_state.file_names:

        st.caption(
            "Loaded: "
            + ", ".join(st.session_state.file_names)
        )

    st.markdown("---")

    st.subheader("📝 Task Assistant")

    if st.session_state.tasks:

        for number, task in enumerate(
            st.session_state.tasks,
            start=1
        ):

            status = "✅" if task["done"] else "⬜"

            st.write(
                f"{number}. {status} {task['text']}"
            )

    else:

        st.caption("No tasks added yet.")

    st.markdown("---")

    if st.button(
        "Clear Chat and Files",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.file_context = ""
        st.session_state.file_names = []
        st.session_state.tasks = []

        st.rerun()

    st.caption("Zay-G | Virtual Assistant")


# -------------------- CHAT INTERFACE --------------------

st.subheader("💬 Chat with Zay-G")

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


user_input = st.chat_input(
    "Message Zay-G..."
)

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    answer = local_reply(user_input)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    st.rerun()


# -------------------- VOICE FEATURES --------------------

st.markdown("---")

left, right = st.columns([2, 1])

with left:

    st.subheader("🎙️ Voice Input")

    st.info(
        "You can record audio here. "
        "Voice transcription is not enabled in this no-API demo."
    )

    recorded_audio = st.audio_input(
        "Record your voice"
    )

    if recorded_audio is not None:

        st.audio(recorded_audio)


with right:

    st.subheader("🔊 Voice Output")

    if (
        st.session_state.messages
        and st.session_state.messages[-1]["role"] == "assistant"
    ):

        if st.button("Speak Latest Answer"):

            try:

                audio_buffer = io.BytesIO()

                with st.spinner("Preparing voice..."):

                    gTTS(
                        st.session_state.messages[-1]["content"],
                        lang="en"
                    ).write_to_fp(audio_buffer)

                st.audio(
                    audio_buffer.getvalue(),
                    format="audio/mp3"
                )

            except Exception as error:

                st.error(
                    "Voice output failed. "
                    "Check your internet connection."
                )

    else:

        st.caption(
            "Ask Zay-G a question to enable voice output."
        )


# -------------------- FOOTER --------------------

st.markdown("---")

st.markdown(
    """
    <p class="small-note">
        Zay-G Virtual Assistant | Demo Version
        <br>
        Upload a document and ask questions using keywords.
    </p>
    """,
    unsafe_allow_html=True
)