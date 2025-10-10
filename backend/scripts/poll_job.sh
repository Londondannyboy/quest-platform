#!/bin/bash
JOB_ID=$1
for i in {1..10}; do
  echo "=== Poll #$i ==="
  curl -s https://quest-platform-production-9ee0.up.railway.app/api/jobs/$JOB_ID | python3 -m json.tool
  echo ""
  sleep 15
done
