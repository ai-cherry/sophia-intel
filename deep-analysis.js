#!/usr/bin/env node
/**
 * Deep Repository Analysis using Perfect Swarm
 * Comprehensive analysis using all specialized models
 */

import https from 'https';
import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import readline from 'readline';

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || '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';

// Model configurations for deep analysis
const analysisModels = {
  architecture: {
    model: "anthropic/claude-3-opus-20240229",
    systemPrompt: "You are an expert software architect. Analyze the codebase structure, patterns, dependencies, and provide insights on architecture quality, technical debt, and improvement opportunities.",
    temperature: 0.7
  },
  codeQuality: {
    model: "qwen/qwen-2.5-coder-32b-instruct",
    systemPrompt: "You are a code quality expert. Analyze code for patterns, anti-patterns, code smells, duplication, complexity, and suggest refactoring opportunities.",
    temperature: 0.3
  },
  security: {
    model: "x-ai/grok-beta",
    systemPrompt: "You are a security expert. Identify security vulnerabilities, potential attack vectors, exposed secrets, insecure dependencies, and OWASP top 10 issues.",
    temperature: 0.5
  },
  performance: {
    model: "google/gemini-2.0-flash-exp",
    systemPrompt: "You are a performance optimization expert. Identify bottlenecks, inefficient algorithms, memory leaks, unnecessary computations, and optimization opportunities.",
    temperature: 0.4
  },
  testing: {
    model: "anthropic/claude-3-haiku-20240307",
    systemPrompt: "You are a QA expert. Analyze test coverage, identify untested code paths, suggest missing test cases, and evaluate testing strategies.",
    temperature: 0.4
  },
  documentation: {
    model: "mistralai/mistral-nemo",
    systemPrompt: "You are a documentation expert. Evaluate documentation completeness, identify undocumented APIs, assess README quality, and suggest documentation improvements.",
    temperature: 0.5
  },
  dependencies: {
    model: "deepseek/deepseek-chat",
    systemPrompt: "You are a dependency management expert. Analyze dependencies for vulnerabilities, version conflicts, unnecessary packages, and optimization opportunities.",
    temperature: 0.3
  },
  bestPractices: {
    model: "openai/gpt-4-turbo-preview",
    systemPrompt: "You are a best practices expert. Evaluate adherence to SOLID principles, design patterns, coding standards, and industry best practices.",
    temperature: 0.5
  }
};

// Gather repository information
function gatherRepoInfo() {
  console.log("📊 Gathering repository information...\n");
  
  const repoInfo = {
    path: process.cwd(),
    files: [],
    structure: {},
    stats: {},
    gitInfo: {}
  };

  // Get file structure
  function walkDir(dir, relativePath = '') {
    const files = fs.readdirSync(dir);
    const result = [];
    
    for (const file of files) {
      if (file.startsWith('.') && !file.includes('.env')) continue;
      if (['node_modules', 'venv', '__pycache__', 'dist', 'build'].includes(file)) continue;
      
      const fullPath = path.join(dir, file);
      const relPath = path.join(relativePath, file);
      const stats = fs.statSync(fullPath);
      
      if (stats.isDirectory()) {
        result.push({
          name: file,
          type: 'directory',
          path: relPath,
          children: walkDir(fullPath, relPath)
        });
      } else {
        const ext = path.extname(file);
        if (['.js', '.ts', '.py', '.jsx', '.tsx', '.json', '.yaml', '.yml', '.md'].includes(ext)) {
          result.push({
            name: file,
            type: 'file',
            path: relPath,
            extension: ext,
            size: stats.size
          });
          repoInfo.files.push(relPath);
        }
      }
    }
    return result;
  }

  repoInfo.structure = walkDir(repoInfo.path);

  // Get Git information
  try {
    repoInfo.gitInfo.branch = execSync('git branch --show-current', { encoding: 'utf8' }).trim();
    repoInfo.gitInfo.lastCommit = execSync('git log -1 --pretty=format:"%h - %s"', { encoding: 'utf8' }).trim();
    repoInfo.gitInfo.uncommittedChanges = execSync('git status --short', { encoding: 'utf8' }).trim().split('\n').length - 1;
    repoInfo.gitInfo.branches = execSync('git branch -a', { encoding: 'utf8' }).trim().split('\n').map(b => b.trim());
  } catch (e) {
    console.log("⚠️  Git information not available");
  }

  // Count file types
  const fileTypes = {};
  repoInfo.files.forEach(file => {
    const ext = path.extname(file) || 'no-ext';
    fileTypes[ext] = (fileTypes[ext] || 0) + 1;
  });
  repoInfo.stats.fileTypes = fileTypes;
  repoInfo.stats.totalFiles = repoInfo.files.length;

  // Read key files
  const keyFiles = ['package.json', 'requirements.txt', 'README.md', '.env.example', 'docker-compose.yml'];
  repoInfo.keyFiles = {};
  
  keyFiles.forEach(file => {
    if (fs.existsSync(file)) {
      try {
        repoInfo.keyFiles[file] = fs.readFileSync(file, 'utf8').substring(0, 1000);
      } catch (e) {}
    }
  });

  // Sample code from main directories
  const codeSamples = {};
  const dirs = ['src', 'app', 'lib', 'components', 'services', 'mcp_servers', 'agents'];
  
  for (const dir of dirs) {
    if (fs.existsSync(dir)) {
      const files = fs.readdirSync(dir);
      const codeFile = files.find(f => ['.js', '.ts', '.py'].includes(path.extname(f)));
      if (codeFile) {
        try {
          codeSamples[`${dir}/${codeFile}`] = fs.readFileSync(path.join(dir, codeFile), 'utf8').substring(0, 500);
        } catch (e) {}
      }
    }
  }
  repoInfo.codeSamples = codeSamples;

  return repoInfo;
}

