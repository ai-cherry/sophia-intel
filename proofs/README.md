# Proof Artifacts

This directory contains real artifacts proving functionality:

- `healthz/` - Health check curl outputs
- `endpoints/` - API endpoint proofs  
- `deployments/` - Deployment evidence

All files should show headers + body, no mocks/fakes.

## Example Structure

```
proofs/
├── healthz/
│   ├── sophia-dashboard.txt
│   ├── sophia-code.txt
│   └── sophia-research.txt
├── endpoints/
│   ├── research-search.txt
│   └── code-generate.txt
└── deployments/
    ├── fly-deploy-output.txt
    └── github-pr-evidence.txt
```

## Format Requirements

Each proof file should contain:
1. Command executed
2. Full HTTP headers
3. Complete response body
4. Timestamp of execution

Example:
```bash
$ curl -i https://sophia-code.fly.dev/healthz
HTTP/1.1 200 OK
Content-Type: application/json
Date: Wed, 21 Aug 2025 07:00:00 GMT

{"status":"ok","service":"code-server","version":"4.2.0"}
```
