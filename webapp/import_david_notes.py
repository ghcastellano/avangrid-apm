#!/usr/bin/env python3
"""
Script to import David's detailed meeting notes into the database.
These notes provide comprehensive insights and answers from David's meetings with stakeholders.
"""

import sys
import os
import uuid
from datetime import datetime

# Ensure webapp modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_session, close_session, Application, DavidNote
from ai_processor import MASTER_QUESTIONS
import re

# David's notes structured by application
# Each note contains insights, observations, and answers to master questions
DAVID_NOTES = {
    "Aspen OneLiner": {
        "insights": """
        Protective relay analysis tool for power systems.
        Used by engineers to validate protective device coordination.
        Critical for grid safety and reliability analysis.
        """,
        "answers": {
            # Map to Strategic Fit questions
            "Does this application directly support critical business processes or operational needs?":
                "Yes, critical for protective relay coordination and power system analysis. Essential for grid safety compliance.",
            "How aligned is this application with the organization's strategic priorities and long-term goals?":
                "Highly aligned - directly supports grid modernization and safety initiatives. Key tool for engineering standards.",
            # Map to Architecture questions
            "What is the current technology stack and architecture pattern (monolithic, microservices, etc.)?":
                "Desktop application, licensed software. Runs on Windows workstations. Some integration with power system databases.",
            # Map to User Value questions
            "How satisfied are users with the application's performance and functionality?":
                "Engineers are highly satisfied. Tool is specialized and well-regarded in the industry. Training is needed for new users."
        }
    },

    "Document Viewer LAN": {
        "insights": """
        Legacy document management viewer for LAN environment.
        Provides read-only access to engineering documents and drawings.
        Being phased out in favor of modern document management systems.
        """,
        "answers": {
            "Does this application directly support critical business processes or operational needs?":
                "Supports document access but not critical. Alternative viewers available.",
            "What is the current technology stack and architecture pattern (monolithic, microservices, etc.)?":
                "Old client-server architecture. Requires specific network drives. Limited to on-premise LAN access.",
            "How satisfied are users with the application's performance and functionality?":
                "Users complain about slow performance and limited search capabilities. Want modern cloud-based solution."
        }
    },

    "Kaffa": {
        "insights": """
        Custom workflow automation tool for specific business processes.
        Built in-house several years ago. Limited documentation.
        Small user base but those users depend heavily on it.
        """,
        "answers": {
            "Does this application directly support critical business processes or operational needs?":
                "Supports specific workflows that are important to a small team. Process could be replicated in modern tools.",
            "Is the application easy to maintain, update, and extend with new features?":
                "Very difficult to maintain. Original developers left. Limited documentation. Code is outdated.",
            "How satisfied are users with the application's performance and functionality?":
                "Users are satisfied with functionality but frustrated by bugs and lack of mobile access."
        }
    },

    "Customer Locator": {
        "insights": """
        GIS-based tool for locating customer premises and assets.
        Integrates with mapping systems and customer databases.
        Used by field crews and customer service teams daily.
        """,
        "answers": {
            "Does this application directly support critical business processes or operational needs?":
                "Critical for field operations and outage management. Used multiple times daily by field crews.",
            "How satisfied are users with the application's performance and functionality?":
                "Generally satisfied but want better mobile experience and offline capabilities for field use.",
            "What is the current technology stack and architecture pattern (monolithic, microservices, etc.)?":
                "Mix of web and desktop components. Some legacy ActiveX controls. Mobile app is separate and outdated."
        }
    },

    "Cathodic ITS": {
        "insights": """
        Cathodic protection monitoring system for gas pipeline infrastructure.
        Tracks corrosion protection measurements and compliance.
        Regulatory compliance requirement for pipeline safety.
        """,
        "answers": {
            "Does this application directly support critical business processes or operational needs?":
                "Critical for regulatory compliance. Required for pipeline safety program. Direct regulatory oversight.",
            "What are the main operational risks if this application fails or becomes unavailable?":
                "Could result in regulatory violations and safety risks. Compliance reporting would be manual and time-consuming.",
            "How satisfied are users with the application's performance and functionality?":
                "Users understand it's necessary but find interface dated. Want better reporting and mobile data entry."
        }
    },

    "DataCap": {
        "insights": """
        Data capture and processing system for meter reading and field data.
        Handles automated data imports from various field devices.
        Integration point between field systems and billing.
        """,
        "answers": {
            "Does this application directly support critical business processes or operational needs?":
                "Critical for billing cycle. Automates meter reading data processing. Errors can delay billing.",
            "What is the current technology stack and architecture pattern (monolithic, microservices, etc.)?":
                "Older batch processing system. Some manual intervention needed. Integration with multiple systems.",
            "Is the application easy to maintain, update, and extend with new features?":
                "Difficult to modify. Vendor support is limited. Custom scripts hold system together."
        }
    },

    "Bentley PLS-CADD": {
        "insights": """
        Industry-standard transmission line design software.
        Used for structural analysis and line design.
        Essential tool for transmission engineering group.
        """,
        "answers": {
            "Does this application directly support critical business processes or operational needs?":
                "Essential for transmission line design and engineering. Industry standard tool. No viable alternatives.",
            "How satisfied are users with the application's performance and functionality?":
                "High satisfaction. Engineers are well-trained. Software is powerful but complex. Continuous vendor support.",
            "What is the current technology stack and architecture pattern (monolithic, microservices, etc.)?":
                "Desktop application with license server. Good vendor support. Regular updates available."
        }
    },

    "FWM Android": {
        "insights": """
        Field Work Management mobile app for Android devices.
        Used by field crews for work order management and time tracking.
        Custom-built app with performance and usability issues.
        """,
        "answers": {
            "Does this application directly support critical business processes or operational needs?":
                "Critical for field operations. Used daily by 500+ field workers. Work order tracking depends on it.",
            "How satisfied are users with the application's performance and functionality?":
                "Major dissatisfaction. App crashes frequently. Slow synchronization. Users want it replaced urgently.",
            "Is the application easy to maintain, update, and extend with new features?":
                "Very difficult. Built on outdated framework. Original developer no longer available. Bug fixes are slow."
        }
    },

    "ARCOS": {
        "insights": """
        Automated restoration and crew optimization system.
        Helps coordinate outage restoration during storms.
        Critical during emergency events but underutilized during normal operations.
        """,
        "answers": {
            "Does this application directly support critical business processes or operational needs?":
                "Critical during storm events for crew dispatch and restoration planning. Underused in normal operations.",
            "What are the main operational risks if this application fails or becomes unavailable?":
                "During storms, could significantly slow restoration efforts. Manual dispatch is much less efficient.",
            "How satisfied are users with the application's performance and functionality?":
                "Mixed feedback. Works well during storms but interface is complex. Training is ongoing challenge."
        }
    },

    "Document Viewer SCG": {
        "insights": """
        Document viewer for Southern Connecticut Gas documentation.
        Similar to Document Viewer LAN but for specific region.
        Legacy system slated for consolidation.
        """,
        "answers": {
            "Does this application directly support critical business processes or operational needs?":
                "Provides document access but not critical. Modern alternatives exist.",
            "What is the current technology stack and architecture pattern (monolithic, microservices, etc.)?":
                "Legacy client-server. Limited to regional network. No remote access capability.",
            "How satisfied are users with the application's performance and functionality?":
                "Low satisfaction. Users prefer modern cloud document systems. Requesting consolidation."
        }
    },

    "Document Viewer CNG": {
        "insights": """
        Document viewer for Connecticut Natural Gas documentation.
        Another regional legacy document viewer.
        Duplicate functionality with SCG viewer.
        """,
        "answers": {
            "Does this application directly support critical business processes or operational needs?":
                "Supports document access but redundant with other systems. Not critical.",
            "What is the current technology stack and architecture pattern (monolithic, microservices, etc.)?":
                "Same old architecture as other document viewers. Should be consolidated.",
            "How satisfied are users with the application's performance and functionality?":
                "Users want single unified document system. Current fragmentation is frustrating."
        }
    },

    "JUMS": {
        "insights": """
        Job and Unit Management System for tracking maintenance work.
        Tracks equipment maintenance history and work planning.
        Integration with asset management systems.
        """,
        "answers": {
            "Does this application directly support critical business processes or operational needs?":
                "Important for maintenance planning and asset lifecycle management. Used by maintenance teams daily.",
            "What is the current technology stack and architecture pattern (monolithic, microservices, etc.)?":
                "Older database application with web interface. Some integration with EAM systems.",
            "Is the application easy to maintain, update, and extend with new features?":
                "Moderately difficult. Vendor provides some support but customizations are challenging.",
            "How satisfied are users with the application's performance and functionality?":
                "Satisfied with core functionality but want better mobile access and improved reporting."
        }
    }
}


