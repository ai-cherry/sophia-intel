#!/usr/bin/env node
/**
 * OpenRouter MCP Server - Multi-Model Swarm
 * Using WORKING models available on OpenRouter
 */

import https from 'https';
import readline from 'readline';

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || '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';
const OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1/chat/completions';

// WORKING Model configurations - tested on OpenRouter
const config = {
  tools: {
    plan: {
      models: [
        "anthropic/claude-3-opus",               // Claude 3 Opus (works)
        "deepseek/deepseek-chat",               // DeepSeek Chat (works)
        "anthropic/claude-3-sonnet",            // Claude 3 Sonnet fallback
        "openai/gpt-4-turbo-preview"            // GPT-4 Turbo
      ],
      max_tokens: 4096,
      temperature: 0.7,
      systemPrompt: 'You are an expert software architect. Provide detailed, actionable plans with clear steps, risks, and success criteria.'
    },
    code_special: {
      models: [
        "deepseek/deepseek-coder",              // DeepSeek Coder (works)
        "anthropic/claude-3-sonnet",            // Claude 3 Sonnet (works)
        "mistralai/mistral-large",              // Mistral Large (works)
        "openai/gpt-4-turbo-preview"            // GPT-4 Turbo
      ],
      max_tokens: 4096,
      temperature: 0.3,
      systemPrompt: 'You are a specialized coder. Generate complete, working code with proper error handling, types, and documentation.'
    },
    challenge: {
      models: [
        "openai/gpt-4-turbo-preview",           // GPT-4 Turbo (works)
        "anthropic/claude-3-opus",              // Claude 3 Opus
        "mistralai/mistral-large",              // Mistral Large
        "deepseek/deepseek-chat"                // DeepSeek
      ],
      max_tokens: 4096,
      temperature: 0.8,
      systemPrompt: 'You are a senior code reviewer. Challenge assumptions, find bugs, identify edge cases, and suggest improvements.'
    },
    qa_test: {
      models: [
        "openai/gpt-4-turbo-preview",           // GPT-4 Turbo
        "anthropic/claude-3-haiku",             // Claude 3 Haiku (fast)
        "google/gemini-pro",                    // Gemini Pro
        "mistralai/mistral-medium"              // Mistral Medium
      ],
      max_tokens: 4096,
      temperature: 0.4,
      systemPrompt: 'You are a QA engineer. Generate comprehensive test cases covering all scenarios.'
    },
    doc_review: {
      models: [
        "anthropic/claude-3-sonnet",            // Claude 3 Sonnet
        "openai/gpt-4-turbo-preview",           // GPT-4 Turbo
        "google/gemini-pro",                    // Gemini Pro
        "mistralai/mistral-large"               // Mistral Large
      ],
      max_tokens: 4096,
      temperature: 0.5,
      systemPrompt: 'You are a technical documentation expert. Review for accuracy, completeness, and alignment.'
    }
  }
};

// Helper to call OpenRouter with better error handling
async function callOpenRouter(toolConfig, userContent) {
  const errors = [];
  
  for (const model of toolConfig.models) {
    try {
      console.log(`  🔄 Trying ${model}...`);
      const response = await new Promise((resolve, reject) => {
        const data = JSON.stringify({
          model,
          messages: [
            { role: 'system', content: toolConfig.systemPrompt },
            { role: 'user', content: userContent }
          ],
          max_tokens: toolConfig.max_tokens,
          temperature: toolConfig.temperature
        });

        const options = {
          hostname: 'openrouter.ai',
          path: '/api/v1/chat/completions',
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:3000',
            'X-Title': 'Sophia Intel Swarm',
            'Content-Length': data.length
          }
        };

        const req = https.request(options, (res) => {
          let body = '';
          res.on('data', (chunk) => body += chunk);
          res.on('end', () => {
            if (res.statusCode === 200) {
              try {
                const parsed = JSON.parse(body);
                console.log(`  ✅ Success with ${model}`);
                resolve({
                  model,
                  content: parsed.choices[0].message.content
                });
              } catch (e) {
                reject(new Error(`Failed to parse response: ${e.message}`));
              }
            } else {
              const errorBody = body.length > 200 ? body.substring(0, 200) + '...' : body;
              reject(new Error(`HTTP ${res.statusCode}: ${errorBody}`));
            }
          });
        });

        req.on('error', reject);
        req.write(data);
        req.end();
      });

      return response;
    } catch (err) {
      const shortError = err.message.length > 100 ? err.message.substring(0, 100) + '...' : err.message;
      errors.push(`${model}: ${shortError}`);
      console.log(`  ❌ ${model} failed: ${shortError}`);
      continue;
    }
  }
  
  throw new Error(`All models failed:\n${errors.join('\n')}`);
}

// Process commands
async function processCommand(command) {
  const parts = command.trim().split(' ');
  const tool = parts[0];
  const args = parts.slice(1).join(' ');

  if (!config.tools[tool]) {
    console.log(`Unknown tool: ${tool}. Available: ${Object.keys(config.tools).join(', ')}`);
    return;
  }

  console.log(`\n🚀 Calling ${tool}...\n`);
  
  try {
    const result = await callOpenRouter(config.tools[tool], args);
    console.log(`\n✅ Response from [${result.model}]\n`);
    console.log('─'.repeat(80));
    console.log(result.content);
    console.log('─'.repeat(80) + '\n');
  } catch (error) {
    console.error(`\n❌ Error: ${error.message}\n`);
  }
}

// Main CLI interface
console.log(`
╔══════════════════════════════════════════════════════════════════╗
║         🎯 SOPHIA INTEL SWARM - WORKING MODELS                  ║
║         Claude 3 | GPT-4 Turbo | DeepSeek | Mistral             ║
╚══════════════════════════════════════════════════════════════════╝

Available commands:
  plan <goal>         - Architecture (Claude Opus, DeepSeek)
  code_special <task> - Coding (DeepSeek Coder, Claude Sonnet)
  challenge <code>    - Review (GPT-4 Turbo, Claude Opus)
  qa_test <code>      - Testing (GPT-4, Claude Haiku, Gemini)
  doc_review <doc>    - Documentation (Claude Sonnet, GPT-4)
  exit                - Quit

Type a command and press Enter:
`);

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: '> '
});

rl.prompt();

rl.on('line', async (line) => {
  if (line.trim() === 'exit') {
    rl.close();
  } else if (line.trim()) {
    await processCommand(line);
    rl.prompt();
  } else {
    rl.prompt();
  }
});

rl.on('close', () => {
  console.log('\n👋 Goodbye!\n');
  process.exit(0);
});
