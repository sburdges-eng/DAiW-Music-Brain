"""
Collaborative Critique Protocol

A structured system for multi-AI feedback on musical compositions.
Each AI provides specialized critique from their domain of expertise.

Assigned to: ChatGPT

Features:
- Role-based critique (arrangement, harmony, production, emotional impact)
- Structured feedback format with actionable suggestions
- Consensus building for major issues
- Priority scoring for feedback items
- Integration with intent validation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime
import json


class CritiqueRole(Enum):
    """Specialized roles for critique."""
    ARRANGEMENT = "arrangement"      # Structure, instrumentation, dynamics
    HARMONY = "harmony"              # Chord choices, voice leading, key
    RHYTHM = "rhythm"                # Groove, timing, feel
    PRODUCTION = "production"        # Mix, sound design, sonic texture
    EMOTIONAL = "emotional"          # Emotional impact, intent alignment
    LYRICAL = "lyrical"              # Lyrics, phrasing, storytelling
    COMMERCIAL = "commercial"        # Accessibility, hooks, market fit
    ARTISTIC = "artistic"            # Creativity, uniqueness, risk-taking


class IssueSeverity(Enum):
    """How severe is the identified issue."""
    CRITICAL = "critical"      # Must fix - breaks the song
    IMPORTANT = "important"    # Should fix - significantly impacts quality
    SUGGESTION = "suggestion"  # Nice to have - would improve
    NITPICK = "nitpick"        # Minor detail - perfectionist territory


class IssueCategory(Enum):
    """Category of the identified issue."""
    TECHNICAL = "technical"          # Wrong notes, timing issues
    CREATIVE = "creative"            # Artistic choices
    INTENT_MISMATCH = "intent_mismatch"  # Doesn't match stated intent
    CONVENTION = "convention"        # Breaks conventions (may be intentional)
    ACCESSIBILITY = "accessibility"  # Hard to follow/understand
    BALANCE = "balance"              # Mix/arrangement balance


@dataclass
class CritiqueIssue:
    """A single issue identified during critique."""
    id: str
    category: IssueCategory
    severity: IssueSeverity
    title: str
    description: str
    location: Optional[str] = None     # e.g., "verse 2", "bar 16-20"
    suggestion: Optional[str] = None   # How to fix it
    reference: Optional[str] = None    # Example or resource
    intent_related: bool = False       # Does this relate to the song's stated intent?


@dataclass
class CritiqueStrength:
    """A strength or positive aspect identified."""
    id: str
    title: str
    description: str
    location: Optional[str] = None
    why_it_works: Optional[str] = None


@dataclass
class RoleCritique:
    """Critique from a single role/perspective."""
    role: CritiqueRole
    ai_name: str
    issues: List[CritiqueIssue] = field(default_factory=list)
    strengths: List[CritiqueStrength] = field(default_factory=list)
    overall_score: float = 0.0         # 0-10 rating from this perspective
    summary: str = ""
    timestamp: str = ""


@dataclass
class ConsensusItem:
    """An issue that multiple AIs agree on."""
    issue_title: str
    severity: IssueSeverity
    agreeing_roles: List[CritiqueRole]
    combined_suggestion: str
    priority_score: float              # Higher = more urgent to address


@dataclass
class CritiqueSession:
    """A complete critique session for a song/composition."""
    session_id: str
    song_title: Optional[str] = None
    intent_summary: Optional[str] = None

    role_critiques: List[RoleCritique] = field(default_factory=list)
    consensus_items: List[ConsensusItem] = field(default_factory=list)

    overall_score: float = 0.0
    top_priorities: List[str] = field(default_factory=list)
    top_strengths: List[str] = field(default_factory=list)

    created_at: str = ""
    finalized_at: Optional[str] = None


class CritiqueProtocol:
    """
    Orchestrates multi-perspective critique sessions.

    The protocol ensures structured, actionable feedback by:
    1. Assigning specialized roles to different AI perspectives
    2. Collecting independent critiques
    3. Finding consensus on major issues
    4. Prioritizing actionable feedback
    """

    def __init__(self):
        self.role_prompts = self._build_role_prompts()

    def _build_role_prompts(self) -> Dict[CritiqueRole, str]:
        """Build specialized prompts for each critique role."""
        return {
            CritiqueRole.ARRANGEMENT: """
You are critiquing ARRANGEMENT. Focus on:
- Song structure (intro, verse, chorus, bridge, outro)
- Instrumentation choices and layering
- Dynamic arc throughout the song
- Use of space and silence
- Build-ups and releases
- Section transitions
""",
            CritiqueRole.HARMONY: """
