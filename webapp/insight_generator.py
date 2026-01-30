"""
Enhanced Strategic Insight Generator
Generates deep, actionable insights by combining transcript analysis with market research
"""

import json
import uuid
from typing import List, Dict, Tuple
from datetime import datetime
from openai import OpenAI
import os
from dotenv import load_dotenv

from database import (
    get_session, close_session,
    Application, MeetingTranscript, QuestionnaireAnswer,
    TranscriptAnswer, SynergyScore, AppInsight, PortfolioInsight
)
from ai_processor import calculate_bvi_thi, get_recommendation, SYNERGY_BLOCKS

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Commercial products that have market alternatives
COMMERCIAL_PRODUCTS = [
    "SAP", "Oracle", "Salesforce", "ServiceNow", "Workday",
    "Microsoft", "Adobe", "IBM", "PeopleSoft", "Maximo"
]

def is_commercial_product(app_name: str) -> bool:
    """Check if application is a commercial product with market alternatives"""
    return any(product.lower() in app_name.lower() for product in COMMERCIAL_PRODUCTS)

def search_market_data(app_name: str) -> str:
    """
    Search for market data about the application.
    For commercial products, looks for alternatives and market trends.
    """
    # Use web search to find market information
    # This is a placeholder - would integrate with actual web search
    try:
        from ai_processor import client as ai_client

        search_query = f"{app_name} application capabilities features alternatives 2026"

        # Simple web search approach - in production, use dedicated search API
        prompt = f"""Search the web for information about the application '{app_name}'.

Focus on:
1. Core capabilities and features
2. Known limitations or issues
3. Modern alternatives or competitors
4. Recent market trends or news
5. Typical migration paths or replacements

Provide a concise summary (200 words max) of relevant findings."""

        # Note: In production, replace with actual web search
        # For now, return placeholder
        return f"Market research for {app_name} - analysis pending"

    except Exception as e:
        print(f"Error searching market data for {app_name}: {e}")
        return ""

