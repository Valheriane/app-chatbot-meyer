import json
import os
import time
from datetime import datetime

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000")

MAX_REQUESTS = 5
WINDOW_SECONDS = 60
MIN_DELAY_BETWEEN_REQUESTS = 2


st.set_page_config(
    page_title="Meyer RAG — Épée longue",
    page_icon="⚔️",
    layout="wide",
)


# =========================
# CSS
# =========================

st.markdown(
    """
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }

    .app-title {
        text-align: center;
        font-size: 2.3rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .app-subtitle {
        text-align: center;
        font-size: 1.05rem;
        color: #666;
        margin-bottom: 1.5rem;
    }

    .welcome-box {
        background: #f8f5ef;
        border: 1px solid #d8c7a3;
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }

    div[data-testid="stSidebar"] {
        background: #f7f3ea;
    }
</style>
""",
    unsafe_allow_html=True,
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


def send_question(
    question: str,
    conversation_id: int | None,
    mode: str,
    k: int,
    verbosity: str,
    temperature: float,
):
    payload = {
        "question": question,
        "conversation_id": conversation_id,
        "mode": mode,
        "k": k,
        "verbosity": verbosity,
        "temperature": temperature,
    }

    response = requests.post(
        f"{API_URL}/chat",
        json=payload,
        timeout=300,
    )

    response.raise_for_status()
    return response.json()


# =========================
# Rate limiting
# =========================

def init_rate_limit():
    if "request_timestamps" not in st.session_state:
        st.session_state.request_timestamps = []

    if "last_request_time" not in st.session_state:
        st.session_state.last_request_time = 0.0


def check_rate_limit():
    now = time.time()

    st.session_state.request_timestamps = [
        ts for ts in st.session_state.request_timestamps
        if now - ts < WINDOW_SECONDS
    ]

    time_since_last_request = now - st.session_state.last_request_time

    if time_since_last_request < MIN_DELAY_BETWEEN_REQUESTS:
        remaining = round(MIN_DELAY_BETWEEN_REQUESTS - time_since_last_request, 1)
        return False, f"Merci d’attendre encore {remaining} seconde(s) avant d’envoyer une nouvelle question."

    if len(st.session_state.request_timestamps) >= MAX_REQUESTS:
        return False, "Limite atteinte : trop de requêtes en moins d’une minute. Merci d’attendre un peu."

    return True, None


def register_request():
    now = time.time()
    st.session_state.request_timestamps.append(now)
    st.session_state.last_request_time = now


def get_rate_limit_status():
    now = time.time()

    st.session_state.request_timestamps = [
        ts for ts in st.session_state.request_timestamps
        if now - ts < WINDOW_SECONDS
    ]

    used_requests = len(st.session_state.request_timestamps)
    remaining_requests = MAX_REQUESTS - used_requests

    if st.session_state.request_timestamps:
        oldest_request = min(st.session_state.request_timestamps)
        reset_in = max(0, int(WINDOW_SECONDS - (now - oldest_request)))
    else:
        reset_in = 0

    wait_before_next = max(
        0,
        round(MIN_DELAY_BETWEEN_REQUESTS - (now - st.session_state.last_request_time), 1),
    )

    return {
        "used_requests": used_requests,
        "remaining_requests": remaining_requests,
        "reset_in": reset_in,
        "wait_before_next": wait_before_next,
    }


# =========================
# Métriques
# =========================

def init_metrics():
    if "metrics" not in st.session_state:
        st.session_state.metrics = {
            "total_requests": 0,
            "total_questions": 0,
            "total_errors": 0,
            "rate_limit_blocked": 0,
            "empty_responses": 0,
            "total_response_time": 0.0,
            "last_response_time": 0.0,
            "sources_returned": 0,
            "question_types": {
                "general": 0,
                "technical": 0,
                "drill": 0,
                "source": 0,
                "other": 0,
            },
            "satisfaction_positive": 0,
            "satisfaction_negative": 0,
        }

    if "last_feedback_message_id" not in st.session_state:
        st.session_state.last_feedback_message_id = None

    if "feedback_given_for" not in st.session_state:
        st.session_state.feedback_given_for = set()


def classify_question(question: str, mode: str):
    text = question.lower()

    if mode == "drill" or "drill" in text or "exercice" in text:
        return "drill"

    if mode == "search" or "source" in text or "texte" in text or "passage" in text:
        return "source"

    if mode == "explanation" or "explique" in text or "comment" in text:
        return "technical"

    if mode == "general" or "contexte" in text or "histoire" in text:
        return "general"

    return "other"


def get_average_response_time():
    metrics = st.session_state.metrics

    if metrics["total_requests"] == 0:
        return 0

    return round(metrics["total_response_time"] / metrics["total_requests"], 2)


# =========================
# Session state
# =========================

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_sources" not in st.session_state:
    st.session_state.last_sources = []

init_rate_limit()
init_metrics()


# =========================
# Sidebar
# =========================

with st.sidebar:
    st.title("⚔️ Meyer RAG")

    st.markdown("### ⚙️ Paramètres")

    mode = st.selectbox(
        "Mode de réponse",
        ["general", "search", "explanation", "drill", "teaching_sheet"],
        format_func=lambda x: {
            "general": "Question générale / synthèse",
            "search": "Recherche documentaire",
            "explanation": "Explication technique",
            "drill": "Création de drill",
            "teaching_sheet": "Fiche pédagogique",
        }[x],
    )

    verbosity = st.selectbox(
        "Niveau de détail",
        ["short", "normal", "detailed", "course"],
        index=1,
        format_func=lambda x: {
            "short": "Court",
            "normal": "Normal",
            "detailed": "Détaillé",
            "course": "Cours complet",
        }[x],
    )

    temperature = st.select_slider(
        "Température du modèle",
        options=[0.0, 0.5, 1.0],
        value=0.2 if 0.2 in [0.0, 0.5, 1.0] else 0.5,
    )

    st.caption(
        "0 = déterministe · 0.5 = équilibré · 1 = plus créatif"
    )

    k = st.slider("Nombre de sources", 3, 12, 6)

    st.divider()

    st.markdown("### 🧰 Actions")

    if st.button("➕ Nouvelle conversation", use_container_width=True):
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.session_state.last_sources = []
        st.session_state.last_feedback_message_id = None
        st.rerun()

    if st.button("🗑️ Reset interface", use_container_width=True):
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.session_state.last_sources = []
        st.session_state.metrics = {
            "total_requests": 0,
            "total_questions": 0,
            "total_errors": 0,
            "rate_limit_blocked": 0,
            "empty_responses": 0,
            "total_response_time": 0.0,
            "last_response_time": 0.0,
            "sources_returned": 0,
            "question_types": {
                "general": 0,
                "technical": 0,
                "drill": 0,
                "source": 0,
                "other": 0,
            },
            "satisfaction_positive": 0,
            "satisfaction_negative": 0,
        }
        st.session_state.request_timestamps = []
        st.session_state.last_request_time = 0.0
        st.rerun()

    if st.session_state.messages:
        export_data = {
            "conversation_id": st.session_state.conversation_id,
            "exported_at": datetime.now().isoformat(),
            "messages": st.session_state.messages,
            "last_sources": st.session_state.last_sources,
            "metrics": st.session_state.metrics,
        }

        st.download_button(
            "💾 Exporter la conversation JSON",
            data=json.dumps(export_data, ensure_ascii=False, indent=2),
            file_name="meyer_conversation.json",
            mime="application/json",
            use_container_width=True,
        )

    st.divider()

    st.markdown("### 📚 Conversations")

    conversations = get_conversations()

    conversation_options = {
        f"#{conv['id']} — {conv.get('title') or 'Sans titre'}": conv["id"]
        for conv in conversations
    }

    if conversation_options:
        selected_label = st.selectbox(
            "Historique",
            options=["Aucune"] + list(conversation_options.keys()),
        )

        if selected_label != "Aucune":
            selected_id = conversation_options[selected_label]

            if st.button("📂 Charger cette conversation", use_container_width=True):
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
                    st.session_state.last_feedback_message_id = None
                    st.rerun()
                else:
                    st.error("Impossible de charger cette conversation.")
    else:
        st.info("Aucune conversation enregistrée.")

    st.divider()

    st.markdown("### ⏱️ Limitation des requêtes")

    rate_status = get_rate_limit_status()

    st.markdown(
        f"""
| Indicateur | Valeur |
|---|---:|
| Utilisées | {rate_status['used_requests']} / {MAX_REQUESTS} |
| Restantes | {rate_status['remaining_requests']} |
| Reset dans | {rate_status['reset_in']} s |
| Prochaine requête | {rate_status['wait_before_next']} s |
"""
    )

    st.progress(rate_status["used_requests"] / MAX_REQUESTS)

    st.divider()

    metrics = st.session_state.metrics

    with st.expander("📈 Monitoring", expanded=False):
        st.markdown(
            f"""
| Métrique | Valeur |
|---|---:|
| Requêtes API | {metrics['total_requests']} |
| Questions posées | {metrics['total_questions']} |
| Erreurs | {metrics['total_errors']} |
| Blocages rate limit | {metrics['rate_limit_blocked']} |
| Réponses vides | {metrics['empty_responses']} |
| Dernier temps de réponse | {round(metrics['last_response_time'], 2)} s |
| Temps moyen de réponse | {get_average_response_time()} s |
| Sources retournées | {metrics['sources_returned']} |
"""
        )

    with st.expander("🧠 Types de questions", expanded=False):
        question_types = metrics["question_types"]
        st.markdown(
            f"""
| Type | Nombre |
|---|---:|
| Général | {question_types['general']} |
| Technique | {question_types['technical']} |
| Drill | {question_types['drill']} |
| Source | {question_types['source']} |
| Autre | {question_types['other']} |
"""
        )

    with st.expander("🙂 Satisfaction", expanded=False):
        st.markdown(
            f"""
| Indicateur | Valeur |
|---|---:|
| 👍 Positif | {metrics['satisfaction_positive']} |
| 👎 Négatif | {metrics['satisfaction_negative']} |
"""
        )


# =========================
# Page principale
# =========================

st.markdown(
    '<div class="app-title">⚔️ Meyer RAG — Épée longue</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="app-subtitle">Assistant RAG pour explorer Joachim Meyer, ses sources et leurs usages pédagogiques.</div>',
    unsafe_allow_html=True,
)

if st.session_state.conversation_id:
    st.caption(f"Conversation active : #{st.session_state.conversation_id}")
else:
    st.caption("Nouvelle conversation")

st.markdown(
    """
<div class="welcome-box">
<strong>Bienvenue.</strong><br>
Pose une question sur Meyer, une technique, un principe, une source ou demande un drill pédagogique.
Le chatbot utilise une recherche documentaire dans le corpus avant de générer sa réponse.
</div>
""",
    unsafe_allow_html=True,
)


# =========================
# Affichage conversation
# =========================

for message in st.session_state.messages:
    role = message.get("role", "assistant")

    if role == "user":
        with st.chat_message("user", avatar="🧑"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar="⚔️"):
            st.markdown(message["content"])


# =========================
# Zone de saisie
# =========================

question = st.chat_input("Pose ta question sur Meyer, une technique ou un drill...")

if question:
    question = question.strip()

    if not question:
        st.warning("Merci d’écrire une question avant d’envoyer.")

    elif len(question) < 3:
        st.warning("La question est trop courte. Essaie d’écrire une vraie demande.")

    else:
        allowed, error_message = check_rate_limit()

        if not allowed:
            st.session_state.metrics["rate_limit_blocked"] += 1
            st.warning(error_message)

        else:
            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": question,
                }
            )

            with st.chat_message("user", avatar="🧑"):
                st.markdown(question)

            with st.chat_message("assistant", avatar="⚔️"):
                try:
                    with st.spinner("Recherche dans le corpus Meyer..."):
                        start_time = time.time()

                        data = send_question(
                            question=question,
                            conversation_id=st.session_state.conversation_id,
                            mode=mode,
                            k=k,
                            verbosity=verbosity,
                            temperature=temperature,
                        )

                        end_time = time.time()

                    response_time = end_time - start_time

                    st.session_state.conversation_id = data["conversation_id"]

                    answer = data.get("answer", "")
                    sources = data.get("sources", [])

                    if not answer or not answer.strip():
                        st.session_state.metrics["empty_responses"] += 1
                        st.warning("Le modèle a renvoyé une réponse vide.")
                    else:
                        st.markdown(answer)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                        }
                    )

                    st.session_state.last_sources = sources

                    register_request()

                    st.session_state.metrics["total_requests"] += 1
                    st.session_state.metrics["total_questions"] += 1
                    st.session_state.metrics["last_response_time"] = response_time
                    st.session_state.metrics["total_response_time"] += response_time
                    st.session_state.metrics["sources_returned"] += len(sources)

                    question_type = classify_question(question, mode)
                    st.session_state.metrics["question_types"][question_type] += 1

                    st.session_state.last_feedback_message_id = (
                        f"assistant_{len(st.session_state.messages)}_{int(time.time())}"
                    )

                except requests.exceptions.ReadTimeout:
                    st.session_state.metrics["total_errors"] += 1
                    st.error(
                        "Le backend met trop longtemps à répondre. "
                        "Merci de réessayer dans quelques instants."
                    )

                except requests.exceptions.ConnectionError:
                    st.session_state.metrics["total_errors"] += 1
                    st.error(
                        "Impossible de joindre le backend. "
                        "Vérifie que FastAPI tourne bien sur http://localhost:8000."
                    )

                except requests.exceptions.HTTPError as error:
                    st.session_state.metrics["total_errors"] += 1
                    st.error("Le serveur a renvoyé une erreur HTTP.")
                    st.caption(str(error))

                except ValueError as error:
                    st.session_state.metrics["total_errors"] += 1
                    st.warning(f"Réponse invalide : {error}")

                except Exception as error:
                    st.session_state.metrics["total_errors"] += 1
                    st.error("Une erreur inattendue est survenue. Merci de réessayer.")
                    st.caption(str(error))


