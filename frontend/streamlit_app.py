import requests
import streamlit as st
import os


API_URL = os.getenv("API_URL", "http://localhost:8000")


st.set_page_config(
    page_title="Meyer RAG — Épée longue",
    page_icon="⚔️",
    layout="wide",
)


# =========================
# Fonctions API
# =========================

def get_conversations():
    try:
        response = requests.get(f"{API_URL}/conversations", timeout=20)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException:
        return []


def get_conversation(conversation_id: int):
    try:
        response = requests.get(
            f"{API_URL}/conversations/{conversation_id}",
            timeout=20,
        )
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None


def send_question(question: str, conversation_id: int | None, mode: str, k: int):
    payload = {
        "question": question,
        "conversation_id": conversation_id,
        "mode": mode,
        "k": k,
        "verbosity": verbosity,
    }

    response = requests.post(
        f"{API_URL}/chat",
        json=payload,
        timeout=300,
    )

    response.raise_for_status()
    return response.json()


# =========================
# Session state
# =========================

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_sources" not in st.session_state:
    st.session_state.last_sources = []

if "selected_conversation_label" not in st.session_state:
    st.session_state.selected_conversation_label = None


# =========================
# Sidebar
# =========================

st.sidebar.title("⚔️ Meyer RAG")

mode = st.sidebar.selectbox(
    "Mode",
    ["general", "search", "explanation", "drill", "teaching_sheet"],
    format_func=lambda x: {
        "general": "Question générale / synthèse",
        "search": "Recherche documentaire",
        "explanation": "Explication technique",
        "drill": "Création de drill",
        "teaching_sheet": "Fiche pédagogique",
    }[x],
)

verbosity = st.sidebar.selectbox(
    "Niveau de détail",
    ["short", "normal", "detailed", "course"],
    format_func=lambda x: {
        "short": "Court",
        "normal": "Normal",
        "detailed": "Détaillé",
        "course": "Cours complet",
    }[x],
)

k = st.sidebar.slider("Nombre de sources", 3, 12, 6)

st.sidebar.divider()

if st.sidebar.button("➕ Nouvelle conversation"):
    st.session_state.conversation_id = None
    st.session_state.messages = []
    st.session_state.last_sources = []
    st.rerun()


st.sidebar.subheader("Conversations")

conversations = get_conversations()

conversation_options = {
    f"#{conv['id']} — {conv.get('title') or 'Sans titre'}": conv["id"]
    for conv in conversations
}

if conversation_options:
    selected_label = st.sidebar.selectbox(
        "Historique",
        options=["Aucune"] + list(conversation_options.keys()),
    )

    if selected_label != "Aucune":
        selected_id = conversation_options[selected_label]

        if st.sidebar.button("📂 Charger cette conversation"):
            conversation_data = get_conversation(selected_id)

            if conversation_data and "messages" in conversation_data:
                st.session_state.conversation_id = selected_id
                st.session_state.messages = [
                    {
                        "role": msg["role"],
                        "content": msg["content"],
                    }
                    for msg in conversation_data["messages"]
                ]
                st.session_state.last_sources = []
                st.rerun()
            else:
                st.sidebar.error("Impossible de charger cette conversation.")
else:
    st.sidebar.info("Aucune conversation enregistrée pour l’instant.")


# =========================
# Page principale
# =========================

st.title("⚔️ Meyer RAG — Épée longue")

if st.session_state.conversation_id:
    st.caption(f"Conversation active : #{st.session_state.conversation_id}")
else:
    st.caption("Nouvelle conversation")

st.write(
    "Assistant RAG pour rechercher, expliquer et transformer le corpus de Joachim Meyer en supports pédagogiques."
)


# =========================
# Affichage conversation
# =========================

for message in st.session_state.messages:
    role = message.get("role", "assistant")

    if role == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.write(message["content"])


# =========================
# Zone de saisie
# =========================

question = st.chat_input("Pose ta question sur Meyer, une technique ou un drill...")

if question:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Recherche dans le corpus Meyer..."):
            try:
                data = send_question(
                    question=question,
                    conversation_id=st.session_state.conversation_id,
                    mode=mode,
                    k=k,
                )

                st.session_state.conversation_id = data["conversation_id"]

                answer = data["answer"]
                sources = data.get("sources", [])

                st.write(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

                st.session_state.last_sources = sources

            except requests.exceptions.ReadTimeout:
                st.error(
                    "Le backend met trop longtemps à répondre. "
                    "Vérifie la console FastAPI ou augmente le timeout."
                )

            except requests.exceptions.ConnectionError:
                st.error(
                    "Impossible de joindre le backend. "
                    "Vérifie que FastAPI tourne bien sur http://localhost:8000."
                )

            except requests.exceptions.HTTPError as error:
                st.error(f"Erreur HTTP : {error}")

            except Exception as error:
                st.error(f"Erreur inattendue : {error}")


# =========================
# Sources de la dernière réponse
# =========================

if st.session_state.last_sources:
    st.divider()
    st.subheader("Sources de la dernière réponse")

    for source in st.session_state.last_sources:
        title = source.get("title") or "Source inconnue"
        score = source.get("score", 0)

        label = f"{title} — score {score:.3f}"

        with st.expander(label):
            st.write("**Langue :**", source.get("language"))
            st.write("**Type :**", source.get("source_type"))
            st.write("**Niveau :**", source.get("truth_level"))
            st.write("**Chunk ID :**", source.get("chunk_id"))
            st.write("**Document ID :**", source.get("document_id"))
            st.markdown("### Extrait")
            st.write(source.get("content"))