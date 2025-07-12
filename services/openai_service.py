from openai import OpenAI
import os
from dotenv import load_dotenv
from services.rag_service import query_knowledge_base
from services.crm_service import get_recent_conversations
from helpers import classify_message_category

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_response(user_id: str, user_input: str):
    try:
        print(f"Processing request for user: {user_id}")
        print(f"User input: {user_input}")        
        detected_category = classify_message_category(user_input)

        try:
            recent_conversations = get_recent_conversations(user_id, limit=3)
            print(f"Retrieved {len(recent_conversations)} recent conversations")
        except Exception as e:
            print(f"Error getting conversations: {e}")
            recent_conversations = []
        
        messages = [{
            "role": "system", 
            "content": """You are a helpful real estate assistant specializing in Manhattan rental properties in New York City.

            IMPORTANT CONTEXT:
            - ALL properties in our database are located in Manhattan, NYC
            - Addresses like "15 W 38th St" and "36 W 36th St" are Manhattan locations
            - When users ask about "properties" without specifying location, assume they mean Manhattan properties
            - Our database contains commercial rental spaces in Manhattan
            
            Guidelines:
            - Always mention that properties are in Manhattan when responding
            - Include specific property details (address, price, size, floor, suite)
            - If multiple properties match, list them clearly with rent prices
            - When users ask for "cheapest" properties, focus on the lowest rent options
            - Include broker contact information when available
            - Format your response in a clear, organized manner
            """
        }]

        # add recent conversation context only 2 messages from each
        recent_messages = []
        for conv in recent_conversations:
            for msg in conv.get("messages", [])[-2:]:
                recent_messages.append({
                    "role": msg["role"], 
                    "content": msg["content"]
                })
        
        # limit total messages to reduce token usage
        if len(recent_messages) > 6:
            recent_messages = recent_messages[-6:]
        
        messages.extend(recent_messages)
        print(f"Added {len(recent_messages)} messages from history")

        try:
            print("Querying knowledge base...")
            retrieved_knowledge = query_knowledge_base(user_input, k=50)
            print(f"Retrieved knowledge: {retrieved_knowledge[:200]}..." if retrieved_knowledge else "No knowledge retrieved")
        except Exception as e:
            print(f"Error querying knowledge base: {e}")
            retrieved_knowledge = "Error accessing knowledge base"

        if retrieved_knowledge and "No relevant information" not in retrieved_knowledge and "Error" not in retrieved_knowledge:
            messages.append({
                "role": "system",
                "content": f"""Here are the relevant Manhattan commercial properties from our database:

{retrieved_knowledge}

Please use this information to answer the user's question. Remember to mention that all these properties are located in Manhattan, NYC. Be specific about properties that match their criteria."""
            })
        else:
            messages.append({
                "role": "system",
                "content": "No specific property matches were found in our Manhattan database. Provide general guidance about Manhattan commercial real estate and suggest the user contact us for more options."
            })
            
        messages.append({"role": "user", "content": user_input})
        
        print(f"Sending {len(messages)} messages to OpenAI")
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=2000,
                temperature=0.3,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            ai_response = response.choices[0].message.content
            print(f"OpenAI response received: {ai_response[:100]}...")
            return ai_response, detected_category
            
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return f"I apologize, but I'm experiencing an API issue: {str(e)}", detected_category

    except Exception as e:
        print(f"General error in generate_response: {e}")
        import traceback
        traceback.print_exc()
        return f"I apologize, but I'm having trouble processing your request: {str(e)}", "general"
