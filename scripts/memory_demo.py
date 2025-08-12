#!/usr/bin/env python3
"""
Interactive demo of the contextualized memory system
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_servers.memory_service import MemoryService
from services.portkey_client import PortkeyClient
from loguru import logger

class MemoryDemo:
    def __init__(self):
        self.memory = MemoryService()
        self.ai_client = PortkeyClient()
        self.session_id = f"demo_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    async def run(self):
        """Run the interactive demo"""
        print("\n" + "="*60)
        print("🧠 SOPHIA INTEL - Contextualized Memory Demo")
        print("="*60)
        print("\nThis demo shows how the system maintains context across conversations.")
        print("Type 'quit' to exit, 'history' to see stored context, or 'clear' to reset.\n")
        
        # Store initial context about the user
        await self.memory.store_context(
            self.session_id,
            "This is a demo session for the Sophia Intel MCP server with memory capabilities.",
            {"type": "system", "timestamp": datetime.now().isoformat()}
        )
        
        while True:
            try:
                # Get user input
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() == 'quit':
                    print("\nGoodbye! Session context has been saved locally.")
                    break
                    
                elif user_input.lower() == 'history':
                    await self.show_history()
                    continue
                    
                elif user_input.lower() == 'clear':
                    await self.clear_memory()
                    continue
                    
                elif not user_input:
                    continue
                
                # Store user input in memory
                await self.memory.store_context(
                    self.session_id,
                    f"User said: {user_input}",
                    {"type": "user_message", "timestamp": datetime.now().isoformat()}
                )
                
                # Query relevant context
                context = await self.memory.query_context(
                    self.session_id,
                    user_input,
                    top_k=3
                )
                
                # Display relevant context found
                if context:
                    print("\n📚 Relevant context found:")
                    for ctx in context[:2]:
                        print(f"  - {ctx['content'][:80]}...")
                
                # Simulate AI response (you could integrate with real AI here)
                response = await self.generate_response(user_input, context)
                print(f"\n🤖 Assistant: {response}")
                
                # Store AI response in memory
                await self.memory.store_context(
                    self.session_id,
                    f"Assistant said: {response}",
                    {"type": "assistant_message", "timestamp": datetime.now().isoformat()}
                )
                
            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"\n❌ Error: {e}")
    
    async def generate_response(self, user_input: str, context: list) -> str:
        """Generate a response (mock for demo, can integrate real AI)"""
        # For demo purposes, we'll create contextual responses based on patterns
        user_lower = user_input.lower()
        
        # Check if asking about previously mentioned information
        if any(word in user_lower for word in ["remember", "recall", "said", "mentioned"]):
            if context:
                return f"Yes, I remember. {context[0]['content']}"
            else:
                return "I don't have any specific context about that in our conversation."
        
        # Name-related queries
        if "name" in user_lower and "my" in user_lower:
            for ctx in context:
                if "Lynn" in ctx['content']:
                    return "Your name is Lynn Musil, and you're working on the Sophia Intel project."
            return "I don't have your name in my context. What would you like me to call you?"
        
        # Project-related queries
        if any(word in user_lower for word in ["project", "sophia", "mcp"]):
            return "The Sophia Intel project is an advanced MCP server with AI routing and memory capabilities. It uses local storage or Qdrant for maintaining conversation context."
        
        # Technical queries
        if any(word in user_lower for word in ["memory", "context", "storage"]):
            return "I'm using a contextualized memory system that stores our conversation locally. This allows me to maintain context across our discussion and retrieve relevant information when needed."
        
        # Default response with context awareness
        if context:
            return f"I understand you're asking about '{user_input}'. Based on our conversation context, I can help you with that."
        else:
            return f"I see you're asking about '{user_input}'. This is now stored in my memory for future reference."
    
    async def show_history(self):
        """Show conversation history"""
        history = await self.memory.get_session_history(self.session_id, limit=10)
        
        print("\n📜 Conversation History:")
        print("-" * 40)
        
        if history:
            for item in history:
                timestamp = item.get('timestamp', 'Unknown time')
                content = item.get('content', '')
                print(f"[{timestamp[:19]}] {content[:100]}")
        else:
            print("No history found for this session.")
    
    async def clear_memory(self):
        """Clear session memory"""
        await self.memory.clear_session(self.session_id)
        print("\n🗑️  Memory cleared for this session.")
        
        # Re-initialize with basic context
        await self.memory.store_context(
            self.session_id,
            "Memory was cleared. Starting fresh conversation.",
            {"type": "system", "timestamp": datetime.now().isoformat()}
        )

async def main():
    """Run the demo"""
    demo = MemoryDemo()
    await demo.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo terminated.")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        sys.exit(1)
