#!/bin/bash

API_KEY="sk_HedYC8pG9Zntwj45eGbGbFHsa514SAVn0f"
BASE_URL="https://gen.pollinations.ai/image"

# Generate hero background
curl -L "${BASE_URL}/futuristic%20AI%20neural%20network%20purple%20pink%20cyan%20glow%20dark%20background%20abstract%20technology?width=1920&height=1080&nologo=true" \
  -H "Authorization: Bearer ${API_KEY}" \
  -o hero-bg.jpg 2>/dev/null

# Generate feature image 1 - AI/Automation
curl -L "${BASE_URL}/robot%20AI%20agent%20autonomous%20futuristic%20minimal%20dark%20background%20purple%20blue%20glow?width=400&height=400&nologo=true" \
  -H "Authorization: Bearer ${API_KEY}" \
  -o feature-ai.jpg 2>/dev/null

# Generate feature image 2 - Token/Crypto
curl -L "${BASE_URL}/cryptocurrency%20token%20coin%20diamond%203D%20futuristic%20dark%20background%20pink%20cyan%20glow?width=400&height=400&nologo=true" \
  -H "Authorization: Bearer ${API_KEY}" \
  -o feature-token.jpg 2>/dev/null

# Generate feature image 3 - Community
curl -L "${BASE_URL}/community%20network%20connection%20nodes%203D%20futuristic%20dark%20background%20purple%20blue%20glow?width=400&height=400&nologo=true" \
  -H "Authorization: Bearer ${API_KEY}" \
  -o feature-community.jpg 2>/dev/null

# Generate feature image 4 - Goals/Target
curl -L "${BASE_URL}/target%20bullseye%20arrow%20success%203D%20futuristic%20dark%20background%20cyan%20green%20glow?width=400&height=400&nologo=true" \
  -H "Authorization: Bearer ${API_KEY}" \
  -o feature-goals.jpg 2>/dev/null

# Generate OG image for social sharing
curl -L "${BASE_URL}/Ken%20AI%20virtual%20influencer%20robot%20portrait%20futuristic%20purple%20pink%20cyan%20gradient%20dark%20background%20professional%20high%20quality?width=1200&height=630&nologo=true" \
  -H "Authorization: Bearer ${API_KEY}" \
  -o og-image.jpg 2>/dev/null

echo "Images generated!"