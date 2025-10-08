#!/bin/bash
# Add all environment variables to Railway service

RAILWAY_TOKEN="926abaa5-0038-49ae-b884-0f9ef8df6675"
PROJECT_ID="cff74017"

# Get service ID (you'll need to find this in Railway dashboard)
# For now, we'll add variables at the project level

echo "Adding environment variables to Railway project..."

# Add database
curl -X POST https://backboard.railway.app/graphql/v2 \
  -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation variableUpsert($input: VariableUpsertInput!) { variableUpsert(input: $input) }",
    "variables": {
      "input": {
        "projectId": "'"$PROJECT_ID"'",
        "name": "NEON_CONNECTION_STRING",
        "value": "postgresql://neondb_owner:npg_Q9VMTIX2eHws@ep-steep-wildflower-abrkgyqu-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"
      }
    }
  }'

# Add Redis
curl -X POST https://backboard.railway.app/graphql/v2 \
  -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation variableUpsert($input: VariableUpsertInput!) { variableUpsert(input: $input) }",
    "variables": {
      "input": {
        "projectId": "'"$PROJECT_ID"'",
        "name": "UPSTASH_REDIS_URL",
        "value": "redis://default:AcLLAAIjcDE5ZTg2MTg0ODBmNGY0ZDRkYTEwZjU3ZDFmNGI0YWNhZXAxMA@humorous-gibbon-10467.upstash.io:6379"
      }
    }
  }'

echo ""
echo "✅ Added database and Redis variables"
echo ""
echo "⚠️  You still need to add the AI API keys manually in Railway dashboard:"
echo "   - PERPLEXITY_API_KEY"
echo "   - ANTHROPIC_API_KEY"
echo "   - OPENAI_API_KEY"
echo "   - REPLICATE_API_TOKEN"
echo "   - CLOUDINARY_CLOUD_NAME"
echo "   - CLOUDINARY_API_KEY"
echo "   - CLOUDINARY_API_SECRET"
echo "   - ENVIRONMENT=production"
echo ""
echo "Go to: Railway Dashboard → Variables tab → Add each variable"