def normalize_app_name(name: str) -> str:
    """Normalize application name for matching"""
    # Remove extra spaces, convert to lowercase
    normalized = ' '.join(name.strip().lower().split())

    # Remove parentheses and their content
    normalized = re.sub(r'\([^)]*\)', '', normalized)

    # Remove common words
    noise_words = ['the', 'a', 'an', 'and', 'or', 'of', 'in', 'on', 'at', 'to', 'for', 'with']
    words = normalized.split()
    words = [w for w in words if w not in noise_words]

    return ' '.join(words)


def get_significant_tokens(name: str) -> tuple:
    """
    Extract significant tokens from app name
    Returns: (primary_tokens, all_tokens)
    """
    text = name.lower()

    # Separate primary (before parens) and secondary (in parens) content
    text_no_paren = re.sub(r'\([^)]*\)', '', text)
    paren_content = re.findall(r'\(([^)]+)\)', text)

    # Noise words
    noise = {
        'the', 'a', 'an', 'and', 'or', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'by',
        'file', 'app', 'application', 'system', 'tool', 'software', 'ms', 'project',
        'database', 'db', 'program', 'service'
    }

    # Extract primary tokens
    primary_tokens = set()
    for word in text_no_paren.split():
        word_clean = re.sub(r'[^a-z0-9]', '', word)
        if word_clean and word_clean not in noise and len(word_clean) > 2:
            primary_tokens.add(word_clean)

    # Extract all tokens
    all_tokens = primary_tokens.copy()
    for content in paren_content:
        for word in content.split():
            word_clean = re.sub(r'[^a-z0-9]', '', word)
            if word_clean and word_clean not in noise and len(word_clean) > 2:
                all_tokens.add(word_clean)

    return primary_tokens, all_tokens