You are critiquing HARMONY. Focus on:
- Chord progression choices
- Key center and modulations
- Voice leading between chords
- Use of extensions and alterations
- Harmonic rhythm
- Resolution and tension patterns
""",
            CritiqueRole.RHYTHM: """
You are critiquing RHYTHM. Focus on:
- Groove and pocket
- Timing feel (ahead/behind the beat)
- Rhythmic variation and development
- Drum pattern choices
- Syncopation and accent patterns
- Tempo appropriateness
""",
            CritiqueRole.PRODUCTION: """
You are critiquing PRODUCTION. Focus on:
- Mix balance and clarity
- Frequency spectrum usage
- Stereo image and panning
- Use of effects (reverb, delay, etc.)
- Sound design choices
- Overall sonic quality and polish
""",
            CritiqueRole.EMOTIONAL: """
You are critiquing EMOTIONAL IMPACT. Focus on:
- Does it evoke the intended emotion?
- Emotional arc and journey
- Authenticity of expression
- Connection with the listener
- Memorability of emotional moments
- Alignment with stated intent
""",
            CritiqueRole.LYRICAL: """
You are critiquing LYRICS & PHRASING. Focus on:
- Lyrical content and meaning
- Word choice and imagery
- Rhyme scheme and flow
- Phrasing with the melody
- Hook effectiveness
- Story arc if narrative
""",
            CritiqueRole.COMMERCIAL: """
You are critiquing COMMERCIAL VIABILITY. Focus on:
- Hook strength and memorability
- Accessibility to general audiences
- Genre conventions met or broken
- Radio/streaming potential
- Current market trends alignment
- First-impression impact
""",
            CritiqueRole.ARTISTIC: """
