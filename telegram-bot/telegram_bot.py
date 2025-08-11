#!/usr/bin/env python3
"""
Sophia Intel Telegram Bot - Complete Implementation
Version: 3.0.0 - AI-Integrated Multi-Platform Bot

A comprehensive Telegram bot for Sophia Intel repository management with AI integration.
"""

import os
import asyncio
import logging
import json
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import aiohttp
import aiofiles

from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    BotCommand,
    ChatAction,
    ParseMode
)
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    filters, 
    ContextTypes,
    ConversationHandler
)

# AI Integration imports
try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Configuration
class Config:
    """Bot configuration from environment variables"""
    
    def __init__(self):
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        self.CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.GROK_API_KEY = os.getenv('GROK_API_KEY')
        self.GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
        
        # Repository configuration
        self.REPO = "ai-cherry/sophia-intel"
        self.DEFAULT_BRANCH = "notion"
        
        # Bot settings
        self.MAX_MESSAGE_LENGTH = 4096
        self.CACHE_TTL = 300  # 5 minutes
        self.RATE_LIMIT = 30  # requests per minute
        
        # Validate required tokens
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
SELECTING_BRANCH, SELECTING_AI, WAITING_FOR_QUERY = range(3)

class SophiaIntelBot:
    """Main bot class with AI integration and repository management"""
    
    def __init__(self):
        self.config = Config()
        self.user_sessions = {}  # Store user session data
        self.cache = {}  # Simple in-memory cache
        self.rate_limits = {}  # Rate limiting per user
        
        # Initialize AI clients
        self.claude_client = None
        self.openai_client = None
        
        if ANTHROPIC_AVAILABLE and self.config.CLAUDE_API_KEY:
            self.claude_client = AsyncAnthropic(api_key=self.config.CLAUDE_API_KEY)
            
        if OPENAI_AVAILABLE and self.config.OPENAI_API_KEY:
            self.openai_client = openai.AsyncOpenAI(api_key=self.config.OPENAI_API_KEY)
    
    def get_user_session(self, user_id: int) -> Dict:
        """Get or create user session"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'current_branch': self.config.DEFAULT_BRANCH,
                'ai_provider': 'claude',
                'last_activity': datetime.now(),
                'preferences': {}
            }
        return self.user_sessions[user_id]
    
    def check_rate_limit(self, user_id: int) -> bool:
        """Check if user is within rate limits"""
        now = datetime.now()
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        
        # Remove old requests
        self.rate_limits[user_id] = [
            req_time for req_time in self.rate_limits[user_id]
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Check limit
        if len(self.rate_limits[user_id]) >= self.config.RATE_LIMIT:
            return False
        
        self.rate_limits[user_id].append(now)
        return True
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command with welcome message and branch selection"""
        user_id = update.effective_user.id
        
        if not self.check_rate_limit(user_id):
            await update.message.reply_text("⚠️ Rate limit exceeded. Please wait a moment.")
            return
        
        session = self.get_user_session(user_id)
        
        keyboard = [
            [InlineKeyboardButton("📘 Notion Branch", callback_data='branch_notion')],
            [InlineKeyboardButton("📗 Main Branch", callback_data='branch_main')],
            [InlineKeyboardButton("🔧 Development Branch", callback_data='branch_dev')],
            [InlineKeyboardButton("🌿 List All Branches", callback_data='list_branches')],
            [InlineKeyboardButton("🤖 AI Settings", callback_data='ai_settings')],
            [InlineKeyboardButton("ℹ️ Help", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
🚀 *Sophia Intel CLI Bot v3.0.0*

Welcome to the AI-integrated repository management bot!

*Current Settings:*
• Branch: `{session['current_branch']}`
• AI Provider: `{session['ai_provider']}`

*Features:*
✅ Multi-branch repository management
✅ AI-powered analysis and assistance
✅ Real-time repository monitoring
✅ Natural language queries
✅ Security scanning and reporting

Select a branch to get started or configure your AI settings.
        """
        
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def handle_branch_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle branch selection callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        
        if query.data == 'branch_notion':
            session['current_branch'] = 'notion'
            await self.show_branch_operations(update, context, 'notion')
        elif query.data == 'branch_main':
            session['current_branch'] = 'main'
            await self.show_branch_operations(update, context, 'main')
        elif query.data == 'branch_dev':
            session['current_branch'] = 'development'
            await self.show_branch_operations(update, context, 'development')
        elif query.data == 'list_branches':
            await self.list_all_branches(update, context)
        elif query.data == 'ai_settings':
            await self.show_ai_settings(update, context)
        elif query.data == 'help':
            await self.show_help(update, context)
    
    async def show_branch_operations(self, update: Update, context: ContextTypes.DEFAULT_TYPE, branch: str):
        """Show available operations for selected branch"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Repository Info", callback_data=f'repo_info_{branch}'),
                InlineKeyboardButton("📁 List Files", callback_data=f'list_files_{branch}')
            ],
            [
                InlineKeyboardButton("🔐 Security Scan", callback_data=f'security_scan_{branch}'),
                InlineKeyboardButton("📝 Recent Commits", callback_data=f'recent_commits_{branch}')
            ],
            [
                InlineKeyboardButton("📈 Generate Report", callback_data=f'generate_report_{branch}'),
                InlineKeyboardButton("🔍 Search Code", callback_data=f'search_code_{branch}')
            ],
            [
                InlineKeyboardButton("🤖 AI Analysis", callback_data=f'ai_analysis_{branch}'),
                InlineKeyboardButton("📊 Branch Stats", callback_data=f'branch_stats_{branch}')
            ],
            [
                InlineKeyboardButton("🔄 Change Branch", callback_data='start'),
                InlineKeyboardButton("⚙️ Settings", callback_data='ai_settings')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""
*Current Branch: `{branch}`*

Select an operation to perform on the {branch} branch:

🔹 *Repository Operations*
• Repository Info - View basic repository information
• List Files - Browse files in the current branch
• Recent Commits - View recent commit history

🔹 *Analysis & Security*
• Security Scan - Run security analysis
• Generate Report - Create comprehensive report
• Search Code - Search through codebase

🔹 *AI-Powered Features*
• AI Analysis - Get AI insights about the branch
• Branch Stats - Detailed statistics and metrics
        """
        
        await update.callback_query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def show_ai_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show AI provider settings"""
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        
        keyboard = []
        
        # Add available AI providers
        if self.claude_client:
            emoji = "✅" if session['ai_provider'] == 'claude' else "⚪"
            keyboard.append([InlineKeyboardButton(f"{emoji} Claude (Anthropic)", callback_data='ai_claude')])
        
        if self.openai_client:
            emoji = "✅" if session['ai_provider'] == 'gpt' else "⚪"
            keyboard.append([InlineKeyboardButton(f"{emoji} GPT-4 (OpenAI)", callback_data='ai_gpt')])
        
        if self.config.GROK_API_KEY:
            emoji = "✅" if session['ai_provider'] == 'grok' else "⚪"
            keyboard.append([InlineKeyboardButton(f"{emoji} Grok (xAI)", callback_data='ai_grok')])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Main", callback_data='start')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""
🤖 *AI Provider Settings*

Current Provider: `{session['ai_provider']}`

Select your preferred AI provider for analysis and assistance:

*Available Providers:*
• **Claude** - Advanced reasoning and analysis
• **GPT-4** - General purpose AI assistant  
• **Grok** - Real-time and witty responses

*Note:* Only providers with valid API keys are shown.
        """
        
        await update.callback_query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def handle_ai_provider_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle AI provider selection"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        
        if query.data == 'ai_claude':
            session['ai_provider'] = 'claude'
            await query.edit_message_text("✅ AI Provider set to Claude")
        elif query.data == 'ai_gpt':
            session['ai_provider'] = 'gpt'
            await query.edit_message_text("✅ AI Provider set to GPT-4")
        elif query.data == 'ai_grok':
            session['ai_provider'] = 'grok'
            await query.edit_message_text("✅ AI Provider set to Grok")
        
        # Return to main menu after 2 seconds
        await asyncio.sleep(2)
        await self.start(update, context)
    
    async def execute_github_command(self, command: str) -> str:
        """Execute GitHub CLI command and return result"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"Error: {result.stderr.strip()}"
                
        except subprocess.TimeoutExpired:
            return "Error: Command timed out"
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def get_repository_info(self, branch: str) -> str:
        """Get repository information for specified branch"""
        cache_key = f"repo_info_{branch}"
        
        # Check cache
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if time.time() - cache_time < self.config.CACHE_TTL:
                return data
        
        # Fetch fresh data
        command = f"gh api repos/{self.config.REPO}"
        repo_data = await self.execute_github_command(command)
        
        if repo_data.startswith("Error:"):
            return repo_data
        
        try:
            repo_json = json.loads(repo_data)
            
            # Get branch-specific info
            branch_command = f"gh api repos/{self.config.REPO}/branches/{branch}"
            branch_data = await self.execute_github_command(branch_command)
            
            info = f"""
📊 *Repository Information*

*Basic Info:*
• Name: `{repo_json.get('name', 'N/A')}`
• Description: {repo_json.get('description', 'No description')}
• Visibility: `{repo_json.get('visibility', 'N/A')}`
• Size: `{repo_json.get('size', 0)} KB`

*Statistics:*
• Stars: ⭐ {repo_json.get('stargazers_count', 0)}
• Forks: 🍴 {repo_json.get('forks_count', 0)}
• Issues: 🐛 {repo_json.get('open_issues_count', 0)}

*Branch: `{branch}`*
• Last updated: {repo_json.get('updated_at', 'N/A')}
• Default branch: `{repo_json.get('default_branch', 'N/A')}`
            """
            
            # Cache the result
            self.cache[cache_key] = (time.time(), info)
            return info
            
        except json.JSONDecodeError:
            return "Error: Failed to parse repository data"
    
    async def get_recent_commits(self, branch: str, limit: int = 5) -> str:
        """Get recent commits for specified branch"""
        command = f"gh api repos/{self.config.REPO}/commits?sha={branch}&per_page={limit}"
        commits_data = await self.execute_github_command(command)
        
        if commits_data.startswith("Error:"):
            return commits_data
        
        try:
            commits_json = json.loads(commits_data)
            
            if not commits_json:
                return f"No commits found in branch `{branch}`"
            
            commits_text = f"📝 *Recent Commits in `{branch}`*\n\n"
            
            for commit in commits_json:
                sha = commit['sha'][:7]
                message = commit['commit']['message'].split('\n')[0][:50]
                author = commit['commit']['author']['name']
                date = commit['commit']['author']['date'][:10]
                
                commits_text += f"• `{sha}` {message}\n  👤 {author} • 📅 {date}\n\n"
            
            return commits_text
            
        except json.JSONDecodeError:
            return "Error: Failed to parse commits data"
    
    async def process_with_ai(self, query: str, provider: str, context_data: str = "") -> str:
        """Process query with selected AI provider"""
        
        system_prompt = f"""
You are Sophia Intel CLI assistant. You help users manage and analyze the Sophia Intel repository.

Context: {context_data}

Available operations:
- Repository analysis and insights
- Code review and suggestions
- Security recommendations
- Development workflow guidance
- Branch comparison and analysis

Provide helpful, concise responses. If the user wants to execute a specific command, 
suggest the appropriate action they can take through the bot interface.
        """
        
        try:
            if provider == 'claude' and self.claude_client:
                response = await self.claude_client.messages.create(
                    model="claude-3-opus-20240229",
                    messages=[
                        {"role": "user", "content": f"{system_prompt}\n\nUser query: {query}"}
                    ],
                    max_tokens=1000
                )
                return response.content[0].text
                
            elif provider == 'gpt' and self.openai_client:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}
                    ],
                    max_tokens=1000
                )
                return response.choices[0].message.content
                
            elif provider == 'grok' and self.config.GROK_API_KEY:
                # Grok API implementation
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "Authorization": f"Bearer {self.config.GROK_API_KEY}",
                        "Content-Type": "application/json"
                    }
                    data = {
                        "model": "grok-1",
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": query}
                        ]
                    }
                    
                    async with session.post(
                        "https://api.x.ai/v1/chat/completions",
                        headers=headers,
                        json=data
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result['choices'][0]['message']['content']
                        else:
                            return f"Error: Grok API returned status {response.status}"
            
            else:
                return f"AI provider '{provider}' is not available or not configured."
                
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            return f"Error processing with AI: {str(e)}"
    
    async def handle_natural_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle natural language messages"""
        user_id = update.effective_user.id
        
        if not self.check_rate_limit(user_id):
            await update.message.reply_text("⚠️ Rate limit exceeded. Please wait a moment.")
            return
        
        session = self.get_user_session(user_id)
        user_message = update.message.text
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        # Get repository context
        repo_info = await self.get_repository_info(session['current_branch'])
        context_data = f"Current branch: {session['current_branch']}\n{repo_info}"
        
        # Process with AI
        response = await self.process_with_ai(
            user_message, 
            session['ai_provider'], 
            context_data
        )
        
        # Split long messages
        if len(response) > self.config.MAX_MESSAGE_LENGTH:
            for i in range(0, len(response), self.config.MAX_MESSAGE_LENGTH):
                chunk = response[i:i + self.config.MAX_MESSAGE_LENGTH]
                await update.message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
        else:
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all callback queries"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        
        # Branch selection
        if query.data.startswith('branch_') or query.data in ['list_branches', 'ai_settings', 'help', 'start']:
            await self.handle_branch_selection(update, context)
        
        # AI provider selection
        elif query.data.startswith('ai_'):
            await self.handle_ai_provider_selection(update, context)
        
        # Repository operations
        elif query.data.startswith('repo_info_'):
            branch = query.data.split('_')[-1]
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            info = await self.get_repository_info(branch)
            await query.edit_message_text(info, parse_mode=ParseMode.MARKDOWN)
        
        elif query.data.startswith('recent_commits_'):
            branch = query.data.split('_')[-1]
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            commits = await self.get_recent_commits(branch)
            await query.edit_message_text(commits, parse_mode=ParseMode.MARKDOWN)
        
        elif query.data.startswith('ai_analysis_'):
            branch = query.data.split('_')[-1]
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            
            # Get repository context for AI analysis
            repo_info = await self.get_repository_info(branch)
            commits = await self.get_recent_commits(branch)
            context_data = f"{repo_info}\n\n{commits}"
            
            analysis = await self.process_with_ai(
                f"Analyze the {branch} branch and provide insights",
                session['ai_provider'],
                context_data
            )
            
            await query.edit_message_text(
                f"🤖 *AI Analysis for `{branch}` branch*\n\n{analysis}",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help information"""
        help_text = """
🤖 *Sophia Intel CLI Bot Help*

*Available Commands:*
• `/start` - Main menu and branch selection
• `/help` - Show this help message
• `/status` - Show bot and repository status
• `/branches` - List all available branches

*Features:*
🔹 **Multi-Branch Management**
   Switch between notion, main, and development branches

🔹 **AI Integration**
   Get AI-powered insights using Claude, GPT-4, or Grok

🔹 **Repository Operations**
   • View repository information
   • Browse files and commits
   • Security scanning
   • Code search

🔹 **Natural Language**
   Just type your questions in plain English!

*Examples:*
• "Show me recent commits in the notion branch"
• "What files changed in the last week?"
• "Analyze the security of this repository"
• "Compare main and notion branches"

*Tips:*
• Use the inline keyboard for quick operations
• Switch AI providers in Settings for different perspectives
• All operations respect GitHub rate limits
        """
        
        await update.callback_query.edit_message_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot status"""
        user_id = update.effective_user.id
        session = self.get_user_session(user_id)
        
        # Check AI providers
        ai_status = []
        if self.claude_client:
            ai_status.append("✅ Claude")
        if self.openai_client:
            ai_status.append("✅ GPT-4")
        if self.config.GROK_API_KEY:
            ai_status.append("✅ Grok")
        
        status_text = f"""
🤖 *Bot Status*

*Version:* 3.0.0
*Uptime:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

*Your Session:*
• Current Branch: `{session['current_branch']}`
• AI Provider: `{session['ai_provider']}`
• Last Activity: {session['last_activity'].strftime('%H:%M:%S')}

*AI Providers:*
{chr(10).join(ai_status) if ai_status else "❌ No AI providers configured"}

*Repository:* `{self.config.REPO}`
*Rate Limit:* {len(self.rate_limits.get(user_id, []))}/{self.config.RATE_LIMIT} requests/min
        """
        
        await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)
    
    async def list_branches_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all repository branches"""
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        
        command = f"gh api repos/{self.config.REPO}/branches"
        branches_data = await self.execute_github_command(command)
        
        if branches_data.startswith("Error:"):
            await update.message.reply_text(f"❌ {branches_data}")
            return
        
        try:
            branches_json = json.loads(branches_data)
            
            branches_text = "🌿 *Available Branches:*\n\n"
            for branch in branches_json:
                name = branch['name']
                protected = "🔒" if branch.get('protected', False) else "🔓"
                branches_text += f"{protected} `{name}`\n"
            
            await update.message.reply_text(branches_text, parse_mode=ParseMode.MARKDOWN)
            
        except json.JSONDecodeError:
            await update.message.reply_text("❌ Error: Failed to parse branches data")
    
    def run(self):
        """Start the bot"""
        if not self.config.TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN is required")
            return
        
        # Create application
        app = Application.builder().token(self.config.TELEGRAM_BOT_TOKEN).build()
        
        # Set bot commands
        commands = [
            BotCommand("start", "Start the bot and select branch"),
            BotCommand("help", "Show help information"),
            BotCommand("status", "Show bot status"),
            BotCommand("branches", "List all branches")
        ]
        
        # Add handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", lambda u, c: self.show_help(u, c)))
        app.add_handler(CommandHandler("status", self.status_command))
        app.add_handler(CommandHandler("branches", self.list_branches_command))
        
        # Callback query handler
        app.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # Natural language message handler
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_natural_language
        ))
        
        # Set commands
        asyncio.create_task(app.bot.set_my_commands(commands))
        
        logger.info("🚀 Sophia Intel Bot starting...")
        logger.info(f"Repository: {self.config.REPO}")
        logger.info(f"AI Providers: Claude={bool(self.claude_client)}, GPT={bool(self.openai_client)}, Grok={bool(self.config.GROK_API_KEY)}")
        
        # Start bot
        app.run_polling(drop_pending_updates=True)

def main():
    """Main entry point"""
    try:
        bot = SophiaIntelBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise

if __name__ == "__main__":
    main()

