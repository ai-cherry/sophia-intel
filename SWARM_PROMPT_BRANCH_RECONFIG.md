# 🎯 SWARM PROMPT: Branch Reconfiguration & Optimization

## CONTEXT
Repository: sophia-intel (local clone at /Users/lynnmusil/Projects/sophia-main/sophia-intel-clone)
Current State: 12 branches with redundancy and unclear purposes
Goal: Streamline to 4 clear branches with defined workflows

## CURRENT BRANCH ANALYSIS
```
Duplicates: main, unified-dev, backup/pre-swarm (all 115 files, same content)
Outdated: feat/initial-setup, feat/integration-agno, feat/esc-bootstrap (33 files each)
Advanced: feature/ai-swarm-complete (120 files), feature/advanced-portkey (116 files)
Streamlined: notion (41 files, CLI v3.0.0), release/ready-to-ship (87 files)
```

## TASK FOR PLANNER
Create a migration strategy to reorganize branches from 12 to 4, preserving important features while eliminating redundancy. The new structure should be:
- main: stable base
- production: streamlined deployment from notion branch
- next: advanced features merging ai-swarm and portkey
- release/template: clean template from ready-to-ship

## TASK FOR CODER
Write a Git automation script that:
1. Creates new branch structure without losing commits
2. Merges feature branches intelligently
3. Archives old branches as tags
4. Provides rollback capability
5. Updates remote repository safely

## TASK FOR CHALLENGER
Review the reconfiguration plan for:
- Risk of losing important commits or features
- Merge conflicts between ai-swarm and portkey branches
- Impact on existing CI/CD pipelines
- Team member disruption
- Recovery strategy if something goes wrong

## TASK FOR QA/TESTER
Generate test cases to verify:
- All features from merged branches still work
- No code is lost in the transition
- Git history remains intact
- Tags properly preserve archived branches
- New workflow (main→next→production) functions correctly

## TASK FOR DOC_REVIEWER
Review and create documentation for:
- New branch structure and purpose of each branch
- Migration guide for team members
- Updated CI/CD configuration requirements
- Git workflow diagrams
- Rollback procedures

## DELIVERABLES NEEDED
1. Detailed migration plan with risk assessment
2. Executable shell script for branch reconfiguration
3. Validation checklist to confirm success
4. Team communication template
5. Rollback script if needed

## CONSTRAINTS
- Cannot lose any commit history
- Must maintain ability to access old branches (via tags)
- Should complete in under 10 minutes
- Must be reversible
- Minimize disruption to active development

## SUCCESS CRITERIA
- Reduce from 12 to 4 active branches
- Clear purpose for each remaining branch
- All tests pass on new branches
- Team can immediately understand new structure
- Git history fully preserved
