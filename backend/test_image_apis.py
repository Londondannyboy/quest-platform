#!/usr/bin/env python3
"""
Test Image Generation & Storage APIs for Quest Platform
Tests Replicate (FLUX Pro) and Cloudinary
"""
import os
import sys
import requests
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_replicate_flux_pro():
    """Test Replicate API with FLUX Pro model"""
    api_key = os.getenv('REPLICATE_API_KEY')
    if not api_key:
        return "❌ No API key configured"

    try:
        # FLUX Pro model - highest quality
        model_id = "black-forest-labs/flux-pro"

        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers={
                "Authorization": f"Token {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "version": "95b7223104b62efdbf4c8e5a6ce24db356d6d122c7d39845e507208918f48e98",
                "input": {
                    "prompt": "Professional modern office with people working on laptops, bright natural lighting, photorealistic",
                    "width": 1024,
                    "height": 768,
                    "steps": 25,
                    "guidance": 3,
                    "output_format": "webp",
                    "output_quality": 80
                }
            },
            timeout=10
        )

        if response.status_code == 201:
            data = response.json()
            return f"✅ Working - Prediction ID: {data['id'][:8]}... (will take ~30s to generate)"
        else:
            return f"⚠️ Status {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def test_replicate_flux_schnell():
    """Test Replicate API with FLUX Schnell (fast) model"""
    api_key = os.getenv('REPLICATE_API_KEY')
    if not api_key:
        return "❌ No API key configured"

    try:
        # FLUX Schnell - faster, lower quality
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers={
                "Authorization": f"Token {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "version": "5599ed30703defd1d160a25a63321b4dec97101d98b4674bcc56e41f62f35637",
                "input": {
                    "prompt": "Digital nomad working from a cafe in Lisbon, laptop, coffee, sunny",
                    "width": 1024,
                    "height": 768,
                    "num_outputs": 1
                }
            },
            timeout=10
        )

        if response.status_code == 201:
            data = response.json()
            return f"✅ Working - Prediction ID: {data['id'][:8]}... (will take ~5s to generate)"
        else:
            return f"⚠️ Status {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def test_cloudinary():
    """Test Cloudinary API for image upload and transformation"""
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')

    if not all([cloud_name, api_key, api_secret]):
        return "❌ Missing Cloudinary credentials"

    try:
        # Test admin API endpoint
        auth = base64.b64encode(f"{api_key}:{api_secret}".encode()).decode()

        response = requests.get(
            f"https://api.cloudinary.com/v1_1/{cloud_name}/ping",
            headers={"Authorization": f"Basic {auth}"},
            timeout=10
        )

        if response.status_code == 200:
            # Also test usage endpoint
            usage_response = requests.get(
                f"https://api.cloudinary.com/v1_1/{cloud_name}/usage",
                headers={"Authorization": f"Basic {auth}"},
                timeout=10
            )

            if usage_response.status_code == 200:
                usage = usage_response.json()
                plan = usage.get('plan', 'unknown')
                credits_used = usage.get('credits', {}).get('usage', 0)
                return f"✅ Working - Plan: {plan}, Credits used: {credits_used:.2f}"
            else:
                return f"✅ Ping works, usage check failed: {usage_response.status_code}"
        else:
            return f"⚠️ Status {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def test_dataforseo():
    """Test DataForSEO API for keyword research"""
    login = os.getenv('DATAFORSEO_LOGIN')
    password = os.getenv('DATAFORSEO_PASSWORD')

    if not all([login, password]):
        return "❌ Missing DataForSEO credentials"

    try:
        # Base64 encode credentials
        auth_string = f"{login}:{password}"
        auth = base64.b64encode(auth_string.encode()).decode()

        # Test with keyword volume endpoint
        response = requests.post(
            "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live",
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/json"
            },
            json=[{
                "keywords": ["digital nomad portugal", "remote work lisbon"],
                "location_code": 2620,  # Portugal
                "language_code": "en"
            }],
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('status_code') == 20000:
                # Success
                tasks = data.get('tasks', [])
                if tasks and tasks[0].get('result'):
                    results = tasks[0]['result'][0] if tasks[0]['result'] else {}
                    keyword_count = len(results.get('keyword', []))
                    cost = tasks[0].get('cost', 0)
                    return f"✅ Working - {keyword_count} keywords analyzed, cost: ${cost:.4f}"
                return "✅ Connected but no results"
            else:
                return f"⚠️ API Error: {data.get('status_message', 'Unknown')}"
        else:
            return f"⚠️ Status {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def main():
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║    IMAGE GENERATION & SEO API VALIDATION TEST            ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print("\n" + "="*60)

    # Test all APIs
    apis = [
        ("1. Replicate FLUX Pro (High Quality)", test_replicate_flux_pro),
        ("2. Replicate FLUX Schnell (Fast)", test_replicate_flux_schnell),
        ("3. Cloudinary (Image Storage/CDN)", test_cloudinary),
        ("4. DataForSEO (Keyword Research)", test_dataforseo),
    ]

    working_count = 0
    failed_count = 0

    for name, test_func in apis:
        print(f"\nTesting {name}...")
        result = test_func()
        print(f"   {result}")

        if "✅" in result:
            working_count += 1
        elif "❌" in result:
            failed_count += 1

    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print(f"   ✅ Working: {working_count}/4")
    print(f"   ❌ Failed: {failed_count}/4")

    print("\n💡 NOTES:")
    print("   • FLUX Pro: Best quality, ~30s generation time, ~$0.05/image")
    print("   • FLUX Schnell: Faster (~5s), lower quality, ~$0.01/image")
    print("   • Cloudinary: Free tier = 25 credits/month")
    print("   • DataForSEO: ~$0.01 per keyword batch")

    return working_count >= 2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)