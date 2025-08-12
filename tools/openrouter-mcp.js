#!/usr/bin/env node
/**
 * OpenRouter MCP Server - Multi-Model Swarm for Claude Code
 * Provides specialized tools that route to best-in-class models via OpenRouter
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import fs from 'fs/promises';
import path from 'path';
import fetch from 'node-fetch';

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
const OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1/chat/completions';

// Load config
const CONFIG_PATH = path.join(process.cwd(), '.claude', 'openrouter-config.json');
let config = {
  tools: {
    plan: {
      models: ["anthropic/claude-3-opus-20240229", "deepseek/deepseek-chat"],
      max_tokens: 4096,
      temperature: 0.7
    },
    code_special: {
      models: ["qwen/qwen-2.5-coder-32b-instruct", "mistralai/mistral-nemo"],
      max_tokens: 4096,
      temperature: 0.3
    },
    challenge: {
      models: ["x-ai/grok-beta", "openai/gpt-4-turbo-preview"],
      max_tokens: 4096,
      temperature: 0.8
    },
    qa_test: {
      models: ["google/gemini-2.0-flash-exp", "anthropic/claude-3-haiku-20240307"],
      max_tokens: 4096,
      temperature: 0.4
    },
    doc_review: {
      models: ["google/gemini-2.0-flash-exp"],
      max_tokens: 4096,
      temperature: 0.5
    }
  }
};

// Try to load custom config
try {
  const customConfig = await fs.readFile(CONFIG_PATH, 'utf-8');
  config = JSON.parse(customConfig);
} catch (err) {
  console.error('Using default config. Create .claude/openrouter-config.json to customize.');
}

// Helper to call OpenRouter with fallback
async function callOpenRouter(toolConfig, messages, systemPrompt) {
  const errors = [];
  
  for (const model of toolConfig.models) {
    try {
      const response = await fetch(OPENROUTER_BASE_URL, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
          'Content-Type': 'application/json',
          'HTTP-Referer': 'http://localhost:3000',
          'X-Title': 'Claude Code Swarm'
        },
        body: JSON.stringify({
          model,
          messages: [
            { role: 'system', content: systemPrompt },
            ...messages
          ],
          max_tokens: toolConfig.max_tokens || 4096,
          temperature: toolConfig.temperature || 0.5
        })
      });

      if (!response.ok) {
        throw new Error(`${model} returned ${response.status}`);
      }

      const data = await response.json();
      return {
        model,
        content: data.choices[0].message.content
      };
    } catch (err) {
      errors.push(`${model}: ${err.message}`);
      continue; // Try next model
    }
  }
  
  throw new Error(`All models failed: ${errors.join(', ')}`);
}

// Create MCP server
const server = new Server(
  {
    name: 'openrouter-swarm',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Tool definitions
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'plan',
      description: 'Deep reasoning planner for architecture and migration strategies',
      inputSchema: {
        type: 'object',
        properties: {
          goal: { type: 'string', description: 'What to accomplish' },
          context: { type: 'string', description: 'Current state/files/constraints' },
          deliverables: {
            type: 'array',
            items: { type: 'string' },
            description: 'Expected outputs (plan, risks, etc)'
          }
        },
        required: ['goal']
      }
    },
    {
      name: 'code_special',
      description: 'Specialized coding tasks (tests, docs, refactoring)',
      inputSchema: {
        type: 'object',
        properties: {
          target: {
            type: 'array',
            items: { type: 'string' },
            description: 'Files or functions to target'
          },
          task: { type: 'string', description: 'Specific coding task' },
          style: { type: 'string', description: 'Code style preferences' }
        },
        required: ['target', 'task']
      }
    },
    {
      name: 'challenge',
      description: 'Review code and challenge assumptions, find bugs',
      inputSchema: {
        type: 'object',
        properties: {
          diff: { type: 'string', description: 'Code diff or changes to review' },
          focus: {
            type: 'array',
            items: { type: 'string' },
            description: 'Areas to focus on (security, performance, etc)'
          }
        },
        required: ['diff']
      }
    },
    {
      name: 'qa_test',
      description: 'Generate comprehensive test cases and testing strategies',
      inputSchema: {
        type: 'object',
        properties: {
          target: { type: 'string', description: 'Code to test' },
          testing_policy: { type: 'string', description: 'Testing framework and coverage goals' },
          existing_tests: { type: 'string', description: 'Current test suite context' }
        },
        required: ['target']
      }
    },
    {
      name: 'doc_review',
      description: 'Review documentation, diagrams, or UI (multimodal when available)',
      inputSchema: {
        type: 'object',
        properties: {
          input: { type: 'string', description: 'Document/diagram path or content' },
          request: { type: 'string', description: 'What to review or validate' }
        },
        required: ['input', 'request']
      }
    }
  ]
}));

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  try {
    let result;
    
    switch (name) {
      case 'plan':
        result = await callOpenRouter(
          config.tools.plan,
          [{ role: 'user', content: `Goal: ${args.goal}\n\nContext: ${args.context || 'N/A'}\n\nDeliverables: ${(args.deliverables || ['step-by-step plan']).join(', ')}` }],
          'You are an expert software architect and migration planner. Provide a detailed, actionable plan with clear steps, risks, and success criteria. Format as structured JSON when possible.'
        );
        break;
        
      case 'code_special':
        result = await callOpenRouter(
          config.tools.code_special,
          [{ role: 'user', content: `Target files: ${args.target.join(', ')}\n\nTask: ${args.task}\n\nStyle preferences: ${args.style || 'Clean, documented, type-safe'}` }],
          'You are a specialized coder focused on clean, production-ready code. Generate complete, working code with proper error handling, types, and documentation.'
        );
        break;
        
      case 'challenge':
        result = await callOpenRouter(
          config.tools.challenge,
          [{ role: 'user', content: `Code diff to review:\n\n${args.diff}\n\nFocus areas: ${(args.focus || ['general quality']).join(', ')}` }],
          'You are a senior code reviewer. Challenge assumptions, find bugs, identify edge cases, and suggest improvements. Be constructive but thorough.'
        );
        break;
        
      case 'qa_test':
        result = await callOpenRouter(
          config.tools.qa_test,
          [{ role: 'user', content: `Code to test:\n\n${args.target}\n\nTesting policy: ${args.testing_policy || 'comprehensive unit tests'}\n\nExisting tests: ${args.existing_tests || 'None'}` }],
          'You are a QA engineer. Generate comprehensive test cases covering happy paths, edge cases, error conditions, and performance scenarios. Use the specified testing framework.'
        );
        break;
        
      case 'doc_review':
        result = await callOpenRouter(
          config.tools.doc_review,
          [{ role: 'user', content: `Input: ${args.input}\n\nReview request: ${args.request}` }],
          'You are a technical documentation expert. Review for accuracy, completeness, clarity, and alignment with implementation.'
        );
        break;
        
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
    
    return {
      content: [
        {
          type: 'text',
          text: `[Model: ${result.model}]\n\n${result.content}`
        }
      ]
    };
    
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`
        }
      ],
      isError: true
    };
  }
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
console.error('OpenRouter MCP Server running');
