# 🎯 SWARM PROMPT: Complete Repository Assessment & Branch Optimization

## COPY THIS INTO YOUR SWARM CLI:

```
plan Perform complete repository assessment of sophia-intel with 12 branches (main-115 files, notion-41 files, ai-swarm-120 files, portkey-116 files, unified-dev-115 files duplicate of main, release/ready-to-ship-87 files, 5 feat/* branches with 30-40 files each outdated). Analyze: 1) Code duplication across branches 2) Feature completeness and production readiness 3) Commit history value 4) Dependencies and conflicts 5) CI/CD compatibility. Recommend optimal branch structure reducing from 12 to 4-5 branches. Consider: notion branch has streamlined CLI v3.0, ai-swarm has monitoring dashboard and Qdrant memory, portkey has OpenRouter integration, main/unified-dev are identical, feat/* branches are 2+ weeks old. Must preserve all valuable code, maintain git history via tags, enable clean development workflow, support production deployments, and complete reorganization in under 10 minutes. Provide risk assessment, migration strategy, and rollback plan.
```

## OR BREAK IT INTO SPECIALIZED ASSESSMENTS:

### 1. DEEP ANALYSIS (Opus 4.1):
```
plan Analyze sophia-intel repository structure: Compare 12 branches for code overlap, identify unique features per branch, assess technical debt, evaluate production readiness. Branches: main(115), notion(41-streamlined), ai-swarm(120-monitoring), portkey(116-routing), unified-dev(115-duplicate), release(87), 5 feat/* branches(30-40 each). Determine minimum viable branch set preserving all functionality.
```

### 2. IMPLEMENTATION STRATEGY (Sonnet 4):
```
code_special Create comprehensive Git migration script for sophia-intel: safely merge ai-swarm+portkey into 'next' branch, convert notion to 'production' branch, archive 5 feat/* branches as annotated tags, delete duplicate unified-dev/backup branches, preserve complete commit history, provide automated rollback mechanism, update remote refs, and validate no code loss. Include pre-flight checks, progress logging, and recovery procedures.
```

### 3. RISK ASSESSMENT (Grok 4):
```
challenge Assess risks in consolidating 12 Git branches to 4: merging 120-file ai-swarm with 116-file portkey (conflict potential), deleting unified-dev/backup (data loss risk), converting 41-file notion to production (missing features?), archiving feat/* branches as tags (lost branch history). Review for: merge conflicts, CI/CD breakage, lost commits, team disruption, deployment failures, rollback complexity. Provide mitigation strategies.
```

### 4. VALIDATION TESTING (Gemini 2.5):
```
qa_test Generate comprehensive test suite for Git branch migration validation: verify all code from 12 original branches exists in 4 new branches, confirm no commits lost during consolidation, validate merged features work together (ai-swarm monitoring + portkey routing), test CI/CD pipelines with new structure, verify tags preserve archived branch access, test rollback procedures, validate production deployment from new 'production' branch.
```

### 5. DOCUMENTATION (GLM-4.5V):
```
doc_review Create complete documentation for optimized branch structure: explain purpose of each final branch (main-stable, production-deploy, next-features, archive-tags), document migration path from old to new structure, create visual diagram of new git workflow, update CI/CD configuration examples, write team migration guide, document emergency rollback procedures. Ensure clarity for developers unfamiliar with reorganization.
```

## COMPREHENSIVE ONE-SHOT PROMPT:

```
swarm_orchestrate Perform full repository audit and branch optimization for sophia-intel: Analyze 12 branches (main-115, notion-41, ai-swarm-120, portkey-116, unified-dev-115-duplicate, release-87, 5 feat/*-30each) for duplication/value/readiness. Design optimal 4-branch structure preserving all code. Create migration script with: branch consolidation plan, merge conflict resolution, tag-based archival, CI/CD updates, validation tests, rollback capability. Assess risks: data loss, merge conflicts, team disruption, deployment issues. Generate: implementation checklist, test cases, documentation, visual workflow diagram. Success criteria: <10min execution, zero code loss, maintainable structure, clear team communication. Deliver actionable plan ready for immediate execution.
```

## KEY QUESTIONS TO ANSWER:

1. **Which branches contain unique, production-critical code?**
2. **What's the overlap percentage between main/unified-dev/backup?**
3. **Can notion's 41 files serve as the entire production branch?**
4. **Will merging ai-swarm (120) + portkey (116) create conflicts?**
5. **Are the feat/* branches truly obsolete or contain unmerged features?**
6. **What's the minimum branch count while maintaining all functionality?**
7. **How to preserve history while removing redundancy?**

## EXPECTED DELIVERABLES:

1. **Branch Comparison Matrix** - showing overlap/unique features
2. **Optimal Structure Recommendation** - 4-5 branches with clear purposes
3. **Migration Script** - executable code for reorganization
4. **Risk Assessment** - with probability/impact ratings
5. **Validation Checklist** - to confirm success
6. **Team Communication Plan** - for smooth transition
7. **Rollback Procedure** - if issues arise

## SUCCESS METRICS:

- ✅ Reduce from 12 to ≤5 branches
- ✅ Zero code/commit loss
- ✅ All tests pass post-migration
- ✅ Clear branch purposes
- ✅ <10 minute execution time
- ✅ Fully reversible changes
- ✅ Team can immediately understand new structure
