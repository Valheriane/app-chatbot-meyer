from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message, MessageSource
from app.services.groq_service import call_groq
from app.services.prompt_service import build_prompt
from app.services.retrieval_service import retrieve_chunks


def ask_rag(
    db: Session,
    question: str,
    mode: str = "search",
    conversation_id: int | None = None,
    k: int = 6,
    verbosity: str = "normal",
) -> dict:
    if conversation_id is None:
        conversation = Conversation(
            title=question[:80],
            mode=mode,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    else:
        conversation = db.get(Conversation, conversation_id)
        if conversation is None:
            raise ValueError("Conversation introuvable.")

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=question,
    )
    db.add(user_message)
    db.commit()

    sources = retrieve_chunks(db, question, k=k)
    prompt = build_prompt(
        question,
        sources,
        mode=mode,
        verbosity=verbosity,
    )
    answer = call_groq(prompt)

    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=answer,
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    for rank, source in enumerate(sources, start=1):
        db.add(
            MessageSource(
                message_id=assistant_message.id,
                chunk_id=source["chunk_id"],
                score=source["score"],
                rank=rank,
            )
        )

    db.commit()

    return {
        "conversation_id": conversation.id,
        "answer": answer,
        "sources": sources,
    }