// Call OpenRouter API
async function callOpenRouter(model, systemPrompt, userContent, maxTokens = 4096) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userContent }
      ],
      max_tokens: maxTokens,
      temperature: 0.5
    });

    const options = {
      hostname: 'openrouter.ai',
      path: '/api/v1/chat/completions',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'http://localhost:3000',
        'X-Title': 'Repository Analysis',
        'Content-Length': data.length
      }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          const parsed = JSON.parse(body);
          resolve(parsed.choices[0].message.content);
        } else {
          reject(new Error(`${model} returned ${res.statusCode}`));
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// Perform deep analysis
async function performDeepAnalysis() {
  console.log(`
╔══════════════════════════════════════════════════════════════════╗
║           🔍 DEEP REPOSITORY ANALYSIS - PERFECT SWARM           ║
╚══════════════════════════════════════════════════════════════════╝
`);

  const repoInfo = gatherRepoInfo();
  
  console.log(`📁 Repository: ${repoInfo.path}`);
  console.log(`📊 Total files: ${repoInfo.stats.totalFiles}`);
  console.log(`🌳 Current branch: ${repoInfo.gitInfo.branch || 'unknown'}`);
  console.log(`📝 Uncommitted changes: ${repoInfo.gitInfo.uncommittedChanges || 0}\n`);

  // Prepare context for analysis
  const context = `
Repository Structure:
${JSON.stringify(repoInfo.structure, null, 2).substring(0, 3000)}

File Statistics:
${JSON.stringify(repoInfo.stats, null, 2)}

Key Files:
${JSON.stringify(Object.keys(repoInfo.keyFiles), null, 2)}

Sample package.json:
${repoInfo.keyFiles['package.json'] || 'Not found'}

Code Samples:
${Object.entries(repoInfo.codeSamples).map(([file, code]) => `\n--- ${file} ---\n${code}`).join('\n').substring(0, 2000)}

Git Branches:
${repoInfo.gitInfo.branches?.join('\n') || 'Not available'}
`;

  const analyses = {};
  const analysisOrder = [
    'architecture',
    'codeQuality',
    'security',
    'performance',
    'testing',
    'documentation',
    'dependencies',
    'bestPractices'
  ];

  // Run analyses sequentially
  for (const analysisType of analysisOrder) {
    const config = analysisModels[analysisType];
    console.log(`\n🔄 Running ${analysisType} analysis with ${config.model}...`);
    
    try {
      const result = await callOpenRouter(
        config.model,
        config.systemPrompt,
        `Analyze this repository and provide specific, actionable insights:\n\n${context}`,
        4096
      );
      analyses[analysisType] = result;
      console.log(`✅ ${analysisType} analysis complete`);
    } catch (error) {
      console.log(`❌ ${analysisType} analysis failed: ${error.message}`);
      analyses[analysisType] = "Analysis failed";
    }
  }

  // Generate comprehensive report
  generateReport(repoInfo, analyses);
}

// Generate markdown report
function generateReport(repoInfo, analyses) {
  const timestamp = new Date().toISOString();
  const reportName = `deep-analysis-${Date.now()}.md`;
  
  let report = `# 🔍 Deep Repository Analysis Report
  
**Generated:** ${timestamp}  
**Repository:** ${repoInfo.path}  
**Branch:** ${repoInfo.gitInfo.branch || 'unknown'}  
**Files Analyzed:** ${repoInfo.stats.totalFiles}  

## 📊 Repository Overview

### File Distribution
${Object.entries(repoInfo.stats.fileTypes).map(([ext, count]) => `- **${ext}**: ${count} files`).join('\n')}

### Git Status
- Current Branch: ${repoInfo.gitInfo.branch}
- Last Commit: ${repoInfo.gitInfo.lastCommit}
- Uncommitted Changes: ${repoInfo.gitInfo.uncommittedChanges}

---

## 🏗️ Architecture Analysis
*Model: Claude Opus 4.1*

${analyses.architecture || 'Analysis pending...'}

---

## 💻 Code Quality Analysis
*Model: Qwen Coder 32B*

${analyses.codeQuality || 'Analysis pending...'}

---

## 🔐 Security Analysis
*Model: Grok 4*

${analyses.security || 'Analysis pending...'}

---

## ⚡ Performance Analysis
*Model: Gemini 2.5 Flash*

${analyses.performance || 'Analysis pending...'}

---

## 🧪 Testing Analysis
*Model: Claude Haiku*

${analyses.testing || 'Analysis pending...'}

---

## 📚 Documentation Analysis
*Model: Mistral Nemo*

${analyses.documentation || 'Analysis pending...'}

---

## 📦 Dependencies Analysis
*Model: DeepSeek Chat*

${analyses.dependencies || 'Analysis pending...'}

---

## ✨ Best Practices Analysis
*Model: GPT-4 Turbo*

${analyses.bestPractices || 'Analysis pending...'}

---

## 🎯 Executive Summary

This comprehensive analysis was performed by 8 specialized AI models, each focusing on their area of expertise. Review each section for specific insights and recommendations.

### Priority Actions
1. Review security findings immediately
2. Address critical code quality issues
3. Implement missing tests
4. Update documentation
5. Optimize performance bottlenecks

---

*Generated by Sophia Intel Perfect Swarm*
`;

  // Save report
  fs.writeFileSync(reportName, report);
  console.log(`\n✅ Report saved to: ${reportName}`);
  console.log(`\n📋 View the report with: cat ${reportName}`);
  
  // Also save as JSON for programmatic access
  const jsonReport = {
    timestamp,
    repository: repoInfo,
    analyses
  };
  fs.writeFileSync(`deep-analysis-${Date.now()}.json`, JSON.stringify(jsonReport, null, 2));
}

// Interactive mode
async function interactiveMode() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });

  console.log("\n🤔 Would you like to ask specific questions about the analysis?");
  console.log("Type 'exit' to quit or ask any question:\n");

  rl.on('line', async (input) => {
    if (input.trim() === 'exit') {
      rl.close();
      process.exit(0);
    }

    // Route question to most appropriate model
    console.log("\n🔄 Processing your question...");
    try {
      const response = await callOpenRouter(
        "anthropic/claude-3-opus-20240229",
        "You are a senior technical advisor. Answer based on the repository analysis context.",
        input,
        2048
      );
      console.log(`\n${response}\n`);
    } catch (error) {
      console.log(`❌ Error: ${error.message}\n`);
    }
  });
}

// Main execution
console.log("🚀 Starting Deep Repository Analysis...\n");
performDeepAnalysis().then(() => {
  interactiveMode();
}).catch(error => {
  console.error(`\n❌ Fatal error: ${error.message}`);
  process.exit(1);
});
