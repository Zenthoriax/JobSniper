#!/bin/bash

# JobSniper Quick Setup & Test Script
# This script verifies your environment and runs a quick test

echo "🦅 JobSniper v2.1 - Setup Verification"
echo "========================================"
echo ""

# Check Python version
echo "📌 Checking Python version..."
python_version=$(python3 --version 2>&1)
echo "   ✅ $python_version"
echo ""

# Check if in correct directory
if [ ! -f "src/main.py" ]; then
    echo "❌ Error: Please run this script from the JobSniper root directory"
    exit 1
fi
echo "✅ Correct directory"
echo ""

# Check/Install dependencies
echo "📦 Checking dependencies..."
if ! python3 -c "import pandas" 2>/dev/null; then
    echo "   ⚠️  Dependencies not installed. Installing now..."
    pip install -r requirements.txt
    echo "   ✅ Dependencies installed"
else
    echo "   ✅ Dependencies already installed"
fi
echo ""

# Check .env file
echo "🔐 Checking environment variables..."
if [ ! -f ".env" ]; then
    echo "   ⚠️  .env file not found. Creating template..."
    cat > .env << 'EOF'
EMAIL_APP_PASSWORD=your_gmail_app_password_here
GEMINI_API_KEY=your_gemini_api_key_here
EOF
    echo "   ⚠️  Please edit .env file with your credentials"
    echo "   📖 See GITHUB_ACTIONS_SETUP.md for instructions"
else
    echo "   ✅ .env file exists"
    
    # Check if credentials are set
    if grep -q "your_gmail_app_password_here" .env; then
        echo "   ⚠️  EMAIL_APP_PASSWORD not configured"
    else
        echo "   ✅ EMAIL_APP_PASSWORD configured"
    fi
fi
echo ""

# Check data directory structure
echo "📁 Checking data directories..."
mkdir -p data/raw data/verified
echo "   ✅ Data directories ready"
echo ""

# Display current configuration
echo "⚙️  Current Configuration:"
echo "   - HOURS_OLD: 24 (fresh jobs only)"
echo "   - MIN_MATCH_SCORE: 55"
echo "   - USE_GEMINI: False (local scoring)"
echo "   - Delay per job: 2 seconds"
echo ""

# Offer to run test
echo "🧪 Ready to test JobSniper?"
echo ""
echo "Options:"
echo "  1. Run full test (scrape + audit + email)"
echo "  2. Skip test (setup only)"
echo ""
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo ""
    echo "🚀 Starting JobSniper test run..."
    echo "   This may take 2-5 minutes depending on job availability"
    echo ""
    cd src
    python3 main.py
    echo ""
    echo "✅ Test complete! Check your email for results."
else
    echo ""
    echo "✅ Setup verification complete!"
fi

echo ""
echo "📚 Next Steps:"
echo "   1. Configure .env with your credentials"
echo "   2. Test locally: python src/main.py"
echo "   3. Push to GitHub"
echo "   4. Setup GitHub Actions (see GITHUB_ACTIONS_SETUP.md)"
echo ""
echo "🎉 Happy job hunting!"
