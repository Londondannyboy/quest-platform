#!/bin/bash
# Test article generation API

curl -X POST http://localhost:8000/api/articles/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"Best Digital Nomad Cities in Portugal 2025","target_site":"relocation","target_audience":"remote_workers","tone":"professional"}'
