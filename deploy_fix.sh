#!/bin/bash
# Quick deployment fix script

echo "🚀 Applying fixes for 500 error on Render..."

# Add all changes
git add .

# Commit with descriptive message
git commit -m "Fix 500 error: enhance logging, add health check, improve ALLOWED_HOSTS"

# Push to GitHub (triggers Render deployment)
git push origin main

echo "✅ Changes pushed to GitHub"
echo "🔄 Render will now automatically redeploy"
echo ""
echo "📋 Next steps:"
echo "1. Check Render dashboard for build progress"
echo "2. Test health endpoint: https://mining-encyclopedia.onrender.com/health/"
echo "3. Check main site: https://mining-encyclopedia.onrender.com/"
echo ""
echo "🆘 If issues persist, check Render logs and refer to RENDER_TROUBLESHOOTING.md"