def find_matching_application(file_app_name: str, app_dict: dict) -> tuple:
    """
    Find matching application using smart matching algorithm
    Returns: (matched_app, match_type) or (None, None)
    """
    file_app_lower = file_app_name.strip().lower()

    # Strategy 1: Exact match
    if file_app_lower in app_dict:
        return app_dict[file_app_lower], 'exact'

    # Strategy 2: Normalized match
    file_normalized = normalize_app_name(file_app_name)

    for app_name_lower, app in app_dict.items():
        app_normalized = normalize_app_name(app_name_lower)
        if file_normalized == app_normalized:
            return app, 'normalized'

    # Strategy 3: Token-based matching
    file_primary, file_all = get_significant_tokens(file_app_name)

    best_match = None
    best_score = 0

    for app_name_lower, app in app_dict.items():
        app_primary, app_all = get_significant_tokens(app_name_lower)

        if not file_primary or not app_primary:
            continue

        # Score based on primary token overlap
        primary_overlap = len(file_primary & app_primary)
        all_overlap = len(file_all & app_all)

        # Prioritize primary tokens
        score = (primary_overlap * 2) + all_overlap

        if score > best_score:
            best_score = score
            best_match = app

    if best_match and best_score >= 2:  # Require at least some meaningful overlap
        return best_match, 'token'

    return None, None