def generate_app_insight(app: Application, session) -> Dict:
    """
    Generate comprehensive strategic insights for a single application.

    Combines:
    - All transcript data
    - Questionnaire responses
    - Current scores and assessment
    - Market research (if commercial product)

    Returns dict with insights by category
    """

    print(f"\n{'='*60}")
    print(f"🔍 Analyzing: {app.name}")
    print(f"{'='*60}")

    # Gather all data
    transcripts = session.query(MeetingTranscript).filter_by(application_id=app.id).all()
    qa_answers = session.query(QuestionnaireAnswer).filter_by(application_id=app.id).all()
    ta_answers = session.query(TranscriptAnswer).filter_by(application_id=app.id).all()
    scores = session.query(SynergyScore).filter_by(application_id=app.id, approved=True).all()

    # Calculate assessment
    scores_dict = {s.block_name: s.score for s in scores} if scores else {}
    bvi, thi = calculate_bvi_thi(scores_dict) if scores_dict else (0, 0)
    recommendation = get_recommendation(bvi, thi) if scores_dict else "UNKNOWN"

    # Build context
    context = {
        'app_name': app.name,
        'bvi': bvi,
        'thi': thi,
        'recommendation': recommendation,
        'transcript_count': len(transcripts),
        'questionnaire_responses': len(qa_answers),
        'transcript_responses': len(ta_answers)
    }

    # Compile all text data
    all_transcripts = "\n\n---TRANSCRIPT---\n\n".join([t.transcript_text for t in transcripts])
    all_qa = "\n".join([f"Q: {qa.question_text}\nA: {qa.answer_text}" for qa in qa_answers])
    all_ta = "\n".join([
        f"Q: {ta.question_text}\nA: {ta.answer_text} (Confidence: {ta.confidence_score:.0%})"
        for ta in ta_answers if ta.confidence_score > 0.5
    ])

    # Score details
    score_summary = "\n".join([
        f"- {s.block_name}: {s.score}/5 - {s.rationale[:100]}..."
        for s in scores
    ]) if scores else "No scores available"

    # Market research for commercial products
    market_data = ""
    if is_commercial_product(app.name):
        print(f"   📊 Commercial product detected - gathering market data...")
        market_data = search_market_data(app.name)

    # Create comprehensive prompt
    prompt = f"""You are a strategic IT portfolio consultant analyzing an application for decision-making.

APPLICATION: {app.name}

CURRENT ASSESSMENT:
- Business Value Index (BVI): {bvi}/100
- Technical Health Index (THI): {thi}/100
- Strategic Recommendation: {recommendation}
- Data Sources: {context['transcript_count']} transcripts, {context['questionnaire_responses']} questionnaire responses

SYNERGY BLOCK SCORES:
{score_summary}

QUESTIONNAIRE DATA:
{all_qa[:3000]}

TRANSCRIPT DATA (User feedback, technical discussions, pain points):
{all_transcripts[:5000]}

TRANSCRIPT-EXTRACTED ANSWERS:
{all_ta[:2000]}

{f"MARKET RESEARCH:\n{market_data}\n" if market_data else ""}

Your task is to provide deep, actionable strategic insights across multiple dimensions:

1. **Capabilities Assessment**: What does this application actually do well? What are its limitations?

2. **User Satisfaction**: What do users say about it? Pain points? Satisfaction signals?

3. **Technical Debt**: Architecture issues, obsolete technology, maintenance challenges?

4. **Integration Opportunities**: Could this be consolidated with other apps? Dependencies?

5. **Market Alternatives**: (If commercial) Are there better modern alternatives? Migration paths?

6. **Strategic Recommendation**: Beyond the BVI/THI matrix, what should we ACTUALLY do?
   - INTEGRATE into which app?
   - MIGRATE to what platform?
   - RETIRE and replace with what?
   - CONSOLIDATE with which apps?
   - ENHANCE in what specific ways?

7. **Action Items**: Top 3-5 specific, actionable next steps

8. **Decision Confidence**: How confident are you in this recommendation? (High/Medium/Low)

9. **Key Evidence**: 2-3 direct quotes from transcripts that support your recommendation

Output as JSON:
{{
  "capabilities": {{
    "strengths": ["capability 1", "capability 2"],
    "limitations": ["limitation 1", "limitation 2"],
    "unique_value": "what makes this app special or irreplaceable"
  }},
  "user_satisfaction": {{
    "sentiment": "positive/mixed/negative",
    "pain_points": ["pain 1", "pain 2"],
    "satisfaction_signals": ["signal 1", "signal 2"],
    "key_quotes": ["quote 1", "quote 2"]
  }},
  "technical_debt": {{
    "severity": "high/medium/low",
    "issues": ["issue 1", "issue 2"],
    "modernization_needs": ["need 1", "need 2"]
  }},
  "integration_opportunities": {{
    "can_consolidate_with": ["app name 1", "app name 2"],
    "should_integrate_into": "target app name or null",
    "dependencies": ["system 1", "system 2"]
  }},
  "market_alternatives": {{
    "alternatives": ["alternative 1", "alternative 2"],
    "migration_path": "recommended migration approach",
    "market_position": "leading/competitive/obsolete"
  }},
  "strategic_recommendation": {{
    "action": "INTEGRATE/MIGRATE/RETIRE/CONSOLIDATE/ENHANCE/MAINTAIN",
    "target": "specific target system or approach",
    "priority": "P1/P2/P3",
    "rationale": "detailed explanation",
    "estimated_impact": "high/medium/low",
    "complexity": "high/medium/low"
  }},
  "action_items": [
    {{"action": "specific action", "owner": "suggested owner", "timeline": "timeframe"}},
  ],
  "confidence": "high/medium/low",
  "confidence_rationale": "why this confidence level",
  "evidence": ["quote 1", "quote 2", "quote 3"]
}}

Return ONLY valid JSON, no other text."""

    try:
        print(f"   🤖 Calling OpenAI GPT-4o for deep analysis...")

        response = client.chat.completions.create(
            model="gpt-4o",  # Using most powerful model for best insights
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior IT portfolio management consultant with 20+ years experience in enterprise application assessment, modernization, and strategic planning. You provide direct, actionable insights backed by evidence."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        print(f"   ✅ Analysis complete!")

        return result

    except Exception as e:
        print(f"   ❌ Error generating insights: {e}")
        return {
            "error": str(e),
            "capabilities": {"strengths": [], "limitations": [], "unique_value": "Error in analysis"},
            "strategic_recommendation": {
                "action": recommendation,
                "rationale": f"Error during analysis: {e}",
                "priority": "P3"
            }
        }

def save_app_insights(app_id: str, insights: Dict, session):
    """Save application insights to database"""

    model_version = "gpt-4o"

    # Save each insight type
    insight_types = {
        'capabilities': insights.get('capabilities', {}),
        'user_satisfaction': insights.get('user_satisfaction', {}),
        'technical_debt': insights.get('technical_debt', {}),
        'integration_opportunities': insights.get('integration_opportunities', {}),
        'market_alternatives': insights.get('market_alternatives', {}),
        'strategic_recommendation': insights.get('strategic_recommendation', {})
    }

    for insight_type, content in insight_types.items():
        if content:
            app_insight = AppInsight(
                id=str(uuid.uuid4()),
                application_id=app_id,
                insight_type=insight_type,
                content=json.dumps(content),
                confidence=insights.get('confidence', 'medium'),
                evidence=insights.get('evidence', []),
                action_items=insights.get('action_items', []),
                affected_systems=content.get('can_consolidate_with', []) if insight_type == 'integration_opportunities' else [],
                generated_at=datetime.utcnow(),
                model_version=model_version
            )
            session.add(app_insight)

    session.commit()
    print(f"   💾 Saved {len(insight_types)} insight types to database")

def generate_portfolio_insights(session) -> Dict:
    """
    Generate portfolio-level strategic insights.
    Identifies patterns, redundancies, consolidation opportunities across all apps.
    """

    print(f"\n{'='*60}")
    print(f"🌐 PORTFOLIO-LEVEL ANALYSIS")
    print(f"{'='*60}")

    # Get all apps with their insights
    apps = session.query(Application).all()
    all_app_insights = session.query(AppInsight).all()

    # Organize insights by app
    insights_by_app = {}
    for app in apps:
        app_insights = [i for i in all_app_insights if i.application_id == app.id]
        if app_insights:
            insights_by_app[app.name] = {
                'app_id': app.id,
                'insights': [json.loads(i.content) for i in app_insights]
            }

    # Get assessment summary
    apps_summary = []
    for app in apps:
        scores = session.query(SynergyScore).filter_by(application_id=app.id, approved=True).all()
        if scores:
            scores_dict = {s.block_name: s.score for s in scores}
            bvi, thi = calculate_bvi_thi(scores_dict)
            rec = get_recommendation(bvi, thi)
            apps_summary.append({
                'name': app.name,
                'bvi': bvi,
                'thi': thi,
                'recommendation': rec
            })

    prompt = f"""You are analyzing an enterprise application portfolio of {len(apps)} applications.

PORTFOLIO SUMMARY:
{json.dumps(apps_summary, indent=2)}

INDIVIDUAL APP INSIGHTS:
{json.dumps(insights_by_app, indent=2)[:15000]}

Your task is to identify PORTFOLIO-LEVEL strategic opportunities and patterns:

1. **Consolidation Opportunities**: Which apps have overlapping functionality and should be merged?

2. **Integration Points**: Which apps should be connected to improve data flow?

3. **Redundancies**: Where are we paying for duplicate capabilities?

4. **Portfolio Gaps**: What critical capabilities are missing?

5. **Quick Wins**: What are the highest-impact, lowest-effort improvements?

6. **Strategic Priorities**: What's the P1/P2/P3 roadmap for portfolio optimization?

7. **Risk Areas**: Where are the biggest technical or business risks?

Output as JSON:
{{
  "consolidation_opportunities": [
    {{
      "apps": ["app1", "app2", "app3"],
      "rationale": "why these should be consolidated",
      "target_state": "what the consolidated solution looks like",
      "priority": "P1/P2/P3",
      "estimated_impact": "high/medium/low",
      "complexity": "high/medium/low"
    }}
  ],
  "integration_points": [
    {{
      "apps": ["app1", "app2"],
      "integration_type": "data sync/API/workflow",
      "business_value": "what this enables",
      "priority": "P1/P2/P3"
    }}
  ],
  "redundancies": [
    {{
      "capability": "what's duplicated",
      "apps": ["app1", "app2"],
      "cost_impact": "annual cost of redundancy if known",
      "recommendation": "which to keep, which to retire"
    }}
  ],
  "gaps": [
    {{
      "capability": "missing capability",
      "impact": "business impact",
      "recommendation": "build vs buy vs integrate"
    }}
  ],
  "quick_wins": [
    {{
      "opportunity": "what to do",
      "apps": ["affected apps"],
      "impact": "high/medium/low",
      "effort": "low/medium/high",
      "roi": "why this is high value"
    }}
  ],
  "strategic_roadmap": {{
    "p1_critical": ["action 1", "action 2"],
    "p2_strategic": ["action 1", "action 2"],
    "p3_routine": ["action 1", "action 2"]
  }},
  "risk_areas": [
    {{
      "risk": "description",
      "apps": ["affected apps"],
      "severity": "high/medium/low",
      "mitigation": "recommended action"
    }}
  ]
}}

Return ONLY valid JSON."""

    try:
        print(f"   🤖 Calling OpenAI GPT-4o for portfolio analysis...")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior enterprise architect specializing in application portfolio optimization and rationalization."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        print(f"   ✅ Portfolio analysis complete!")

        return result

    except Exception as e:
        print(f"   ❌ Error in portfolio analysis: {e}")
        return {"error": str(e)}

def save_portfolio_insights(insights: Dict, session):
    """Save portfolio-level insights to database"""

    model_version = "gpt-4o"

    # Save consolidation opportunities
    for opp in insights.get('consolidation_opportunities', []):
        portfolio_insight = PortfolioInsight(
            id=str(uuid.uuid4()),
            insight_type='consolidation',
            title=f"Consolidate: {', '.join(opp['apps'][:3])}",
            description=opp['rationale'],
            affected_apps=opp['apps'],
            priority=opp.get('priority', 'P2'),
            estimated_impact=opp.get('estimated_impact', 'medium'),
            complexity=opp.get('complexity', 'medium'),
            recommended_action=opp.get('target_state', ''),
            generated_at=datetime.utcnow(),
            model_version=model_version
        )
        session.add(portfolio_insight)

    # Save quick wins
    for win in insights.get('quick_wins', []):
        portfolio_insight = PortfolioInsight(
            id=str(uuid.uuid4()),
            insight_type='quick_win',
            title=win['opportunity'],
            description=win.get('roi', ''),
            affected_apps=win.get('apps', []),
            priority='P1',
            estimated_impact=win.get('impact', 'high'),
            complexity='low',
            recommended_action=win['opportunity'],
            generated_at=datetime.utcnow(),
            model_version=model_version
        )
        session.add(portfolio_insight)

    # Save risk areas
    for risk in insights.get('risk_areas', []):
        portfolio_insight = PortfolioInsight(
            id=str(uuid.uuid4()),
            insight_type='risk',
            title=risk['risk'],
            description=f"Severity: {risk['severity']} - {risk.get('mitigation', '')}",
            affected_apps=risk.get('apps', []),
            priority='P1' if risk['severity'] == 'high' else 'P2',
            estimated_impact=risk['severity'],
            complexity='medium',
            recommended_action=risk.get('mitigation', ''),
            generated_at=datetime.utcnow(),
            model_version=model_version
        )
        session.add(portfolio_insight)

    session.commit()
    print(f"   💾 Saved portfolio insights to database")

def run_full_insight_generation():
    """
    Main entry point: Generate all insights (per-app + portfolio-level)
    This is the one-time batch process that calls OpenAI API
    """

    session = get_session()

    try:
        print("\n" + "="*60)
        print("🚀 STARTING FULL INSIGHT GENERATION")
        print("="*60)

        # Clear existing insights
        print("\n🧹 Clearing old insights...")
        session.query(AppInsight).delete()
        session.query(PortfolioInsight).delete()
        session.commit()

        # Phase 1: Per-application analysis
        apps = session.query(Application).filter(Application.name != "Questions Template").all()
        print(f"\n📊 Phase 1: Analyzing {len(apps)} applications individually...")

        for idx, app in enumerate(apps, 1):
            print(f"\n[{idx}/{len(apps)}] {app.name}")

            insights = generate_app_insight(app, session)
            save_app_insights(app.id, insights, session)

        # Phase 2: Portfolio-level analysis
        print(f"\n📊 Phase 2: Portfolio-level pattern analysis...")
        portfolio_insights = generate_portfolio_insights(session)
        save_portfolio_insights(portfolio_insights, session)

        print("\n" + "="*60)
        print("✅ INSIGHT GENERATION COMPLETE!")
        print("="*60)
        print(f"\n📈 Results:")
        print(f"   - Applications analyzed: {len(apps)}")
        print(f"   - App insights created: {session.query(AppInsight).count()}")
        print(f"   - Portfolio insights created: {session.query(PortfolioInsight).count()}")
        print(f"\n💡 Insights are now available in the UI!")

    except Exception as e:
        print(f"\n❌ Error during insight generation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        close_session(session)

if __name__ == "__main__":
    run_full_insight_generation()
