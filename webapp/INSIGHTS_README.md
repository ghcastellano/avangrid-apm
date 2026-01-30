# Enhanced Strategic Insights System

## Overview

The enhanced insights system provides AI-powered strategic analysis of your application portfolio by:

1. **Deep per-application analysis** - Combining transcript data, questionnaires, and market research
2. **Portfolio-level pattern detection** - Identifying consolidation opportunities, redundancies, and gaps
3. **Actionable recommendations** - Evidence-based strategic guidance with specific action items

## Key Features

### Per-Application Insights
Each application gets analyzed across 6 dimensions:

1. **Capabilities Assessment**
   - Strengths and limitations
   - Unique value proposition
   - Core functionality analysis

2. **User Satisfaction**
   - Sentiment analysis from transcripts
   - Pain points identification
   - Key user quotes as evidence

3. **Technical Debt**
   - Severity assessment
   - Specific issues identified
   - Modernization needs

4. **Integration Opportunities**
   - Consolidation candidates
   - Target systems for integration
   - Dependencies mapping

5. **Market Alternatives** (for commercial products)
   - Modern alternatives available
   - Migration paths
   - Market position analysis

6. **Strategic Recommendation**
   - Specific action (INTEGRATE, MIGRATE, RETIRE, CONSOLIDATE, ENHANCE, MAINTAIN)
   - Target system or approach
   - Priority (P1/P2/P3)
   - Estimated impact and complexity
   - Detailed rationale with evidence
   - Action items with owners and timelines

### Portfolio-Level Insights

Cross-application analysis identifies:

- **Consolidation Opportunities** - Apps with overlapping functionality
- **Integration Points** - Where apps should connect
- **Redundancies** - Duplicate capabilities to eliminate
- **Portfolio Gaps** - Missing critical capabilities
- **Quick Wins** - High-impact, low-effort improvements
- **Strategic Roadmap** - P1/P2/P3 prioritized actions
- **Risk Areas** - Technical or business risks with mitigation

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: Per-Application Deep Dive                        │
│  ├─ Gather: Transcripts + Questionnaires + Market Data     │
│  ├─ Analyze: GPT-4o processes all context                  │
│  └─ Store: AppInsight table (6 insights per app)           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: Portfolio-Level Pattern Detection                │
│  ├─ Gather: All app insights + assessments                 │
│  ├─ Analyze: GPT-4o identifies patterns & opportunities    │
│  └─ Store: PortfolioInsight table                          │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

**AppInsight Table:**
- `application_id` - Links to specific application
- `insight_type` - Type of insight (capabilities, user_satisfaction, etc.)
- `content` - JSON with detailed analysis
- `confidence` - high/medium/low
- `evidence` - Supporting quotes from transcripts
- `action_items` - Specific next steps
- `affected_systems` - Other apps involved
- `model_version` - AI model used (gpt-4o)

**PortfolioInsight Table:**
- `insight_type` - consolidation, quick_win, risk, etc.
- `title` - Brief description
- `description` - Detailed explanation
- `affected_apps` - List of app names involved
- `priority` - P1/P2/P3
- `estimated_impact` - high/medium/low
- `complexity` - high/medium/low
- `recommended_action` - What to do
- `model_version` - AI model used

## Usage Guide

### Step 1: Generate Insights (One-Time)

From the `webapp` directory, run:

```bash
cd webapp
python generate_insights.py
```

**What happens:**
- Analyzes all applications individually (~30 seconds per app)
- Generates portfolio-level analysis (~1 minute)
- Stores everything in database
- Shows progress in real-time

**Cost:** ~$5-10 (varies by number of apps and transcript length)

**When to run:**
- After uploading new questionnaires or transcripts
- When significant changes occur in the portfolio
- To refresh analysis with latest market data

### Step 2: View Insights in UI

#### Per-Application Insights
1. Navigate to **Applications** page
2. Select an application from dropdown
3. Scroll to **Strategic Insights** section
4. Expand each insight type to see details

#### Portfolio-Level Insights
1. Navigate to **Analyses** page
2. Click **Insights** tab (tab 4)
3. View:
   - Summary metrics (consolidation opportunities, quick wins, risks)
   - Grouped insights by type
   - Affected applications
   - Priority and impact assessments

### Step 3: Act on Recommendations

Each insight includes:
- **Priority** - P1 (Critical), P2 (Strategic), P3 (Routine)
- **Impact** - Estimated business/technical impact
- **Complexity** - Implementation difficulty
- **Action Items** - Specific next steps
- **Evidence** - Supporting data from transcripts

Use these to:
1. Build your strategic roadmap
2. Prioritize portfolio initiatives
3. Make data-driven decisions
4. Communicate with stakeholders

## Advanced Features

### Market Research Integration

For commercial products (SAP, Oracle, Salesforce, etc.), the system:
- Automatically detects commercial software
- Searches for market alternatives
- Compares with modern solutions
- Suggests migration paths