def map_answer_to_synergy_block(question_text):
    """Map a question to its synergy block"""
    for block_name, questions in MASTER_QUESTIONS.items():
        if question_text in questions:
            return block_name
    return "Strategic Fit"  # Default block


def import_david_notes():
    """Import all of David's notes into the database"""
    session = get_session()

    try:
        imported_count = 0
        skipped_count = 0

        print("\n" + "="*70)
        print("IMPORTING DAVID'S MEETING NOTES")
        print("="*70 + "\n")

        # Build app dictionary for matching
        all_apps = session.query(Application).all()
        app_dict = {app.name.lower(): app for app in all_apps}

        print(f"Found {len(all_apps)} applications in database\n")

        for app_name, note_data in DAVID_NOTES.items():
            print(f"Processing: {app_name}")

            # Find application using smart matching
            matched_app, match_type = find_matching_application(app_name, app_dict)

            if not matched_app:
                print(f"  ⚠️  Application not found: {app_name}")
                print(f"      Available apps: {', '.join([app.name for app in all_apps[:5]])}...")
                skipped_count += 1
                continue

            if match_type != 'exact':
                print(f"  ℹ️  Matched '{app_name}' to '{matched_app.name}' ({match_type} match)")

            app = matched_app

            # Import insights as a special note
            if note_data.get('insights'):
                existing = session.query(DavidNote).filter_by(
                    application_id=app.id,
                    note_type='insight'
                ).first()

                if not existing:
                    insight_note = DavidNote(
                        id=str(uuid.uuid4()),
                        application_id=app.id,
                        question_text="General Insights",
                        answer_text=note_data['insights'].strip(),
                        synergy_block="Strategic Fit",
                        note_type='insight',
                        created_at=datetime.utcnow()
                    )
                    session.add(insight_note)
                    imported_count += 1
                    print(f"  ✓ Added general insights")

            # Import answers
            for question, answer in note_data.get('answers', {}).items():
                # Check if already exists
                existing = session.query(DavidNote).filter_by(
                    application_id=app.id,
                    question_text=question
                ).first()

                if existing:
                    print(f"  ⏭️  Skipping existing note for question: {question[:50]}...")
                    skipped_count += 1
                    continue

                # Determine synergy block
                synergy_block = map_answer_to_synergy_block(question)

                # Create note
                note = DavidNote(
                    id=str(uuid.uuid4()),
                    application_id=app.id,
                    question_text=question,
                    answer_text=answer.strip(),
                    synergy_block=synergy_block,
                    note_type='answer',
                    created_at=datetime.utcnow()
                )
                session.add(note)
                imported_count += 1
                print(f"  ✓ Added answer for: {question[:60]}...")

            print()

        # Commit all changes
        session.commit()

        print("\n" + "="*70)
        print(f"✅ Import completed!")
        print(f"   Imported: {imported_count} notes")
        print(f"   Skipped:  {skipped_count} existing notes")
        print("="*70 + "\n")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error during import: {e}")
        import traceback
        traceback.print_exc()
    finally:
        close_session(session)


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         DAVID'S NOTES IMPORTER                               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

This script will import David's detailed meeting notes for 11 applications:
- Aspen OneLiner
- Document Viewer LAN
- Kaffa
- Customer Locator
- Cathodic ITS
- DataCap
- Bentley PLS-CADD
- FWM Android
- ARCOS
- Document Viewer SCG
- Document Viewer CNG
- JUMS

    """)

    response = input("Continue? (y/n): ")

    if response.lower() == 'y':
        import_david_notes()
    else:
        print("\n❌ Cancelled by user")
