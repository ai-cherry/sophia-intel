# SOPHIA Intel Infrastructure Guide

## Overview
This guide covers the infrastructure setup and deployment procedures for SOPHIA Intel.

## Environment Variables
The following environment variables are required:

- `OPENROUTER_API_KEY`: OpenRouter API key for AI model access
- `FLY_API_TOKEN`: Fly.io deployment token
- `GITHUB_PAT`: GitHub Personal Access Token
- `DNSIMPLE_API_KEY`: DNSimple API key for domain management
- `PULUMI_ACCESS_TOKEN`: [PULUMI_ACCESS_TOKEN] - managed via GitHub Secrets

## Deployment
All deployments are managed through GitHub Actions and Fly.io platform.

## Security
All sensitive data is managed through GitHub Organization Secrets and Pulumi ESC.