Detected commercial products:
- SAP, Oracle, PeopleSoft
- Salesforce, ServiceNow, Workday
- Microsoft, Adobe, IBM products
- Maximo and similar platforms

### Web Search Enhancement (Optional)

To enable real-time web search for market data:
1. Add web search API key to `.env`:
   ```
   TAVILY_API_KEY=your_key_here
   ```
2. Uncomment web search code in `insight_generator.py`

### Confidence Levels

Each insight has a confidence level:
- **High** - Strong evidence from multiple sources
- **Medium** - Moderate evidence, some gaps
- **Low** - Limited data, assumptions made

Use confidence to guide decision-making:
- High confidence → Act immediately
- Medium confidence → Validate with stakeholders
- Low confidence → Gather more data first

## Customization

### Modify Insight Prompts

Edit `insight_generator.py`:
- `generate_app_insight()` - Per-app analysis prompt
- `generate_portfolio_insights()` - Portfolio analysis prompt

Customize:
- Analysis depth
- Specific focus areas
- Output format
- Evidence requirements

### Add New Insight Types

1. Update database model in `database.py`
2. Add new analysis logic in `insight_generator.py`
3. Update UI display in `app.py`

Example: Add "cost_analysis" insight type for TCO evaluation

### Change AI Model

In `insight_generator.py`, change:
```python
model="gpt-4o"  # Default: High quality, ~$5-10
```

Options:
- `gpt-4o-mini` - Faster, cheaper (~$1-2), good quality
- `o1-preview` - Best reasoning, expensive (~$75)
- `gpt-4o` - Balanced (recommended)

## Troubleshooting

### No insights appearing in UI

**Check:**
1. Did you run `python generate_insights.py`?
2. Check database: `sqlite3 data/avangrid.db "SELECT COUNT(*) FROM app_insights;"`
3. Look for errors in console output

### API errors during generation

**Common causes:**
- Missing or invalid OpenAI API key
- Rate limiting (wait and retry)
- Token limit exceeded (reduce transcript length)

**Solutions:**
- Set `OPENAI_API_KEY` in `.env` file
- Add rate limiting delays
- Truncate long transcripts in `generate_app_insight()`

### Insights seem incorrect

**Possible reasons:**
- Low quality transcript data
- Incomplete questionnaires
- AI hallucination

**Improvements:**
- Ensure transcripts are detailed and accurate
- Complete all questionnaire fields
- Lower temperature in API calls (currently 0.3)
- Use o1-preview model for better reasoning

## Cost Management

### Estimated Costs (as of 2026)

**GPT-4o pricing:**
- Input: $2.50 per 1M tokens
- Output: $10.00 per 1M tokens

**Typical usage:**
- Per-app analysis: ~6,500 tokens total → $0.06/app
- Portfolio analysis: ~23,000 tokens total → $0.23
- **Total for 70 apps: ~$5**

### Cost optimization:

1. **Use gpt-4o-mini** for initial testing ($1-2 total)
2. **Batch processing** - One run covers all apps
3. **Incremental updates** - Only re-analyze changed apps
4. **Caching** - Results stored in database, no re-calls needed

## Integration with Existing Features

### Q&A Assistant
Portfolio insights can inform Q&A responses:
- References specific insights in answers
- Provides evidence-based recommendations
- Links to detailed analysis

### Strategic Roadmap
Insights drive roadmap prioritization:
- P1 insights → Critical initiatives
- P2 insights → Strategic projects
- P3 insights → Routine maintenance

### Calculator
Manual adjustments informed by insights:
- Review insights before changing scores
- Evidence supports decision rationale
- Track which insights led to changes

## Future Enhancements

Potential improvements:
1. **Automated re-analysis** - Trigger on new uploads
2. **Insight voting** - Stakeholder feedback on accuracy
3. **Action tracking** - Link insights to tasks/projects
4. **Cost modeling** - TCO analysis per recommendation
5. **Dependency mapping** - Automatic system relationship detection
6. **Export to Excel** - Include insights in portfolio report

## Support

For issues or questions:
1. Check console output for error messages
2. Review database contents: `sqlite3 data/avangrid.db`
3. Validate API key in `.env` file
4. Check OpenAI API usage dashboard

## Best Practices

1. **Run insights after data collection is complete**
   - Upload all questionnaires first
   - Process all transcripts
   - Then generate insights

2. **Review and validate insights**
   - Don't blindly trust AI recommendations
   - Check evidence and rationale
   - Validate with subject matter experts

3. **Use confidence levels to guide actions**
   - High confidence → Priority actions
   - Low confidence → Gather more data

4. **Update regularly**
   - Re-run quarterly or after major changes
   - Track how insights evolve over time
   - Measure which actions were successful

5. **Combine with human judgment**
   - AI provides data-driven suggestions
   - Humans make final decisions
   - Use insights to inform, not replace, expertise
