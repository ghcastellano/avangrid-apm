"""
AI Processing module using OpenAI API
Handles transcript analysis, score suggestion, insights generation, and Q&A
"""

import os
import json
from typing import Dict, List, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()

# Initialize OpenAI client - support both .env and Streamlit secrets
def _get_openai_key():
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key
    try:
        import streamlit as st
        key = st.secrets.get("OPENAI_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return None

client = OpenAI(api_key=_get_openai_key())

# Master Questions (from existing system)
MASTER_QUESTIONS = {
    "Strategic Fit": [
        "What is the name of the application?",
        "What is the primary business purpose of the application?",
        "Which OPCOs use the application?",
        "Which utility domain(s) is the application used for? (Electric, Gas, or Both)",
        "Which Business Unit(s) use or own the application?",
        "Is the application IT-owned, business-owned, or jointly governed?",
        "Is this application considered business-critical, important, or supportive? Provide an explanation of the statement",
        "Does the application align with the current and future Mobility strategy?",
        "Are there important capabilities missing that limit business effectiveness?",
        "Is the application expected to be used in the next 3–5 years?",
        "Are there planned upgrades, migrations, or replacements?",
        "Could this application be replaced or consolidated with another platform?"
    ],
    "Business Efficiency": [
        "What key business processes does the application support?",
        "What core functionalities does the application provide?",
        "Are any processes partially supported or handled outside the application (manual workarounds, spreadsheets, etc.)?",
        "Does the application overlap functionally with other systems?",
        "Could this application absorb business processes currently supported by another platform or executed through manual workarounds? If yes, which processes and which platform(s)"
    ],
    "User Value": [
        "Which user roles or personas use the application (e.g., field technician, dispatcher, supervisor)?",
        "How many active users does the application have (daily/monthly)?",
        "Is application usage growing, stable, or declining?",
        "Is usage mandatory or optional for users?",
        "What is the overall level of user satisfaction?",
        "Are there known usability or mobility experience issues?"
    ],
    "Financial Value": [
        "What business value does the application deliver today?",
        "What would be the business impact if the application were unavailable?",
        "What are the main cost components (licenses, infrastructure, support)?, and what is the total cost of ownership?",
        "Is the cost reasonable compared to the business value delivered?",
        "Are there upcoming license renewals or contract milestones?",
        "Are there opportunities for cost reduction through consolidation or modernization?"
    ],
    "Architecture": [
        "Is the application a custom-built solution or a market (COTS/SaaS) product?",
        "What platforms does the application run on (mobile OS, web, backend)?",
        "What technologies, frameworks, or programming languages are used?",
        "What version of the application is currently deployed?",
        "Is the application deployed on-premises, in the cloud, or in a hybrid model?",
        "If cloud-based, which hyperscaler or cloud provider is used (e.g., AWS, Azure, GCP)?",
        "Which systems does the application integrate with?",
        "Are integrations real-time, batch-based, or manual?",
        "What limits future evolution or innovation?"
    ],
    "Operational Risk": [
        "Does the application support regulatory and compliance requirements?",
        "How critical are these integrations to business operations?",
        "What type of data does the application create, consume, or update?",
        "Are there known integration or data quality issues?",
        "Does the application handle sensitive, personal, or regulated data?",
        "Is the application governed by corporate security and IT policies?",
        "Is identity and access management (IAM) integrated with corporate IAM solutions?",
        "Are security controls (authentication, authorization, logging) centrally managed or application-specific?",
        "Are there known security risks, audit findings, or compliance gaps?"
    ],
    "Maintainability": [
        "How complex is ongoing maintenance and support?",
        "How frequently are incidents or defects reported?",
        "How easy is it to implement enhancements or changes?",
        "What are the main business challenges with the application?",
        "What are the main technical challenges or limitations?",
        "Are there scalability, performance, or reliability concerns?",
        "Are stakeholders requesting changes or replacement?"
    ],
    "Support Quality": [
        "Is vendor or technology support still available and active?",
        "Who provides application support (internal IT, vendor, third party)?",
        "Is the application proactively monitored (e.g., APM, Dynatrace), or is downtime primarily reported by users?",
        "Are alerts integrated with ITSM tools (e.g., ServiceNow) for auto-ticketing, or are they email-based/manual?"
    ]
}

# Synergy Block Definitions
SYNERGY_BLOCKS = {
    "Strategic Fit": {"Type": "Business", "Weight": 30},
    "Business Efficiency": {"Type": "Business", "Weight": 30},
    "User Value": {"Type": "Business", "Weight": 20},
    "Financial Value": {"Type": "Business", "Weight": 20},
    "Architecture": {"Type": "Tech", "Weight": 30},
    "Operational Risk": {"Type": "Tech", "Weight": 30},
    "Maintainability": {"Type": "Tech", "Weight": 25},
    "Support Quality": {"Type": "Tech", "Weight": 15}
}

def extract_answers_from_transcript(transcript_text: str, application_name: str = None) -> Dict:
    """
    Extract answers to master questions from a meeting transcript using OpenAI.

    Args:
        transcript_text: The full transcript text
        application_name: Optional application name for context

    Returns:
        Dict with structure: {
            "answers": [{"question": str, "answer": str, "confidence": float, "synergy_block": str, "source_excerpt": str}],
            "summary": str
        }
    """

    # Flatten all questions
    all_questions = []
    question_to_block = {}
    for block, questions in MASTER_QUESTIONS.items():
        for q in questions:
            all_questions.append(q)
            question_to_block[q] = block

    # Create prompt
    prompt = f"""You are an expert consultant analyzing application assessment meeting transcripts.

Application Name: {application_name or "Unknown"}

Your task is to extract answers to specific questions from the following meeting transcript.

TRANSCRIPT:
{transcript_text[:15000]}  # Limit to ~15k chars to avoid token limits

QUESTIONS TO ANSWER:
{json.dumps(all_questions, indent=2)}

For each question:
1. If the transcript contains information to answer it, extract the answer
2. Provide a confidence score (0.0 to 1.0) indicating how confident you are
3. Include a brief excerpt from the transcript that supports your answer
4. If no information found, return null for that question

IMPORTANT ANALYSIS GUIDELINES:
- Analyze deeply, not superficially
- Consider implicit mentions (e.g., "we have frequent issues" → low maintainability)
- Look for sentiment and tone
- Cross-reference information across different parts of the transcript
- Be conservative with confidence scores - only use >0.8 for explicit, clear answers

Output format (JSON):
{{
  "answers": [
    {{
      "question": "question text",
      "answer": "extracted answer or null",
      "confidence": 0.0-1.0,
      "source_excerpt": "relevant transcript excerpt or null"
    }}
  ],
  "summary": "Brief 2-3 sentence summary of what was discussed in this meeting"
}}

Return ONLY valid JSON, no other text.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cost-effective model with excellent performance
            messages=[
                {"role": "system", "content": "You are an expert application portfolio management consultant. You analyze transcripts deeply and extract structured information accurately."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # Add synergy block to each answer
        for answer in result.get("answers", []):
            question = answer.get("question", "")
            answer["synergy_block"] = question_to_block.get(question, "Unknown")

        return result

    except Exception as e:
        print(f"Error extracting answers from transcript: {e}")
        return {"answers": [], "summary": "Error processing transcript", "error": str(e)}


def suggest_scores(questionnaire_answers: Dict, transcript_answers: List[Dict]) -> Dict:
    """
    Suggest synergy block scores based on questionnaire and transcript answers.

    Args:
        questionnaire_answers: Dict of {question: answer} from original questionnaire
        transcript_answers: List of extracted answers from transcripts

    Returns:
        Dict with structure: {
            "scores": {
                "Block Name": {
                    "score": 1-5,
                    "confidence": 0.0-1.0,
                    "rationale": "explanation"
                }
            }
        }
    """

    # Combine all answers and track which blocks have data
    combined_answers = []
    blocks_with_data = set()

    for question, answer_obj in questionnaire_answers.items():
        answer_text = answer_obj.get("a", "")
        if answer_text and answer_text.strip():
            combined_answers.append({
                "question": question,
                "answer": answer_text,
                "source": "questionnaire"
            })
            # Find which block this question belongs to
            for block_name, questions in MASTER_QUESTIONS.items():
                if question in questions:
                    blocks_with_data.add(block_name)
                    break

    for ta in transcript_answers:
        if ta.get("answer") and ta.get("confidence", 0) > 0.5:
            combined_answers.append({
                "question": ta.get("question", ""),
                "answer": ta.get("answer", ""),
                "source": "transcript",
                "confidence": ta.get("confidence", 0)
            })
            # Find which block this question belongs to
            question_text = ta.get("question", "")
            for block_name, questions in MASTER_QUESTIONS.items():
                if question_text in questions:
                    blocks_with_data.add(block_name)
                    break

    # Log processing info
    print(f"[AI_PROCESSOR] Preparing to call OpenAI for score suggestion...")
    print(f"[AI_PROCESSOR] Blocks with data: {blocks_with_data}")
    print(f"[AI_PROCESSOR] Total answers to process: {len(combined_answers)}")

    # Create prompt
    prompt = f"""You are an expert application portfolio management consultant using the APM Strategic Framework.

Your task is to analyze all available answers and suggest scores (1-5) for each of the 8 synergy blocks.

SYNERGY BLOCKS AND THEIR MEANINGS:
1. Strategic Fit (Business): How well the application aligns with business strategy
   - 1: Completely misaligned
   - 2: Partially aligned
   - 3: Neutral
   - 4: Well-aligned
   - 5: Strategic driver

2. Business Efficiency (Business): Level of process automation and efficiency
   - 1: Manual
   - 2: Low efficiency
   - 3: Average
   - 4: High
   - 5: Optimized

3. User Value (Business): User satisfaction and value perception
   - 1: Rejected
   - 2: Low satisfaction
   - 3: Acceptable
   - 4: Good
   - 5: Delightful

4. Financial Value (Business): Cost-benefit ratio and ROI
   - 1: Negative
   - 2: Poor
   - 3: Neutral
   - 4: Positive
   - 5: Exceptional

5. Architecture (Tech): Technology stack modernity and scalability
   - 1: Obsolete
   - 2: Aging
   - 3: Stable
   - 4: Modern
   - 5: Future-proof

6. Operational Risk (Tech): Security, compliance, and reliability
   - 1: Critical risk
   - 2: High risk
   - 3: Managed
   - 4: Low risk
   - 5: Fortified

7. Maintainability (Tech): Ease of maintenance and enhancement
   - 1: Impossible
   - 2: Hard
   - 3: Standard
   - 4: Good
   - 5: Excellent

8. Support Quality (Tech): Quality and availability of support
   - 1: Non-existent
   - 2: Reactive
   - 3: Defined
   - 4: Proactive
   - 5: World-class

AVAILABLE ANSWERS:
{json.dumps(combined_answers, indent=2)[:10000]}

SCORING GUIDELINES:
- Only score blocks where you have sufficient information from the available answers
- Analyze deeply: look for patterns, implicit signals, sentiment
- Negative keywords (manual, legacy, obsolete, gaps, issues, poor) → lower scores
- Positive keywords (automated, modern, strategic, optimized, satisfied) → higher scores
- Be contextual: "stable" might be good for Architecture but "stable usage" might be neutral for User Value
- Provide detailed rationale for each score based on the evidence

Output format (JSON):
{{
  "scores": {{
    "Strategic Fit": {{
      "score": 1-5,
      "confidence": 0.0-1.0,
      "rationale": "detailed explanation considering the answers"
    }},
    ... (repeat for all 8 blocks)
  }}
}}

Return ONLY valid JSON, no other text.
"""

    try:
        print(f"[AI_PROCESSOR] 🤖 Calling OpenAI API (gpt-4o-mini)...")
        import time
        start_time = time.time()

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cost-effective model with excellent performance
            messages=[
                {"role": "system", "content": "You are an expert application portfolio management consultant with deep experience in IT assessment and scoring frameworks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        elapsed_time = time.time() - start_time
        print(f"[AI_PROCESSOR] ✅ OpenAI response received in {elapsed_time:.2f}s")

        result = json.loads(response.choices[0].message.content)
        print(f"[AI_PROCESSOR] Scores generated for {len(result.get('scores', {}))} blocks")

        # Override scores for blocks with no data
        blocks_overridden = []
        if "scores" in result:
            for block_name in SYNERGY_BLOCKS.keys():
                if block_name not in blocks_with_data:
                    # No data available for this block - assign conservative defaults
                    result["scores"][block_name] = {
                        "score": 2,
                        "confidence": 0.2,
                        "rationale": "⚠️ NO DATA - Conservative score assigned due to lack of responses. Manual review recommended."
                    }
                    blocks_overridden.append(block_name)

        if blocks_overridden:
            print(f"[AI_PROCESSOR] ⚠️  Overridden {len(blocks_overridden)} blocks with no data: {blocks_overridden}")

        print(f"[AI_PROCESSOR] ✅ Score suggestion complete!")
        return result

    except Exception as e:
        print(f"Error suggesting scores: {e}")
        # Return default scores for all blocks
        return {
            "scores": {
                block: {
                    "score": 2,
                    "confidence": 0.2,
                    "rationale": f"⚠️ ERROR - {str(e)}"
                }
                for block in SYNERGY_BLOCKS.keys()
            }
        }


def generate_insights(applications_data: List[Dict]) -> List[Dict]:
    """
    Generate portfolio-wide insights using OpenAI.

    Args:
        applications_data: List of application data with scores and answers

    Returns:
        List of insights
    """

    # Prepare summary of applications
    apps_summary = []
    for app in applications_data[:20]:  # Limit to 20 apps to avoid token limits
        apps_summary.append({
            "name": app.get("name"),
            "bvi": app.get("bvi", 0),
            "thi": app.get("thi", 0),
            "recommendation": app.get("recommendation", "Unknown"),
            "key_facts": {
                "business_critical": app.get("business_critical", "Unknown"),
                "technology": app.get("technology", "Unknown"),
                "cost": app.get("cost", "Unknown"),
                "integrations": app.get("integrations", [])
            }
        })

    prompt = f"""You are a senior technology consultant preparing strategic insights for an Avangrid application portfolio assessment.

PORTFOLIO SUMMARY:
{json.dumps(apps_summary, indent=2)}

Generate 5-8 actionable insights covering:

1. Integration Opportunities: Which apps have functional overlap and could be consolidated?
2. Absorption Plans: For apps recommended to ELIMINATE, which other apps could absorb their functionality?
3. Technology Updates: Which apps need modernization (cloud, microservices, etc.)?
4. Risk Analysis: Which critical apps have low technical health?
5. Financial Optimization: High-cost, low-value apps
6. Quick Wins: Easy improvements with high impact

For each insight:
- Be specific (mention app names)
- Be actionable (what to do)
- Estimate priority (P1: urgent, P2: important, P3: nice-to-have)
- Keep it concise (2-3 sentences max)

Output format (JSON):
{{
  "insights": [
    {{
      "type": "integration|absorption|technology_update|risk|financial|quick_win",
      "title": "Short title",
      "description": "2-3 sentence description",
      "priority": "P1|P2|P3",
      "affected_apps": ["app1", "app2"],
      "recommendation": "EVOLVE|INVEST|MAINTAIN|ELIMINATE or null"
    }}
  ]
}}

Return ONLY valid JSON, no other text.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cost-effective model with excellent performance
            messages=[
                {"role": "system", "content": "You are a senior technology strategy consultant with expertise in application portfolio management and IT modernization."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)
        return result.get("insights", [])

    except Exception as e:
        print(f"Error generating insights: {e}")
        return []


def answer_question(question: str, context_data: Dict) -> Tuple[str, List[str]]:
    """
    Answer a user question about the portfolio using RAG approach.

    Args:
        question: User's question
        context_data: Relevant context (applications, answers, scores)

    Returns:
        Tuple of (answer, sources)
    """

    # Prepare context - MUCH more generous limit for rich context
    context_summary = json.dumps(context_data, indent=2)[:50000]  # Increased from 8000 to 50000 characters

    prompt = f"""You are a senior business and technical consultant at Avangrid with deep expertise in application portfolio management. You have conducted extensive stakeholder interviews, analyzed documentation, and understand the business and technical landscape intimately.

USER QUESTION:
{question}

AVAILABLE CONTEXT FROM YOUR RESEARCH:
{context_summary}

YOUR KNOWLEDGE BASE (Prioritize High-Confidence Data):
1. **Stakeholder Interviews** - Direct insights from users, SMEs, and business owners
2. **Meeting Transcripts (High confidence ≥70%)** - Validated information from discussions
3. **Application Documentation** - Technical specs, user requirements, integrations
4. **Operational Context** - Business processes, user satisfaction, technical challenges

HOW TO RESPOND AS AN AVANGRID EXPERT:

**CRITICAL: Think like a consultant, not a scoring system**
- Focus on business impact, user needs, technical realities, operational dependencies
- NEVER lead with scores or metrics (BVI/THI) unless specifically asked
- Start with business context, technical details, user feedback, real-world impact

**Prioritize high-confidence qualitative data**:
✓ Direct quotes from stakeholders and SMEs
✓ Technical specifications and architecture details
✓ User satisfaction feedback with ≥70% confidence
✓ Business-critical process dependencies
✓ Regulatory, compliance, or safety considerations

**Be specific and actionable**:
- Name specific users, teams, or business units affected
- Describe technical architectures, integrations, vendor relationships
- Explain business processes supported and operational impacts
- Mention what would happen if the application failed
- Include user sentiment and pain points

**Provide business and technical depth**:
- WHY does this application matter to Avangrid's operations?
- WHAT business processes depend on it?
- WHO are the users and what do they say about it?
- WHAT technical debt, risks, or challenges exist?
- WHAT alternatives or consolidation opportunities exist?

**Trust hierarchy for conflicting data**:
David's stakeholder notes > High-confidence transcripts (≥70%) > Documentation > Scores

**AVOID**:
❌ Starting responses with "BVI is X, THI is Y"
❌ Generic statements without specific operational context
❌ Relying on scores when rich qualitative data exists
❌ Technical jargon without business translation

Format your response as:
[Your expert analysis with business and technical context - consulting quality]

Sources:
- [Application Name - Source Type]
"""

    try:
        start_time = time.time()

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cost-effective model with excellent performance
            messages=[
                {"role": "system", "content": "You are a senior Avangrid business and technical consultant with 15+ years of experience in electric/gas utility operations and application portfolio management. You provide strategic, context-rich insights based on stakeholder interviews and operational knowledge. You NEVER lead with scores - you lead with business impact, technical reality, and user needs. You never make up information."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # Slightly higher for more natural consulting voice
        )

        response_time = int((time.time() - start_time) * 1000)

        answer_text = response.choices[0].message.content

        # Extract sources (simple parsing)
        sources = []
        if "Sources:" in answer_text:
            parts = answer_text.split("Sources:")
            answer = parts[0].strip()
            sources_text = parts[1].strip()
            sources = [s.strip("- ").strip() for s in sources_text.split("\n") if s.strip()]
        else:
            answer = answer_text

        return answer, sources, response_time

    except Exception as e:
        print(f"Error answering question: {e}")
        return f"Error processing question: {e}", [], 0


def calculate_bvi_thi(scores: Dict, custom_weights: Dict = None) -> Tuple[float, float]:
    """
    Calculate BVI and THI from synergy block scores using weighted averages.

    Args:
        scores: Dict of {block_name: score}
        custom_weights: Optional dict of {block_name: weight}. If None, uses SYNERGY_BLOCKS weights.

    Returns:
        Tuple of (BVI, THI)
    """

    # Use custom weights if provided, otherwise use default SYNERGY_BLOCKS
    weights = custom_weights if custom_weights else SYNERGY_BLOCKS

    business_blocks = ["Strategic Fit", "Business Efficiency", "User Value", "Financial Value"]
    tech_blocks = ["Architecture", "Operational Risk", "Maintainability", "Support Quality"]

    # Calculate BVI (Business Value Index) using weighted average
    bvi_sum = 0
    bvi_weight_sum = 0
    for block in business_blocks:
        score = scores.get(block, 1)
        weight = weights.get(block, {}).get('Weight', 25) if isinstance(weights.get(block), dict) else weights.get(block, 25)
        bvi_sum += score * weight
        bvi_weight_sum += weight

    bvi = (bvi_sum / bvi_weight_sum) * 20 if bvi_weight_sum > 0 else 0  # Scale to 0-100

    # Calculate THI (Technical Health Index) using weighted average
    thi_sum = 0
    thi_weight_sum = 0
    for block in tech_blocks:
        score = scores.get(block, 1)
        weight = weights.get(block, {}).get('Weight', 25) if isinstance(weights.get(block), dict) else weights.get(block, 25)
        thi_sum += score * weight
        thi_weight_sum += weight

    thi = (thi_sum / thi_weight_sum) * 20 if thi_weight_sum > 0 else 0  # Scale to 0-100

    return round(bvi, 1), round(thi, 1)


def get_recommendation(bvi: float, thi: float) -> str:
    """
    Get strategic recommendation based on BVI and THI.

    Args:
        bvi: Business Value Index (0-100)
        thi: Technical Health Index (0-100)

    Returns:
        Recommendation string
    """

    if bvi >= 60 and thi >= 60:
        return "EVOLVE"
    elif bvi >= 60 and thi < 60:
        return "INVEST"
    elif bvi < 60 and thi >= 60:
        return "MAINTAIN"
    else:
        return "ELIMINATE"


def get_subcategory_and_priority_detail(recommendation: str, bvi: float, thi: float, arch_score: float, maint_score: float) -> Tuple[str, str]:
    """
    Get subcategory and detailed priority based on recommendation and metrics.

    Args:
        recommendation: Strategic recommendation (EVOLVE, INVEST, MAINTAIN, ELIMINATE)
        bvi: Business Value Index (0-100)
        thi: Technical Health Index (0-100)
        arch_score: Architecture score (1-5)
        maint_score: Maintainability score (1-5)

    Returns:
        Tuple of (subcategory, priority_detail)
    """

    if recommendation == 'ELIMINATE':
        if thi < 40:
            return ('Replace', 'P1 - Critical')
        elif bvi > 50:
            return ('Retire', 'P1 - Critical')
        else:
            return ('Absorbed', 'P2 - Tactical')
    elif recommendation == 'INVEST':
        return ('Absorb', 'P1 - Critical')
    elif recommendation == 'EVOLVE':
        if arch_score <= 2:
            return ('Modernize', 'P1 - Critical')
        elif maint_score <= 2:
            return ('Migrate', 'P1 - Critical')
        elif bvi > 75:
            return ('Enhance', 'P2 - Strategic')
        elif thi < 75:
            return ('Refactor', 'P2 - Strategic')
        else:
            return ('Upgrade', 'P2 - Strategic')
    elif recommendation == 'MAINTAIN':
        if bvi > 50:
            return ('Internalize', 'P2 - Compliance')
        else:
            return ('Maintain', 'P3 - Routine')

    return ('Unknown', 'P3 - Routine')


def extract_dependencies_info(app_id: str, session) -> Dict:
    """
    Extract dependency information for an application.

    Args:
        app_id: Application ID
        session: Database session

    Returns:
        Dict with keys: count, type, systems, display
    """

    # This is a placeholder function - dependency tracking would need to be implemented
    # For now, return empty/default values
    return {
        'count': 0,
        'type': 'None',
        'systems': [],
        'display': 'No dependencies tracked'
    }