You are critiquing ARTISTIC MERIT. Focus on:
- Originality and creativity
- Risk-taking and boundary pushing
- Artistic coherence and vision
- Unique sonic identity
- Innovation vs tradition balance
- Long-term artistic value
"""
        }

    def create_session(self, session_id: str,
                       song_title: Optional[str] = None,
                       intent_summary: Optional[str] = None) -> CritiqueSession:
        """Create a new critique session."""
        return CritiqueSession(
            session_id=session_id,
            song_title=song_title,
            intent_summary=intent_summary,
            created_at=datetime.now().isoformat()
        )

    def get_role_prompt(self, role: CritiqueRole) -> str:
        """Get the critique prompt for a role."""
        return self.role_prompts.get(role, "")

    def submit_critique(self, session: CritiqueSession,
                       critique: RoleCritique) -> None:
        """Submit a critique for a specific role."""
        critique.timestamp = datetime.now().isoformat()
        session.role_critiques.append(critique)

    def build_consensus(self, session: CritiqueSession) -> List[ConsensusItem]:
        """
        Analyze all critiques to find consensus items.
        Items mentioned by multiple roles get higher priority.
        """
        # Group similar issues
        issue_groups: Dict[str, List[Tuple[CritiqueRole, CritiqueIssue]]] = {}

        for critique in session.role_critiques:
            for issue in critique.issues:
                # Simple grouping by title similarity (could be smarter)
                key = issue.title.lower()
                if key not in issue_groups:
                    issue_groups[key] = []
                issue_groups[key].append((critique.role, issue))

        # Build consensus items for issues mentioned by multiple roles
        consensus_items = []
        for title, role_issues in issue_groups.items():
            if len(role_issues) >= 2:  # At least 2 AIs agree
                roles = [ri[0] for ri in role_issues]
                issues = [ri[1] for ri in role_issues]

                # Use highest severity
                severities = [i.severity for i in issues]
                severity_order = [IssueSeverity.CRITICAL, IssueSeverity.IMPORTANT,
                                 IssueSeverity.SUGGESTION, IssueSeverity.NITPICK]
                highest_severity = min(severities, key=lambda s: severity_order.index(s))

                # Combine suggestions
                suggestions = [i.suggestion for i in issues if i.suggestion]
                combined = "; ".join(suggestions) if suggestions else "Address this issue"

                # Priority score based on severity and agreement count
                severity_scores = {
                    IssueSeverity.CRITICAL: 10,
                    IssueSeverity.IMPORTANT: 7,
                    IssueSeverity.SUGGESTION: 4,
                    IssueSeverity.NITPICK: 1
                }
                priority = severity_scores[highest_severity] * len(roles) / 2

                consensus_items.append(ConsensusItem(
                    issue_title=title.title(),
                    severity=highest_severity,
                    agreeing_roles=roles,
                    combined_suggestion=combined,
                    priority_score=priority
                ))

        # Sort by priority
        consensus_items.sort(key=lambda x: x.priority_score, reverse=True)
        session.consensus_items = consensus_items

        return consensus_items

    def finalize_session(self, session: CritiqueSession) -> Dict[str, Any]:
        """
        Finalize the critique session and generate summary.
        """
        # Build consensus if not done
        if not session.consensus_items:
            self.build_consensus(session)

        # Calculate overall score (average of all role scores)
        if session.role_critiques:
            session.overall_score = sum(c.overall_score for c in session.role_critiques) / len(session.role_critiques)

        # Extract top priorities (critical and important issues)
        all_issues = []
        for critique in session.role_critiques:
            for issue in critique.issues:
                if issue.severity in [IssueSeverity.CRITICAL, IssueSeverity.IMPORTANT]:
                    all_issues.append(issue.title)

        session.top_priorities = list(set(all_issues))[:5]

        # Extract top strengths
        all_strengths = []
        for critique in session.role_critiques:
            for strength in critique.strengths:
                all_strengths.append(strength.title)

        session.top_strengths = list(set(all_strengths))[:5]

        session.finalized_at = datetime.now().isoformat()

        return self.export_report(session)

    def export_report(self, session: CritiqueSession) -> Dict[str, Any]:
        """Export the critique session as a structured report."""
        return {
            "session_id": session.session_id,
            "song_title": session.song_title,
            "intent_summary": session.intent_summary,
            "overall_score": round(session.overall_score, 1),
            "top_priorities": session.top_priorities,
            "top_strengths": session.top_strengths,
            "consensus_items": [
                {
                    "issue": item.issue_title,
                    "severity": item.severity.value,
                    "agreeing_roles": [r.value for r in item.agreeing_roles],
                    "suggestion": item.combined_suggestion,
                    "priority": round(item.priority_score, 1)
                }
                for item in session.consensus_items
            ],
            "role_critiques": [
                {
                    "role": c.role.value,
                    "ai": c.ai_name,
                    "score": round(c.overall_score, 1),
                    "summary": c.summary,
                    "issues_count": len(c.issues),
                    "strengths_count": len(c.strengths)
                }
                for c in session.role_critiques
            ],
            "created_at": session.created_at,
            "finalized_at": session.finalized_at
        }


# =============================================================================
# AI Role Assignments (for MCP workstation integration)
# =============================================================================

# Suggested AI assignments based on strengths
AI_ROLE_ASSIGNMENTS = {
    "Claude": [CritiqueRole.EMOTIONAL, CritiqueRole.LYRICAL, CritiqueRole.ARTISTIC],
    "ChatGPT": [CritiqueRole.ARRANGEMENT, CritiqueRole.COMMERCIAL],
    "Gemini": [CritiqueRole.HARMONY, CritiqueRole.PRODUCTION],
    "Copilot": [CritiqueRole.RHYTHM, CritiqueRole.PRODUCTION]
}


def get_ai_roles(ai_name: str) -> List[CritiqueRole]:
    """Get the critique roles assigned to an AI."""
    return AI_ROLE_ASSIGNMENTS.get(ai_name, [])


# =============================================================================
# Critique Templates
# =============================================================================

def create_issue(
    category: IssueCategory,
    severity: IssueSeverity,
    title: str,
    description: str,
    suggestion: Optional[str] = None,
    location: Optional[str] = None
) -> CritiqueIssue:
    """Helper to create a critique issue."""
    import uuid
    return CritiqueIssue(
        id=str(uuid.uuid4())[:8],
        category=category,
        severity=severity,
        title=title,
        description=description,
        suggestion=suggestion,
        location=location
    )


def create_strength(
    title: str,
    description: str,
    why_it_works: Optional[str] = None,
    location: Optional[str] = None
) -> CritiqueStrength:
    """Helper to create a critique strength."""
    import uuid
    return CritiqueStrength(
        id=str(uuid.uuid4())[:8],
        title=title,
        description=description,
        why_it_works=why_it_works,
        location=location
    )


# =============================================================================
# Example Usage
# =============================================================================

def demo_critique_session():
    """Demonstrate the critique protocol."""
    protocol = CritiqueProtocol()

    # Create session
    session = protocol.create_session(
        session_id="demo-001",
        song_title="Midnight Rain",
        intent_summary="A melancholic exploration of letting go, with hidden anger beneath the sadness"
    )

    # Simulate Claude's emotional critique
    claude_critique = RoleCritique(
        role=CritiqueRole.EMOTIONAL,
        ai_name="Claude",
        overall_score=7.5,
        summary="Strong emotional foundation, but the anger isn't coming through enough",
        issues=[
            create_issue(
                IssueCategory.INTENT_MISMATCH,
                IssueSeverity.IMPORTANT,
                "Hidden anger not evident",
                "The stated intent includes hidden anger, but the current arrangement feels purely melancholic without that edge",
                "Consider a more aggressive element in the bridge or outro",
                "Bridge section"
            ),
            create_issue(
                IssueCategory.CREATIVE,
                IssueSeverity.SUGGESTION,
                "Climax could hit harder",
                "The emotional peak feels a bit held back",
                "Let the final chorus really open up dynamically"
            )
        ],
        strengths=[
            create_strength(
                "Authentic vulnerability",
                "The verse melody has a beautiful, exposed quality",
                "The sparse arrangement lets the emotion breathe"
            )
        ]
    )

    # Simulate Gemini's harmony critique
    gemini_critique = RoleCritique(
        role=CritiqueRole.HARMONY,
        ai_name="Gemini",
        overall_score=8.0,
        summary="Solid harmonic choices that serve the emotion well",
        issues=[
            create_issue(
                IssueCategory.CONVENTION,
                IssueSeverity.SUGGESTION,
                "Predictable resolution",
                "The IV-V-I resolution at the end is expected",
                "Consider a deceptive cadence or unresolved ending",
                "Outro"
            )
        ],
        strengths=[
            create_strength(
                "Beautiful chord voicings",
                "The suspended chords in the verse create perfect tension",
                "They align with the lyrical theme of uncertainty"
            ),
            create_strength(
                "Modal interchange",
                "The borrowed chord from minor in the pre-chorus is very effective",
                "Creates the bittersweet quality stated in the intent"
            )
        ]
    )

    # Simulate ChatGPT's arrangement critique
    chatgpt_critique = RoleCritique(
        role=CritiqueRole.ARRANGEMENT,
        ai_name="ChatGPT",
        overall_score=7.0,
        summary="Good structure, needs more contrast between sections",
        issues=[
            create_issue(
                IssueCategory.CREATIVE,
                IssueSeverity.IMPORTANT,
                "Hidden anger not evident",  # Same issue as Claude - will create consensus
                "The arrangement stays in one emotional lane throughout",
                "Add a contrasting element - distorted guitar, aggressive drums"
            ),
            create_issue(
                IssueCategory.BALANCE,
                IssueSeverity.SUGGESTION,
                "Verse 2 too similar to verse 1",
                "The second verse doesn't develop enough from the first",
                "Add a new element or strip something away"
            )
        ],
        strengths=[
            create_strength(
                "Strong intro hook",
                "The opening piano motif is memorable and sets the mood immediately"
            )
        ]
    )

    # Submit critiques
    protocol.submit_critique(session, claude_critique)
    protocol.submit_critique(session, gemini_critique)
    protocol.submit_critique(session, chatgpt_critique)

    # Finalize and get report
    report = protocol.finalize_session(session)

    print("\n" + "=" * 60)
    print("  CRITIQUE REPORT: " + (session.song_title or "Untitled"))
    print("=" * 60)
    print(f"\nOverall Score: {report['overall_score']}/10")
    print(f"\nTop Priorities:")
    for p in report['top_priorities']:
        print(f"  ⚠️  {p}")

    print(f"\nTop Strengths:")
    for s in report['top_strengths']:
        print(f"  ✓  {s}")

    print(f"\n--- CONSENSUS ITEMS ---")
    for item in report['consensus_items']:
        print(f"\n  [{item['severity'].upper()}] {item['issue']}")
        print(f"  Agreed by: {', '.join(item['agreeing_roles'])}")
        print(f"  Suggestion: {item['suggestion']}")

    print("\n--- FULL REPORT (JSON) ---")
    print(json.dumps(report, indent=2))

    return report


# Export public API
__all__ = [
    'CritiqueRole',
    'IssueSeverity',
    'IssueCategory',
    'CritiqueIssue',
    'CritiqueStrength',
    'RoleCritique',
    'ConsensusItem',
    'CritiqueSession',
    'CritiqueProtocol',
    'AI_ROLE_ASSIGNMENTS',
    'get_ai_roles',
    'create_issue',
    'create_strength',
]


if __name__ == "__main__":
    demo_critique_session()
