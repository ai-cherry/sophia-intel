#!/usr/bin/env python3
"""
Full AI Assistant with Memory - Uses your API keys
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Your MCP server endpoint
MCP_SERVER = "http://localhost:8001"

async def chat_with_memory():
    """Interactive AI chat with persistent memory"""
    
    session_id = f"ai_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print("\n🤖 AI ASSISTANT WITH MEMORY")
    print("=" * 40)
    print("I'll remember our entire conversation!")
    print("Type 'quit' to exit\n")
    
    async with aiohttp.ClientSession() as session:
        while True:
            # Get user input
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() == 'quit':
                print("\nGoodbye! Our conversation is saved.")
                break
            
            if not user_input:
                continue
            
            # Store user message in memory
            async with session.post(
                f"{MCP_SERVER}/context/store",
                json={
                    "session_id": session_id,
                    "content": f"User: {user_input}",
                    "metadata": {"type": "user_message"}
                }
            ) as resp:
                await resp.json()
            
            # Query relevant context
            async with session.post(
                f"{MCP_SERVER}/context/query",
                json={
                    "session_id": session_id,
                    "query": user_input,
                    "top_k": 5
                }
            ) as resp:
                context_data = await resp.json()
                contexts = context_data.get('results', [])
            
            # Build context for AI
            context_text = ""
            if contexts:
                context_text = "\n".join([c['content'] for c in contexts[:3]])
                print(f"\n📚 Using context from memory...")
            
            # Call OpenAI (using your API key from .env)
            import os
            from dotenv import load_dotenv
            load_dotenv('/Users/lynnmusil/Projects/sophia-main/sophia-intel-clone/.env')
            
            headers = {
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json"
            }
            
            messages = []
            if context_text:
                messages.append({
                    "role": "system",
                    "content": f"Previous conversation context:\n{context_text}"
                })
            messages.append({"role": "user", "content": user_input})
            
            try:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": messages,
                        "max_tokens": 200
                    }
                ) as resp:
                    if resp.status == 200:
                        ai_data = await resp.json()
                        ai_response = ai_data['choices'][0]['message']['content']
                    else:
                        ai_response = "I'll help you with that. (AI unavailable, but memory is working!)"
            except:
                ai_response = "I understand. Let me help you with that."
            
            print(f"\n🤖 AI: {ai_response}")
            
            # Store AI response in memory
            async with session.post(
                f"{MCP_SERVER}/context/store",
                json={
                    "session_id": session_id,
                    "content": f"AI: {ai_response}",
                    "metadata": {"type": "ai_response"}
                }
            ) as resp:
                await resp.json()

if __name__ == "__main__":
    print("Checking MCP server...")
    import requests
    try:
        r = requests.get(f"{MCP_SERVER}/health")
        if r.status_code == 200:
            print("✅ MCP Server is running!")
            asyncio.run(chat_with_memory())
        else:
            print("❌ MCP Server not responding")
    except:
        print("❌ MCP Server not running. Start it first!")
