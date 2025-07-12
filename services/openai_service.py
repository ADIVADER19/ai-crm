import os
import openai
from dotenv import load_dotenv
from services.crm_service import get_conversations
from services.rag_service import query_knowledge_base

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_response(user_id: str, user_input: str):
    # Memory: Fetch conversation history
    history = get_conversations(user_id)
    messages = [{"role": "system", "content": "You are a helpful assistant for lease-related queries."}]

    for convo in history:
        for msg in convo.get("messages", []):
            messages.append({"role": msg["role"], "content": msg["content"]})

    # Step 1: Fetch related knowledge from RAG
    retrieved_knowledge = query_knowledge_base(user_input)

    # Step 2: Inject knowledge into prompt
    messages.append({
        "role": "system",
        "content": f"Here is some helpful background knowledge:\n{retrieved_knowledge}"
    })

    # Step 3: Add user's current message
    messages.append({"role": "user", "content": user_input})

    # Step 4: Generate response
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=300,
        temperature=0.7
    )

    return response.choices[0].message.content
