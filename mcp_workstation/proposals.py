"""
MCP Workstation - Proposal Management

Handles the 3-improvement proposal system where each AI submits proposals.
Includes voting, prioritization, and consensus tracking.

Special handling:
- MCP Coordinator proposals are auto-approved by default
- User (sburdges-eng) serves as ultimate voter with veto/approve powers
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

from .models import (
    Proposal, ProposalStatus, ProposalCategory, AIAgent, UserVotingConfig
)
from .debug import get_debug, DebugCategory, trace
from .ai_specializations import (
    get_capabilities, get_agents_for_category, TaskType
)


@dataclass
class ProposalVote:
    """A vote on a proposal."""
    agent: AIAgent
    proposal_id: str
    vote: int  # -1 (reject), 0 (neutral), 1 (approve)
    comment: str = ""
    timestamp: str = ""
    weight: float = 1.0  # Vote weight (user votes can have higher weight)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class ProposalManager:
    """
    Manages the proposal system for multi-AI collaboration.

    Each AI can submit up to 3 comprehensive improvement proposals.
    Proposals are voted on by all AIs and prioritized for implementation.

    Special features:
    - MCP Coordinator proposals are auto-approved (configurable)
    - User has ultimate voting power with veto/approve capabilities
    """

    MAX_PROPOSALS_PER_AGENT = 3

    def __init__(self, user_config: Optional[UserVotingConfig] = None):
        self.proposals: Dict[str, Proposal] = {}
        self.votes: List[ProposalVote] = []
        self._debug = get_debug()
        self.user_config = user_config or UserVotingConfig()

    @trace(DebugCategory.PROPOSAL)
    def submit_proposal(
        self,
        agent: AIAgent,
        title: str,
        description: str,
        category: ProposalCategory,
        priority: int = 5,
        estimated_effort: str = "medium",
        phase_target: int = 1,
        implementation_notes: str = "",
    ) -> Optional[Proposal]:
        """
        Submit a new improvement proposal.

        Each agent can submit up to MAX_PROPOSALS_PER_AGENT proposals.
        MCP Coordinator proposals are auto-approved when user_config.auto_approve_mcp is True.
        """
        # MCP Coordinator and User have no proposal limit
        is_special_agent = agent.is_mcp_coordinator or agent.is_user

        # Check proposal limit (only for regular AI agents)
        if not is_special_agent:
            agent_proposals = self.get_proposals_by_agent(agent)
            if len(agent_proposals) >= self.MAX_PROPOSALS_PER_AGENT:
                self._debug.warning(
                    DebugCategory.PROPOSAL,
                    f"Agent {agent.value} has reached proposal limit ({self.MAX_PROPOSALS_PER_AGENT})",
                    agent=agent.value,
                )
                return None

            # Validate category alignment with agent strengths
            capabilities = get_capabilities(agent)
            if category not in capabilities.proposal_categories:
                self._debug.info(
                    DebugCategory.PROPOSAL,
                    f"Note: {category.value} is not a primary strength for {agent.value}",
                    agent=agent.value,
                )

        # Determine initial status
        # MCP Coordinator proposals are auto-approved if configured
        if agent.is_mcp_coordinator and self.user_config.auto_approve_mcp:
            initial_status = ProposalStatus.APPROVED
            self._debug.info(
                DebugCategory.PROPOSAL,
                f"MCP Coordinator proposal auto-approved: {title}",
                agent=agent.value,
            )
        else:
            initial_status = ProposalStatus.SUBMITTED

        # Create proposal
        proposal = Proposal(
            id="",  # Will be auto-generated
            agent=agent,
            title=title,
            description=description,
            category=category,
            status=initial_status,
            priority=priority,
            estimated_effort=estimated_effort,
            phase_target=phase_target,
            implementation_notes=implementation_notes,
        )

        self.proposals[proposal.id] = proposal

        self._debug.info(
            DebugCategory.PROPOSAL,
            f"Proposal submitted: {title}",
            agent=agent.value,
            data={"proposal_id": proposal.id, "category": category.value, "auto_approved": initial_status == ProposalStatus.APPROVED},
        )

        return proposal

    @trace(DebugCategory.PROPOSAL)
    def vote_on_proposal(
        self,
        agent: AIAgent,
        proposal_id: str,
        vote: int,
        comment: str = "",
    ) -> bool:
        """
        Cast a vote on a proposal.

        vote: -1 (reject), 0 (neutral), 1 (approve)

        User (sburdges-eng) has special voting powers:
        - Ultimate veto: Can reject any proposal immediately
        - Ultimate approve: Can approve any proposal immediately
        - Weighted votes based on their specialties
        """
        if proposal_id not in self.proposals:
            self._debug.warning(
                DebugCategory.PROPOSAL,
                f"Proposal {proposal_id} not found",
            )
            return False

        proposal = self.proposals[proposal_id]

        # Can't vote on own proposal (unless you're the user with ultimate power)
        if proposal.agent == agent and not agent.is_user:
            self._debug.warning(
                DebugCategory.PROPOSAL,
                f"Agent {agent.value} cannot vote on own proposal",
                agent=agent.value,
            )
            return False

        # Handle user ultimate voting powers first (before weight calculation)
        if agent.is_user:
            # Ultimate veto - user rejects the proposal immediately
            if vote == -1 and self.user_config.ultimate_veto:
                proposal.status = ProposalStatus.REJECTED
                vote_weight = self.user_config.get_category_weight(proposal.category)
                self._record_vote(agent, proposal_id, vote, comment, vote_weight, proposal)
                self._debug.info(
                    DebugCategory.PROPOSAL,
                    f"User (ultimate voter) vetoed proposal {proposal_id}",
                    agent=agent.value,
                )
                return True

            # Ultimate approve - user approves the proposal immediately
            elif vote == 1 and self.user_config.ultimate_approve:
                proposal.status = ProposalStatus.APPROVED
                vote_weight = self.user_config.get_category_weight(proposal.category)
                self._record_vote(agent, proposal_id, vote, comment, vote_weight, proposal)
                self._debug.info(
                    DebugCategory.PROPOSAL,
                    f"User (ultimate voter) approved proposal {proposal_id}",
                    agent=agent.value,
                )
                return True

            # Neutral vote or powers disabled - use weighted vote
            vote_weight = self.user_config.get_category_weight(proposal.category)
        else:
            vote_weight = 1.0

        # Record vote with weight
        self._record_vote(agent, proposal_id, vote, comment, vote_weight, proposal)

        # Check for consensus
        self._check_consensus(proposal)

        return True

    def _record_vote(
        self,
        agent: AIAgent,
        proposal_id: str,
        vote: int,
        comment: str,
        weight: float,
        proposal: Proposal,
    ):
        """Record a vote and update the proposal."""
        vote_record = ProposalVote(
            agent=agent,
            proposal_id=proposal_id,
            vote=vote,
            comment=comment,
            weight=weight,
        )
        self.votes.append(vote_record)

        # Update proposal votes
        proposal.add_vote(agent, vote)

        self._debug.info(
            DebugCategory.PROPOSAL,
            f"Vote cast: {vote:+d} (weight: {weight}) on proposal {proposal_id}",
            agent=agent.value,
            data={"proposal_id": proposal_id, "vote": vote, "weight": weight},
        )

    def _check_consensus(self, proposal: Proposal):
        """
        Check if a proposal has reached consensus.

        Uses weighted vote scores where user votes can count as more than 1.
        Special agents (MCP_COORDINATOR and USER) are excluded from required vote count.

        Consensus logic:
        - Weighted score >= required_votes: APPROVED
        - Weighted score <= -required_votes: REJECTED
        - Otherwise: UNDER_REVIEW
        """
        # Count regular AI agents only (exclude MCP_COORDINATOR and USER)
        regular_agents = [
            a for a in AIAgent
            if not a.is_mcp_coordinator and not a.is_user
        ]
        total_regular_agents = len(regular_agents)
        votes_cast = len(proposal.votes)

        # Need majority of regular agents (excluding proposer if they're regular)
        if proposal.agent in regular_agents:
            required_votes = total_regular_agents - 1
        else:
            required_votes = total_regular_agents

        if votes_cast < required_votes:
            return

        # Calculate weighted vote score for consensus decisions
        weighted_score = self._get_weighted_vote_score(proposal)

        # Use weighted score for consensus decisions
        # This means user votes with higher weights have more influence
        if weighted_score >= required_votes:
            proposal.status = ProposalStatus.APPROVED
            self._debug.info(
                DebugCategory.PROPOSAL,
                f"Proposal {proposal.id} approved with weighted score {weighted_score:.1f}",
            )
        elif weighted_score <= -required_votes:
            proposal.status = ProposalStatus.REJECTED
            self._debug.info(
                DebugCategory.PROPOSAL,
                f"Proposal {proposal.id} rejected with weighted score {weighted_score:.1f}",
            )
        else:
            proposal.status = ProposalStatus.UNDER_REVIEW
            self._debug.info(
                DebugCategory.PROPOSAL,
                f"Proposal {proposal.id} under review with mixed votes (weighted score: {weighted_score:.1f})",
            )

    def _get_weighted_vote_score(self, proposal: Proposal) -> float:
        """Calculate the weighted vote score for a proposal."""
        weighted_score = 0.0
        for vote_record in self.votes:
            if vote_record.proposal_id == proposal.id:
                weighted_score += vote_record.vote * vote_record.weight
        return weighted_score

    @trace(DebugCategory.PROPOSAL)
    def update_status(
        self,
        proposal_id: str,
        status: ProposalStatus,
        notes: str = "",
    ) -> bool:
        """Update a proposal's status."""
        if proposal_id not in self.proposals:
            return False

        proposal = self.proposals[proposal_id]
        proposal.status = status
        proposal.updated_at = datetime.now().isoformat()

        if notes:
            proposal.implementation_notes += f"\n[{status.value}] {notes}"

        self._debug.info(
            DebugCategory.PROPOSAL,
            f"Proposal {proposal_id} status updated to {status.value}",
        )
        return True

    # Query methods
    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        """Get a proposal by ID."""
        return self.proposals.get(proposal_id)

    def get_all_proposals(self) -> List[Proposal]:
        """Get all proposals."""
        return list(self.proposals.values())

    def get_proposals_by_agent(self, agent: AIAgent) -> List[Proposal]:
        """Get all proposals from a specific agent."""
        return [p for p in self.proposals.values() if p.agent == agent]

    def get_proposals_by_status(self, status: ProposalStatus) -> List[Proposal]:
        """Get proposals by status."""
        return [p for p in self.proposals.values() if p.status == status]

    def get_proposals_by_category(self, category: ProposalCategory) -> List[Proposal]:
        """Get proposals by category."""
        return [p for p in self.proposals.values() if p.category == category]

    def get_proposals_by_phase(self, phase_id: int) -> List[Proposal]:
        """Get proposals targeting a specific phase."""
        return [p for p in self.proposals.values() if p.phase_target == phase_id]

    def get_approved_proposals(self) -> List[Proposal]:
        """Get all approved proposals, sorted by priority."""
        approved = [
            p for p in self.proposals.values()
            if p.status == ProposalStatus.APPROVED
        ]
        return sorted(approved, key=lambda p: (p.priority, p.vote_score), reverse=True)

    def get_pending_votes(self, agent: AIAgent) -> List[Proposal]:
        """Get proposals that an agent hasn't voted on yet."""
        pending = []
        for proposal in self.proposals.values():
            if proposal.agent == agent:
                continue  # Can't vote on own
            if proposal.status not in (ProposalStatus.SUBMITTED, ProposalStatus.UNDER_REVIEW):
                continue  # Already decided
            if agent.value in proposal.votes:
                continue  # Already voted
            pending.append(proposal)
        return pending

    # Analysis methods
    def get_proposal_summary(self) -> Dict:
        """Get summary statistics of proposals."""
        by_status = {}
        by_agent = {}
        by_category = {}
        by_phase = {}

        for proposal in self.proposals.values():
            # By status
            status = proposal.status.value
            by_status[status] = by_status.get(status, 0) + 1

            # By agent
            agent = proposal.agent.value
            by_agent[agent] = by_agent.get(agent, 0) + 1

            # By category
            cat = proposal.category.value
            by_category[cat] = by_category.get(cat, 0) + 1

            # By phase
            phase = proposal.phase_target
            by_phase[phase] = by_phase.get(phase, 0) + 1

        return {
            "total": len(self.proposals),
            "by_status": by_status,
            "by_agent": by_agent,
            "by_category": by_category,
            "by_phase": by_phase,
            "total_votes": len(self.votes),
        }

    def get_implementation_queue(self) -> List[Proposal]:
        """
        Get prioritized queue of proposals to implement.

        Orders by:
        1. Status (approved first)
        2. Priority (highest first)
        3. Vote score (highest first)
        4. Phase target (current phase first)
        """
        approved = [
            p for p in self.proposals.values()
            if p.status == ProposalStatus.APPROVED
        ]

        # Sort by priority score
        def priority_score(p: Proposal) -> Tuple:
            return (
                p.priority,
                p.vote_score,
                -p.phase_target,  # Lower phase = earlier
            )

        return sorted(approved, key=priority_score, reverse=True)

    def get_agent_proposal_slots(self) -> Dict[AIAgent, int]:
        """Get remaining proposal slots for each agent."""
        slots = {}
        for agent in AIAgent:
            current = len(self.get_proposals_by_agent(agent))
            slots[agent] = max(0, self.MAX_PROPOSALS_PER_AGENT - current)
        return slots

    # Serialization
    def to_dict(self) -> Dict:
        """Serialize manager state."""
        return {
            "proposals": {pid: p.to_dict() for pid, p in self.proposals.items()},
            "votes": [
                {
                    "agent": v.agent.value,
                    "proposal_id": v.proposal_id,
                    "vote": v.vote,
                    "comment": v.comment,
                    "timestamp": v.timestamp,
                    "weight": v.weight,
                }
                for v in self.votes
            ],
            "user_config": self.user_config.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ProposalManager":
        """Deserialize manager state."""
        user_config = None
        if "user_config" in data:
            user_config = UserVotingConfig.from_dict(data["user_config"])

        manager = cls(user_config=user_config)

        for pid, pdata in data.get("proposals", {}).items():
            proposal = Proposal.from_dict(pdata)
            manager.proposals[pid] = proposal

        for vdata in data.get("votes", []):
            vote = ProposalVote(
                agent=AIAgent(vdata["agent"]),
                proposal_id=vdata["proposal_id"],
                vote=vdata["vote"],
                comment=vdata.get("comment", ""),
                timestamp=vdata.get("timestamp", ""),
                weight=vdata.get("weight", 1.0),
            )
            manager.votes.append(vote)

        return manager


# =============================================================================
# Proposal Templates
# =============================================================================

def get_proposal_template(category: ProposalCategory) -> Dict:
    """Get a template for a proposal in a given category."""
    templates = {
        ProposalCategory.ARCHITECTURE: {
            "title": "[Architecture] ",
            "description_template": (
                "## Problem\n"
                "[What architectural issue does this address?]\n\n"
                "## Proposed Solution\n"
                "[Describe the architectural change]\n\n"
                "## Impact\n"
                "- Components affected: \n"
                "- Migration needed: \n"
                "- Risk level: "
            ),
            "default_effort": "high",
        },
        ProposalCategory.PERFORMANCE: {
            "title": "[Performance] ",
            "description_template": (
                "## Bottleneck\n"
                "[What performance issue?]\n\n"
                "## Optimization\n"
                "[Proposed optimization]\n\n"
                "## Expected Improvement\n"
                "- Metric: \n"
                "- Current: \n"
                "- Target: "
            ),
            "default_effort": "medium",
        },
        ProposalCategory.CPP_PORT: {
            "title": "[C++ Port] ",
            "description_template": (
                "## Module to Port\n"
                "[Which Python module?]\n\n"
                "## C++ Design\n"
                "[How will it be structured in C++?]\n\n"
                "## Python Bridge\n"
                "[How will Python access it?]\n\n"
                "## Performance Target\n"
                "- Latency: \n"
                "- Throughput: "
            ),
            "default_effort": "very_high",
        },
        ProposalCategory.FEATURE_NEW: {
            "title": "[Feature] ",
            "description_template": (
                "## Feature Description\n"
                "[What does this feature do?]\n\n"
                "## User Value\n"
                "[Why do users need this?]\n\n"
                "## Implementation\n"
                "- Components: \n"
                "- Dependencies: \n"
                "- Complexity: "
            ),
            "default_effort": "medium",
        },
        ProposalCategory.DSP_ALGORITHM: {
            "title": "[DSP] ",
            "description_template": (
                "## Algorithm\n"
                "[What DSP algorithm?]\n\n"
                "## Use Case\n"
                "[How will it be used in DAiW?]\n\n"
                "## Requirements\n"
                "- Sample rate: \n"
                "- Latency: \n"
                "- CPU budget: "
            ),
            "default_effort": "high",
        },
    }

    return templates.get(category, {
        "title": f"[{category.value}] ",
        "description_template": "## Description\n\n## Implementation\n\n## Impact\n",
        "default_effort": "medium",
    })


# =============================================================================
# Proposal Display
# =============================================================================

def format_proposal(proposal: Proposal, include_votes: bool = True) -> str:
    """Format a proposal for display."""
    lines = [
        f"{'=' * 60}",
        f"PROPOSAL: {proposal.title}",
        f"{'=' * 60}",
        f"ID:       {proposal.id}",
        f"Agent:    {proposal.agent.display_name}",
        f"Category: {proposal.category.value}",
        f"Status:   {proposal.status.value}",
        f"Priority: {proposal.priority}/10",
        f"Effort:   {proposal.estimated_effort}",
        f"Phase:    {proposal.phase_target}",
        f"",
        "DESCRIPTION:",
        proposal.description,
    ]

    if include_votes and proposal.votes:
        lines.extend([
            "",
            f"VOTES (Score: {proposal.vote_score:+d}):",
        ])
        for agent_id, vote in proposal.votes.items():
            vote_str = {-1: "REJECT", 0: "NEUTRAL", 1: "APPROVE"}.get(vote, "?")
            lines.append(f"  {agent_id}: {vote_str}")

    if proposal.implementation_notes:
        lines.extend([
            "",
            "IMPLEMENTATION NOTES:",
            proposal.implementation_notes,
        ])

    return "\n".join(lines)


def format_proposal_list(proposals: List[Proposal]) -> str:
    """Format a list of proposals for display."""
    if not proposals:
        return "No proposals found."

    lines = [
        f"{'ID':<10} {'Status':<12} {'Agent':<15} {'Title':<40}",
        "-" * 77,
    ]

    for p in proposals:
        title = p.title[:37] + "..." if len(p.title) > 40 else p.title
        lines.append(
            f"{p.id:<10} {p.status.value:<12} {p.agent.value:<15} {title:<40}"
        )

    return "\n".join(lines)
