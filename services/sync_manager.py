#!/usr/bin/env python3
"""
MCP-Notion Sync Manager for Sophia Intel
Handles intelligent synchronization between GitHub, Lambda Labs, and Notion
"""

import os
import json
import hashlib
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import aiohttp
from notion_client import AsyncClient as NotionClient
from github import Github
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SophiaIntelSyncManager:
    def __init__(self):
        """Initialize sync manager with API credentials"""
        # Lambda Labs config
        self.lambda_api_key = os.getenv('LAMBDA_CLOUD_API_KEY')
        self.lambda_endpoint = os.getenv('LAMBDA_API_CLOUD_ENDPOINT', 'https://cloud.lambda.ai/api/v1')
        
        # GitHub config
        self.github_token = os.getenv('GH_FINE_GRAINED_TOKEN')
        self.github_username = os.getenv('GH_USERNAME', 'scoobyjava')
        self.github = Github(self.github_token)
        self.repo = self.github.get_repo('ai-cherry/sophia-intel')
        
        # Notion config
        self.notion = NotionClient(auth=os.getenv('NOTION_API_KEY'))
        self.notion_workspace_id = os.getenv('NOTION_WORKSPACE_ID')
        
        # Sync state
        self.sync_state_file = 'sync_state.json'
        self.sync_state = self.load_sync_state()
        
    def load_sync_state(self) -> Dict:
        """Load sync state from file"""
        if os.path.exists(self.sync_state_file):
            with open(self.sync_state_file, 'r') as f:
                return json.load(f)
        return {
            'last_sync': None,
            'content_hashes': {},
            'notion_mappings': {},
            'github_mappings': {},
            'dedup_stats': {
                'total_processed': 0,
                'duplicates_prevented': 0,
                'content_merged': 0
            }
        }
    
    def save_sync_state(self):
        """Save sync state to file"""
        with open(self.sync_state_file, 'w') as f:
            json.dump(self.sync_state, f, indent=2, default=str)
    
    async def compute_embedding_lambda(self, text: str) -> np.ndarray:
        """Use Lambda Labs GPU to compute text embeddings"""
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {self.lambda_api_key}',
                'Content-Type': 'application/json'
            }
            
            # Request embedding computation on Lambda GPU
            payload = {
                'model': 'sentence-transformers/all-MiniLM-L6-v2',
                'text': text,
                'gpu_required': True
            }
            
            try:
                async with session.post(
                    f'{self.lambda_endpoint}/embeddings',
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return np.array(data['embedding'])
                    else:
                        logger.error(f'Lambda API error: {response.status}')
                        return self.compute_local_embedding(text)
            except Exception as e:
                logger.error(f'Lambda API exception: {e}')
                return self.compute_local_embedding(text)
    
    def compute_local_embedding(self, text: str) -> np.ndarray:
        """Fallback local embedding computation"""
        # Simple hash-based embedding for fallback
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        # Convert to normalized vector
        embedding = np.frombuffer(hash_bytes, dtype=np.uint8).astype(np.float32)
        embedding = embedding[:384]  # Truncate to standard size
        embedding = embedding / np.linalg.norm(embedding)
        return embedding
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings"""
        return float(np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2)))
    
    async def should_update_content(self, new_content: str, existing_content: str) -> Tuple[bool, float]:
        """
        Determine if content should be updated based on semantic similarity
        Returns: (should_update, similarity_score)
        """
        # Quick hash check first
        new_hash = hashlib.sha256(new_content.encode()).hexdigest()
        existing_hash = hashlib.sha256(existing_content.encode()).hexdigest()
        
        if new_hash == existing_hash:
            self.sync_state['dedup_stats']['duplicates_prevented'] += 1
            return False, 1.0
        
        # Compute semantic similarity using Lambda GPU
        new_embedding = await self.compute_embedding_lambda(new_content)
        existing_embedding = await self.compute_embedding_lambda(existing_content)
        
        similarity = self.calculate_similarity(new_embedding, existing_embedding)
        
        # Update if similarity is less than 80% (significant changes)
        should_update = similarity < 0.8
        
        if not should_update:
            self.sync_state['dedup_stats']['duplicates_prevented'] += 1
        else:
            self.sync_state['dedup_stats']['content_merged'] += 1
        
        return should_update, similarity
    
    async def sync_github_to_notion(self):
        """Sync GitHub content to Notion with deduplication"""
        logger.info('Starting GitHub to Notion sync for sophia-intel...')
        
        # Get files from the branch
        try:
            contents = self.repo.get_contents('', ref='mcp-notion-sync')
        except:
            # If branch doesn't exist, use main
            contents = self.repo.get_contents('')
        
        processed_count = 0
        
        for content_file in contents:
            if content_file.type == 'file' and content_file.path.endswith(('.md', '.py', '.json', '.yaml', '.yml')):
                file_content = content_file.decoded_content.decode('utf-8')
                file_hash = hashlib.sha256(file_content.encode()).hexdigest()
                
                processed_count += 1
                self.sync_state['dedup_stats']['total_processed'] += 1
                
                # Check if content already exists in Notion
                notion_page_id = self.sync_state['notion_mappings'].get(content_file.path)
                
                if notion_page_id:
                    # Check if update is needed
                    try:
                        page = await self.notion.pages.retrieve(notion_page_id)
                        # Extract existing content (simplified)
                        existing_content = str(page)
                        
                        should_update, similarity = await self.should_update_content(
                            file_content, existing_content
                        )
                        
                        if should_update:
                            logger.info(f'Updating {content_file.path} (similarity: {similarity:.2%})')
                            await self.update_notion_page(notion_page_id, file_content, content_file.path)
                        else:
                            logger.info(f'Skipping duplicate: {content_file.path} (similarity: {similarity:.2%})')
                    except Exception as e:
                        logger.error(f'Error processing {content_file.path}: {e}')
                else:
                    # Create new page
                    logger.info(f'Creating new page for {content_file.path}')
                    notion_page_id = await self.create_notion_page(file_content, content_file.path)
                    self.sync_state['notion_mappings'][content_file.path] = notion_page_id
                
                # Update content hash
                self.sync_state['content_hashes'][content_file.path] = file_hash
        
        self.sync_state['last_sync'] = datetime.now().isoformat()
        self.save_sync_state()
        
        logger.info(f'GitHub to Notion sync complete. Processed: {processed_count} files')
        logger.info(f'Deduplication stats: {json.dumps(self.sync_state["dedup_stats"], indent=2)}')
    
    async def create_notion_page(self, content: str, file_path: str) -> str:
        """Create a new Notion page"""
        # This is a simplified version - real implementation would handle Notion blocks properly
        response = await self.notion.pages.create(
            parent={'database_id': self.notion_workspace_id},
            properties={
                'title': {
                    'title': [{
                        'type': 'text',
                        'text': {'content': f'[sophia-intel] {file_path}'}
                    }]
                },
                'Source': {
                    'select': {'name': 'GitHub'}
                },
                'Repository': {
                    'select': {'name': 'sophia-intel'}
                },
                'Last Updated': {
                    'date': {'start': datetime.now().isoformat()}
                }
            },
            children=[
                {
                    'object': 'block',
                    'type': 'code',
                    'code': {
                        'rich_text': [{
                            'type': 'text',
                            'text': {'content': content[:2000]}  # Notion has limits
                        }],
                        'language': 'python' if file_path.endswith('.py') else 'markdown'
                    }
                }
            ]
        )
        return response['id']
    
    async def update_notion_page(self, page_id: str, content: str, file_path: str):
        """Update existing Notion page"""
        await self.notion.pages.update(
            page_id,
            properties={
                'Last Updated': {
                    'date': {'start': datetime.now().isoformat()}
                }
            }
        )
        # Note: Updating blocks requires additional API calls
    
    async def generate_dedup_report(self):
        """Generate deduplication report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'repository': 'sophia-intel',
            'branch': 'mcp-notion-sync',
            'stats': self.sync_state['dedup_stats'],
            'efficiency': {
                'dedup_rate': f"{(self.sync_state['dedup_stats']['duplicates_prevented'] / max(self.sync_state['dedup_stats']['total_processed'], 1) * 100):.2f}%",
                'merge_rate': f"{(self.sync_state['dedup_stats']['content_merged'] / max(self.sync_state['dedup_stats']['total_processed'], 1) * 100):.2f}%"
            },
            'last_sync': self.sync_state.get('last_sync'),
            'notion_pages': len(self.sync_state['notion_mappings'])
        }
        
        logger.info(f'Deduplication Report:\n{json.dumps(report, indent=2)}')
        
        # Save report to file
        with open('dedup_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    async def run_sync_cycle(self):
        """Run a complete sync cycle"""
        logger.info('Starting sync cycle for sophia-intel...')
        
        try:
            # 1. Sync GitHub to Notion with deduplication
            await self.sync_github_to_notion()
            
            # 2. Generate deduplication report
            await self.generate_dedup_report()
            
            logger.info('Sync cycle complete')
            
        except Exception as e:
            logger.error(f'Sync cycle failed: {e}')
            raise

async def main():
    """Main entry point"""
    manager = SophiaIntelSyncManager()
    
    # Run sync cycle
    await manager.run_sync_cycle()
    
    # Optional: Set up periodic sync
    # while True:
    #     await manager.run_sync_cycle()
    #     await asyncio.sleep(300)  # Sync every 5 minutes

if __name__ == '__main__':
    asyncio.run(main())
