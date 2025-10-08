#!/bin/bash
# Add environment variables to Vercel projects
# Usage: bash add-vercel-envs.sh

VERCEL_TOKEN="QBIBlyfZ4Cs80V6nSRBJZQUa"
PROJECT="quest-placement"

echo "Adding environment variables to $PROJECT..."

# Add NEON_CONNECTION_STRING
echo "1. Adding NEON_CONNECTION_STRING..."
curl -X POST "https://api.vercel.com/v10/projects/$PROJECT/env" \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"key":"NEON_CONNECTION_STRING","value":"postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require","type":"encrypted","target":["production","preview","development"]}'

echo ""
echo "2. Adding CLOUDINARY_CLOUD_NAME..."
curl -X POST "https://api.vercel.com/v10/projects/$PROJECT/env" \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"key":"CLOUDINARY_CLOUD_NAME","value":"dc7btom12","type":"encrypted","target":["production","preview","development"]}'

echo ""
echo "3. Adding CLOUDINARY_API_KEY..."
curl -X POST "https://api.vercel.com/v10/projects/$PROJECT/env" \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"key":"CLOUDINARY_API_KEY","value":"653994623498835","type":"encrypted","target":["production","preview","development"]}'

echo ""
echo "4. Adding CLOUDINARY_API_SECRET..."
curl -X POST "https://api.vercel.com/v10/projects/$PROJECT/env" \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"key":"CLOUDINARY_API_SECRET","value":"MQQ61lBHOeaZsIopjOPlWX1ITBw","type":"encrypted","target":["production","preview","development"]}'

echo ""
echo "✅ Done! Environment variables added to $PROJECT"
