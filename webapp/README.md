# ⚡ Avangrid APM Platform

Modern web application for Application Portfolio Management with AI-powered insights.

## 🚀 Quick Start

### 1. Navigate to the webapp folder
```bash
cd webapp
```

### 2. Install dependencies (if not installed yet)
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📋 Features

### ✅ Core Functionality
- **Upload Questionnaires**: Upload application questionnaire Excel files
- **Upload Transcripts**: Upload meeting transcripts (TXT, PDF, DOCX)
- **AI Analysis**: Automatic extraction of answers from transcripts using GPT-4
- **Score Suggestion**: AI-powered score suggestions for all 8 synergy blocks
- **Strategic Dashboard**: Interactive 2x2 matrix (BVI vs THI)
- **Insights Generation**: AI-generated strategic insights
- **Q&A Assistant**: Ask questions about your portfolio using natural language
- **Methodology**: Complete documentation of the APM framework

### 🎨 UI/UX Features
- Modern sidebar navigation
- Avangrid brand colors (#E87722 orange, #0066B3 blue)
- Interactive charts and visualizations
- Responsive design
- Smooth animations and transitions
- Cards with hover effects

## 📂 Project Structure

```
webapp/
├── app.py                 # Main Streamlit application
├── database.py            # SQLite database models
├── ai_processor.py        # OpenAI integration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (API keys)
├── .gitignore            # Git ignore file
├── data/                 # SQLite database storage
│   └── avangrid.db       # Local database (auto-created)
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables (.env)
```
OPENAI_API_KEY=your-api-key-here
DATABASE_PATH=data/avangrid.db
APP_TITLE=Avangrid APM Platform
DEBUG=True
```

**⚠️ IMPORTANT**: The `.env` file contains your OpenAI API key and is already configured.

## 📖 User Guide

### Step 1: Upload Questionnaire
1. Navigate to **Uploads** > **Questionnaire** tab
2. Upload your application questionnaire Excel file
3. The system will parse all applications and their answers
4. Click **Save to Database**

### Step 2: Upload Transcripts (Optional but Recommended)
1. Navigate to **Uploads** > **Transcripts** tab
2. Select the application
3. Upload one or more transcript files (TXT, PDF, DOCX)
4. Click **Process with AI**
5. Wait for AI to extract answers from transcripts

### Step 3: Generate Scores
1. Navigate to **Applications**
2. Click on an application to view details
3. Go to **Suggested Scores** tab
4. Click **Generate Suggested Scores**
5. Review AI suggestions and approve/adjust scores

### Step 4: View Analyses
1. Navigate to **Analyses**
2. Explore:
   - **2x2 Matrix**: Portfolio strategic visualization
   - **Strategic Roadmap**: Prioritized action plan
   - **Calculator**: Detailed score breakdown

### Step 5: Generate Insights
1. Navigate to **Insights**
2. Click **Generate Insights with AI**
3. Review strategic recommendations:
   - Integration opportunities
   - Absorption plans
   - Technology updates
   - Risk analysis
   - Financial optimization
   - Quick wins

### Step 6: Ask Questions
1. Navigate to **Q&A Assistant**
2. Type your question in natural language
3. Click **Ask**
4. Get AI-powered answers based on your data

## 🎯 The 8 Synergy Blocks

### Business Dimension (BVI)
1. **Strategic Fit** (30%): Alignment with business strategy
2. **Business Efficiency** (30%): Process automation level
3. **User Value** (20%): User satisfaction
4. **Financial Value** (20%): Cost-benefit ratio

### Technical Dimension (THI)
5. **Architecture** (30%): Technology modernity
6. **Operational Risk** (30%): Security and compliance
7. **Maintainability** (25%): Ease of maintenance
8. **Support Quality** (15%): Support availability

## 📊 Strategic Recommendations

| Quadrant | BVI | THI | Action |
|----------|-----|-----|--------|
| **EVOLVE** | ≥60 | ≥60 | Invest to enhance and modernize |
| **INVEST** | ≥60 | <60 | Fix technical debt urgently |
| **MAINTAIN** | <60 | ≥60 | Keep as-is, low priority |
| **ELIMINATE** | <60 | <60 | Decommission or consolidate |

## 🤖 AI Features

### Transcript Analysis
- Uses GPT-4 Turbo for deep analysis
- Extracts answers to all 60+ master questions
- Provides confidence scores (0.0 to 1.0)
- Identifies implicit mentions and sentiment
- Cross-references information

### Score Suggestion
- Analyzes both questionnaire and transcript answers
- Considers positive and negative keywords
- Provides detailed rationale for each score
- Defaults to score=1 for unanswered questions

### Insight Generation
- Identifies integration opportunities
- Suggests absorption plans for eliminated apps
- Recommends technology updates
- Flags security and compliance risks
- Finds financial optimization opportunities
- Highlights quick wins

### Q&A Assistant
- Natural language question answering
- Context-aware responses
- Cites specific sources
- Based on your actual data (no hallucinations)

## 💡 Tips

1. **Upload Order**: Upload questionnaire first, then transcripts
2. **Transcript Quality**: Better transcripts = better AI extraction
3. **Review AI Suggestions**: Always review and adjust AI-generated scores
4. **Ask Specific Questions**: More specific questions get better answers
5. **Export**: Use the Export feature to generate final Excel reports

## 🐛 Troubleshooting

### Application won't start
```bash
# Check if all dependencies are installed
pip install -r requirements.txt

# Check if port 8501 is available
lsof -i :8501

# Try a different port
streamlit run app.py --server.port 8502
```

### OpenAI API errors
- Check if API key is correct in `.env`
- Verify API key has credits
- Check internet connection

### Database errors
- Delete `data/avangrid.db` and restart (will reset all data)
- Check file permissions

### Import errors
- Ensure you're in the correct directory
- Ensure virtual environment is activated (if using one)

## 📝 Notes

- **Local Only**: This application runs locally on your machine
- **No Cloud**: Database is SQLite (local file)
- **Demo Purpose**: Built for presentation and demonstration
- **Data Privacy**: All data stays on your computer

## 🔄 Version History

- **v1.0** (2026-01-29): Initial MVP release
  - Core functionality implemented
  - AI integration complete
  - Modern UI with Avangrid branding

## 📧 Support

For issues or questions, refer to the project documentation or contact the development team.

---

**Built with ❤️ using:**
- Streamlit
- OpenAI GPT-4
- SQLAlchemy
- Plotly
- Python 3.14

© 2026 Avangrid
