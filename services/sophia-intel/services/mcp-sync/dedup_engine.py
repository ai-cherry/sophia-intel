#!/usr/bin/env python3
"""
Content Deduplication Engine for Sophia Intel
"""

import hashlib
import json
import re
from typing import List, Dict, Tuple
from difflib import SequenceMatcher
import numpy as np
from datetime import datetime, timedelta

class DeduplicationEngine:
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
        self.content_index = {}
        self.metadata_index = {}
        
    def generate_content_hash(self, content: str) -> str:
        """Generate SHA-256 hash of content"""
        normalized = self.normalize_content(content)
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def normalize_content(self, content: str) -> str:
        """Normalize content for comparison"""
        content = re.sub(r'\s+', ' ', content)
        content = content.lower().strip()
        content = re.sub(r'\d{4}-\d{2}-\d{2}', '', content)
        content = re.sub(r'\d{2}:\d{2}:\d{2}', '', content)
        return content
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        norm1 = self.normalize_content(text1)
        norm2 = self.normalize_content(text2)
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def find_duplicates(self, new_content: str, existing_contents: List[Dict]) -> List[Tuple[str, float]]:
        """Find potential duplicates of new content"""
        duplicates = []
        new_hash = self.generate_content_hash(new_content)
        
        for existing in existing_contents:
            existing_hash = existing.get('hash', self.generate_content_hash(existing['content']))
            
            if new_hash == existing_hash:
                duplicates.append((existing['id'], 1.0))
                continue
            
            similarity = self.calculate_text_similarity(new_content, existing['content'])
            
            if similarity >= self.similarity_threshold:
                duplicates.append((existing['id'], similarity))
        
        return sorted(duplicates, key=lambda x: x[1], reverse=True)
    
    def generate_dedup_report(self, contents: List[Dict]) -> Dict:
        """Generate a deduplication report"""
        total_content = len(contents)
        unique_hashes = set()
        duplicates_found = []
        
        for i, content in enumerate(contents):
            content_hash = self.generate_content_hash(content.get('content', ''))
            
            if content_hash in unique_hashes:
                duplicates_found.append({
                    'index': i,
                    'id': content.get('id'),
                    'hash': content_hash
                })
            else:
                unique_hashes.add(content_hash)
        
        duplicate_count = len(duplicates_found)
        dedup_ratio = (duplicate_count / total_content * 100) if total_content > 0 else 0
        
        return {
            'total_items': total_content,
            'unique_items': len(unique_hashes),
            'duplicates': duplicate_count,
            'deduplication_ratio': f'{dedup_ratio:.2f}%',
            'duplicate_details': duplicates_found[:10],
            'recommendation': self.generate_recommendation(dedup_ratio)
        }
    
    def generate_recommendation(self, dedup_ratio: float) -> str:
        """Generate recommendation based on deduplication ratio"""
        if dedup_ratio < 5:
            return "Content is well-managed with minimal duplicates."
        elif dedup_ratio < 15:
            return "Some duplicates found. Consider running periodic deduplication."
        elif dedup_ratio < 30:
            return "Significant duplicates detected. Deduplication recommended."
        else:
            return "High duplicate ratio. Immediate deduplication strongly recommended."

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Content Deduplication Engine')
    parser.add_argument('--check-duplicates', action='store_true')
    parser.add_argument('--threshold', type=float, default=0.8)
    parser.add_argument('--input-file', type=str, default='sync_state.json')
    
    args = parser.parse_args()
    
    engine = DeduplicationEngine(similarity_threshold=args.threshold)
    
    if args.check_duplicates and args.input_file:
        try:
            with open(args.input_file, 'r') as f:
                data = json.load(f)
                contents = [{'content': v, 'id': k} for k, v in data.get('content_hashes', {}).items()]
            
            report = engine.generate_dedup_report(contents)
            print(json.dumps(report, indent=2))
        except Exception as e:
            print(f"Error: {e}")