# =========================
# Satisfaction
# =========================

feedback_id = st.session_state.get("last_feedback_message_id")

if feedback_id:
    if feedback_id not in st.session_state.feedback_given_for:
        st.markdown("### Cette réponse t’a-t-elle aidée ?")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("👍 Oui", key=f"like_{feedback_id}"):
                st.session_state.metrics["satisfaction_positive"] += 1
                st.session_state.feedback_given_for.add(feedback_id)
                st.success("Merci pour ton retour 👍")
                st.rerun()

        with col2:
            if st.button("👎 Non", key=f"dislike_{feedback_id}"):
                st.session_state.metrics["satisfaction_negative"] += 1
                st.session_state.feedback_given_for.add(feedback_id)
                st.info("Merci pour ton retour.")
                st.rerun()
    else:
        st.caption("Retour déjà enregistré pour cette réponse.")


# =========================
# Sources de la dernière réponse
# =========================

if st.session_state.last_sources:
    st.divider()
    st.subheader("Sources de la dernière réponse")

    for index, source in enumerate(st.session_state.last_sources, start=1):
        title = source.get("title") or "Source inconnue"
        score = source.get("score", 0)

        label = f"Source {index} — {title} — score {score:.3f}"

        with st.expander(label):
            st.write("**Langue :**", source.get("language"))
            st.write("**Type :**", source.get("source_type"))
            st.write("**Niveau :**", source.get("truth_level"))
            st.write("**Chunk ID :**", source.get("chunk_id"))
            st.write("**Document ID :**", source.get("document_id"))
            st.markdown("### Extrait")
            st.write(source.get("content"))