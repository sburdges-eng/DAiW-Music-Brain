"""
Expanded Question Bank for Intent Wizard

500+ branching questions for deep song intent discovery.
- 250 Therapy-Based: Emotional exploration, inner work, relationships
- 250 Musician-Based: Technical, creative, production decisions

Organized by AI assignment:
- Claude: Emotional/Vulnerability/Inner Work (125 therapy)
- ChatGPT: Relationships/Coping/Identity (125 therapy)
- Gemini: Harmony/Theory/Analysis (125 musician)
- Copilot: Production/Arrangement/Technical (125 musician)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class QuestionDomain(Enum):
    THERAPY = "therapy"
    MUSICIAN = "musician"


class TherapyCategory(Enum):
    # Claude's domain
    CORE_WOUND = "core_wound"
    EMOTIONAL_IDENTIFICATION = "emotional_identification"
    VULNERABILITY = "vulnerability"
    SHADOW_WORK = "shadow_work"
    INNER_CHILD = "inner_child"
    GRIEF_LOSS = "grief_loss"
    # ChatGPT's domain
    RELATIONSHIP_DYNAMICS = "relationship_dynamics"
    SELF_IDENTITY = "self_identity"
    COPING_MECHANISMS = "coping_mechanisms"
    ATTACHMENT = "attachment"
    BOUNDARIES = "boundaries"
    FORGIVENESS = "forgiveness"


class MusicianCategory(Enum):
    # Gemini's domain
    HARMONY = "harmony"
    MELODY = "melody"
    THEORY = "theory"
    KEY_MODE = "key_mode"
    CHORD_PROGRESSION = "chord_progression"
    VOICE_LEADING = "voice_leading"
    # Copilot's domain
    PRODUCTION = "production"
    ARRANGEMENT = "arrangement"
    RHYTHM = "rhythm"
    SOUND_DESIGN = "sound_design"
    MIX = "mix"
    GENRE = "genre"


@dataclass
class BankQuestion:
    """A question in the expanded bank."""
    id: str
    text: str
    domain: QuestionDomain
    category: str
    assigned_ai: str
    choices: List[str] = field(default_factory=list)
    follow_ups: List[str] = field(default_factory=list)  # Question IDs
    tags: List[str] = field(default_factory=list)
    depth_level: int = 1  # 1=surface, 2=deeper, 3=core


# =============================================================================
# CLAUDE'S QUESTIONS: Emotional/Vulnerability/Inner Work (125)
# =============================================================================

CLAUDE_THERAPY_QUESTIONS = [
    # CORE WOUND EXPLORATION (30)
    BankQuestion("c_cw_001", "What's the oldest memory connected to this feeling?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),
    BankQuestion("c_cw_002", "If this emotion had a voice, what would it say?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=2),
    BankQuestion("c_cw_003", "Where do you feel this emotion in your body?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=2),
    BankQuestion("c_cw_004", "What did you need to hear back then that you never heard?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),
    BankQuestion("c_cw_005", "Who taught you to feel this way about yourself?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),
    BankQuestion("c_cw_006", "What's the lie you've been telling yourself about this?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),
    BankQuestion("c_cw_007", "If you could go back, what would you tell your younger self?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=2),
    BankQuestion("c_cw_008", "What part of you is still waiting for permission?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),
    BankQuestion("c_cw_009", "What would you have to give up to heal from this?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),
    BankQuestion("c_cw_010", "What's the question you're afraid to ask yourself?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),
    BankQuestion("c_cw_011", "When did you first learn to hide this part of yourself?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),
    BankQuestion("c_cw_012", "What would happen if you stopped protecting everyone from your truth?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),
    BankQuestion("c_cw_013", "What promise did you make to yourself that you've broken?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=2),
    BankQuestion("c_cw_014", "What are you grieving that you haven't named yet?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),
    BankQuestion("c_cw_015", "If this pain could teach you something, what would it be?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=2),
    BankQuestion("c_cw_016", "What part of your story have you never told anyone?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),
    BankQuestion("c_cw_017", "What would your wound say if it could speak?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),
    BankQuestion("c_cw_018", "When do you feel most like a fraud?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=2),
    BankQuestion("c_cw_019", "What's the thing you do that you wish you could stop?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=2),
    BankQuestion("c_cw_020", "What mask are you tired of wearing?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=2),
    BankQuestion("c_cw_021", "What would you attempt if you knew you couldn't fail emotionally?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=2),
    BankQuestion("c_cw_022", "What childhood need still goes unmet?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),
    BankQuestion("c_cw_023", "What's the conversation you keep having in your head?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=2),
    BankQuestion("c_cw_024", "When did you stop believing in yourself?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),
    BankQuestion("c_cw_025", "What are you pretending not to know?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),
    BankQuestion("c_cw_026", "What truth are you dancing around?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=2),
    BankQuestion("c_cw_027", "What would it mean if this feeling never went away?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),
    BankQuestion("c_cw_028", "Who would you be without this pain?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),
    BankQuestion("c_cw_029", "What are you afraid will happen if you let yourself feel this fully?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),
    BankQuestion("c_cw_030", "What part of you died that you're trying to resurrect?", QuestionDomain.THERAPY, "core_wound", "Claude", depth_level=3),

    # EMOTIONAL IDENTIFICATION (25)
    BankQuestion("c_ei_001", "What emotion is sitting just beneath the surface right now?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=1),
    BankQuestion("c_ei_002", "Is this feeling familiar? When have you felt it before?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=2),
    BankQuestion("c_ei_003", "What triggers this emotion most intensely?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=2),
    BankQuestion("c_ei_004", "If you had to name this feeling in one word, what would it be?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=1),
    BankQuestion("c_ei_005", "What color would this emotion be?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=1),
    BankQuestion("c_ei_006", "Does this emotion feel hot or cold?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=1),
    BankQuestion("c_ei_007", "Is this feeling moving or stuck?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=1),
    BankQuestion("c_ei_008", "What does this emotion want from you?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=2),
    BankQuestion("c_ei_009", "Is there an emotion hiding behind this one?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=2),
    BankQuestion("c_ei_010", "How long have you been carrying this feeling?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=2),
    BankQuestion("c_ei_011", "What would happen if you let this emotion out completely?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=2),
    BankQuestion("c_ei_012", "Is this your emotion, or did you inherit it from someone?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=3),
    BankQuestion("c_ei_013", "What physical sensation accompanies this feeling?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=1),
    BankQuestion("c_ei_014", "If this emotion was weather, what would it be?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=1),
    BankQuestion("c_ei_015", "What time of day does this feeling hit hardest?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=1),
    BankQuestion("c_ei_016", "Is this emotion asking you to act or to be still?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=2),
    BankQuestion("c_ei_017", "What story does this emotion tell about you?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=2),
    BankQuestion("c_ei_018", "Is this feeling trying to protect you from something?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=2),
    BankQuestion("c_ei_019", "What would you lose if you stopped feeling this way?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=3),
    BankQuestion("c_ei_020", "How do you typically try to escape this feeling?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=2),
    BankQuestion("c_ei_021", "What secondary emotion shows up when this one gets too intense?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=2),
    BankQuestion("c_ei_022", "Is there any relief mixed in with this pain?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=2),
    BankQuestion("c_ei_023", "What percentage of you wants to feel this vs. escape it?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=2),
    BankQuestion("c_ei_024", "If this feeling had a texture, what would it feel like?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=1),
    BankQuestion("c_ei_025", "What would it feel like to make peace with this emotion?", QuestionDomain.THERAPY, "emotional_identification", "Claude", depth_level=3),

    # VULNERABILITY (25)
    BankQuestion("c_vu_001", "What's the most vulnerable thing you could say right now?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=2),
    BankQuestion("c_vu_002", "What are you afraid people will think if they really knew you?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=3),
    BankQuestion("c_vu_003", "When was the last time you let someone see you cry?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=2),
    BankQuestion("c_vu_004", "What's the bravest thing you've never done?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=2),
    BankQuestion("c_vu_005", "Who in your life has earned the right to hear this story?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=2),
    BankQuestion("c_vu_006", "What would it cost you to be completely honest right now?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=2),
    BankQuestion("c_vu_007", "What part of yourself do you hide even from yourself?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=3),
    BankQuestion("c_vu_008", "When did vulnerability become dangerous for you?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=3),
    BankQuestion("c_vu_009", "What would being truly seen feel like?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=2),
    BankQuestion("c_vu_010", "What's the worst that could happen if you opened up?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=2),
    BankQuestion("c_vu_011", "Who taught you that vulnerability was weakness?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=3),
    BankQuestion("c_vu_012", "What would you say if you knew no one would judge you?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=2),
    BankQuestion("c_vu_013", "What armor are you ready to take off?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=2),
    BankQuestion("c_vu_014", "What's the thing you've never said out loud?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=3),
    BankQuestion("c_vu_015", "How do you protect yourself from being hurt?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=2),
    BankQuestion("c_vu_016", "What would change if you stopped pretending to be okay?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=2),
    BankQuestion("c_vu_017", "Who do you perform strength for?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=2),
    BankQuestion("c_vu_018", "What secret are you keeping that's exhausting to hide?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=3),
    BankQuestion("c_vu_019", "When did you decide it wasn't safe to need people?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=3),
    BankQuestion("c_vu_020", "What would happen if you asked for help?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=2),
    BankQuestion("c_vu_021", "What's the softest part of you that you protect the hardest?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=3),
    BankQuestion("c_vu_022", "How do you know when someone is safe to be vulnerable with?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=2),
    BankQuestion("c_vu_023", "What's the difference between the you that people see and the real you?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=2),
    BankQuestion("c_vu_024", "What fear is keeping you from being authentic?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=2),
    BankQuestion("c_vu_025", "If you could guarantee you wouldn't be rejected, what would you share?", QuestionDomain.THERAPY, "vulnerability", "Claude", depth_level=2),

    # SHADOW WORK (25)
    BankQuestion("c_sw_001", "What part of yourself do you try to hide from others?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=2),
    BankQuestion("c_sw_002", "What trait in others triggers you the most?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=2),
    BankQuestion("c_sw_003", "What's the 'dark' thought you're ashamed of having?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=3),
    BankQuestion("c_sw_004", "What part of yourself did you have to kill to survive?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=3),
    BankQuestion("c_sw_005", "What would your enemy say is your worst quality?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=2),
    BankQuestion("c_sw_006", "What do you judge others for that you secretly do yourself?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=3),
    BankQuestion("c_sw_007", "What's the monster under your bed?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=2),
    BankQuestion("c_sw_008", "What desire do you suppress because it feels wrong?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=3),
    BankQuestion("c_sw_009", "Who would you be if you stopped being 'good'?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=3),
    BankQuestion("c_sw_010", "What's the version of yourself you're terrified of becoming?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=3),
    BankQuestion("c_sw_011", "What would you do if no one was watching and there were no consequences?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=2),
    BankQuestion("c_sw_012", "What's your most selfish want?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=2),
    BankQuestion("c_sw_013", "What rage have you never let yourself feel?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=3),
    BankQuestion("c_sw_014", "What have you done that you can't forgive yourself for?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=3),
    BankQuestion("c_sw_015", "What's the ugliest thing about you that might also be beautiful?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=3),
    BankQuestion("c_sw_016", "What power have you been afraid to claim?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=2),
    BankQuestion("c_sw_017", "What destructive pattern keeps showing up in your life?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=2),
    BankQuestion("c_sw_018", "What would you have to accept about yourself to be free?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=3),
    BankQuestion("c_sw_019", "What scares you about your own potential?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=2),
    BankQuestion("c_sw_020", "What part of yourself needs to die for you to grow?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=3),
    BankQuestion("c_sw_021", "What's the thing you do that you hate yourself for afterward?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=2),
    BankQuestion("c_sw_022", "What's the family secret that lives in your body?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=3),
    BankQuestion("c_sw_023", "What's your relationship with your own anger?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=2),
    BankQuestion("c_sw_024", "What does your shadow want you to know?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=3),
    BankQuestion("c_sw_025", "What gift is hidden in your darkness?", QuestionDomain.THERAPY, "shadow_work", "Claude", depth_level=3),

    # INNER CHILD (20)
    BankQuestion("c_ic_001", "What did you need as a child that you never got?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=3),
    BankQuestion("c_ic_002", "What did little you believe about the world?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=2),
    BankQuestion("c_ic_003", "What were you told you were 'too much' of?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=2),
    BankQuestion("c_ic_004", "What game did you love to play that you've forgotten?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=1),
    BankQuestion("c_ic_005", "What dream did you have before you learned to be realistic?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=2),
    BankQuestion("c_ic_006", "What would your childhood self think of who you've become?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=2),
    BankQuestion("c_ic_007", "What scared you as a child that still scares you?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=2),
    BankQuestion("c_ic_008", "What was your safe place as a child?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=1),
    BankQuestion("c_ic_009", "What did you believe about love before anyone hurt you?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=3),
    BankQuestion("c_ic_010", "What promise did you make to yourself as a kid?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=2),
    BankQuestion("c_ic_011", "What part of your childhood are you still grieving?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=3),
    BankQuestion("c_ic_012", "What was the first time you felt truly alone?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=3),
    BankQuestion("c_ic_013", "What would you say to the kid you used to be?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=2),
    BankQuestion("c_ic_014", "What did you have to grow up too fast for?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=3),
    BankQuestion("c_ic_015", "What innocence did you lose too soon?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=3),
    BankQuestion("c_ic_016", "What did little you think you'd be doing by now?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=1),
    BankQuestion("c_ic_017", "What part of your childhood do you wish you could redo?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=2),
    BankQuestion("c_ic_018", "What would it take to make your inner child feel safe?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=2),
    BankQuestion("c_ic_019", "What song would your childhood self love?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=1),
    BankQuestion("c_ic_020", "What playfulness have you lost that you want back?", QuestionDomain.THERAPY, "inner_child", "Claude", depth_level=2),
]


# =============================================================================
# CHATGPT'S QUESTIONS: Relationships/Coping/Identity (125)
# =============================================================================

CHATGPT_THERAPY_QUESTIONS = [
    # RELATIONSHIP DYNAMICS (30)
    BankQuestion("g_rd_001", "Who is this song really for?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=1),
    BankQuestion("g_rd_002", "What do you wish you could say to them face to face?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_003", "What did they give you that no one else could?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_004", "What did they take from you that you can't get back?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=3),
    BankQuestion("g_rd_005", "What pattern do you keep repeating in relationships?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_006", "What role do you always play: the fixer, the leaver, the one who stays too long?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_007", "What did you sacrifice for this person?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_008", "What red flags did you ignore?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_009", "What version of yourself did you become around them?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_010", "What's the thing you never told them?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=3),
    BankQuestion("g_rd_011", "How did they make you feel about yourself?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_012", "What moment changed everything between you?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_013", "What did you learn about love from this relationship?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_014", "What would you do differently if you could start over?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_015", "Are you writing this to process, to communicate, or to release?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=1),
    BankQuestion("g_rd_016", "What did you see in them that you wish you saw in yourself?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=3),
    BankQuestion("g_rd_017", "What part of the relationship are you romanticizing?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_018", "What part of the relationship are you demonizing?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_019", "Who were you before you met them?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_020", "Who do you want to be after this?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_021", "What boundaries did you let them cross?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_022", "What boundaries did you cross?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_023", "What's the hardest part of letting go?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_024", "What do you miss that you know wasn't real?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=3),
    BankQuestion("g_rd_025", "What small thing do you miss that surprises you?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=1),
    BankQuestion("g_rd_026", "What did this relationship teach you about your needs?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_027", "What future did you imagine with them?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_028", "What future are you grieving?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=3),
    BankQuestion("g_rd_029", "If they heard this song, what would you want them to feel?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),
    BankQuestion("g_rd_030", "What would closure actually look like for you?", QuestionDomain.THERAPY, "relationship_dynamics", "ChatGPT", depth_level=2),

    # SELF-IDENTITY (25)
    BankQuestion("g_si_001", "Who are you when no one is watching?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=2),
    BankQuestion("g_si_002", "What labels have you outgrown?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=2),
    BankQuestion("g_si_003", "What part of your identity feels most fragile right now?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=2),
    BankQuestion("g_si_004", "What do you believe about yourself that might not be true?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=3),
    BankQuestion("g_si_005", "When do you feel most like yourself?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=1),
    BankQuestion("g_si_006", "When do you feel least like yourself?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=2),
    BankQuestion("g_si_007", "What would you have to let go of to become who you want to be?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=2),
    BankQuestion("g_si_008", "What parts of yourself have you abandoned to fit in?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=3),
    BankQuestion("g_si_009", "What do you stand for that you've never fully stood up for?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=2),
    BankQuestion("g_si_010", "What's your relationship with your own reflection?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=2),
    BankQuestion("g_si_011", "What would you name this chapter of your life?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=1),
    BankQuestion("g_si_012", "Who did you used to be that you miss?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=2),
    BankQuestion("g_si_013", "Who are you becoming that scares you?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=2),
    BankQuestion("g_si_014", "What's the difference between who you are and who you pretend to be?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=2),
    BankQuestion("g_si_015", "What would people be surprised to learn about you?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=1),
    BankQuestion("g_si_016", "What's the kindest thing you could say to yourself right now?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=2),
    BankQuestion("g_si_017", "What do you need to prove, and to whom?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=2),
    BankQuestion("g_si_018", "What would you do if you stopped trying to be perfect?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=2),
    BankQuestion("g_si_019", "What's the story you tell yourself about why you're not enough?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=3),
    BankQuestion("g_si_020", "What achievement would finally make you feel worthy?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=2),
    BankQuestion("g_si_021", "What if you're already worthy without achieving anything else?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=3),
    BankQuestion("g_si_022", "What makes you, you - that can never be taken away?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=2),
    BankQuestion("g_si_023", "What title would you give your autobiography?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=1),
    BankQuestion("g_si_024", "What's one thing you've always known about yourself but never said?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=2),
    BankQuestion("g_si_025", "If you could only be remembered for one thing, what would it be?", QuestionDomain.THERAPY, "self_identity", "ChatGPT", depth_level=2),

    # COPING MECHANISMS (20)
    BankQuestion("g_cm_001", "What do you do when you can't handle your feelings?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=1),
    BankQuestion("g_cm_002", "What's your go-to distraction when things get hard?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=1),
    BankQuestion("g_cm_003", "What habit do you know is unhealthy but keep doing anyway?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=2),
    BankQuestion("g_cm_004", "What's the healthiest way you've learned to cope?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=1),
    BankQuestion("g_cm_005", "What would you do if you couldn't use your usual escape?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=2),
    BankQuestion("g_cm_006", "Do you tend to shut down, blow up, or run away?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=2),
    BankQuestion("g_cm_007", "What's your relationship with control?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=2),
    BankQuestion("g_cm_008", "How do you numb yourself?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=2),
    BankQuestion("g_cm_009", "What's the cost of your coping strategy?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=2),
    BankQuestion("g_cm_010", "What would happen if you just sat with the feeling?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=2),
    BankQuestion("g_cm_011", "Who do you call when you're falling apart?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=1),
    BankQuestion("g_cm_012", "What do you tell yourself to get through hard times?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=1),
    BankQuestion("g_cm_013", "What coping mechanism served you once but hurts you now?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=3),
    BankQuestion("g_cm_014", "How do you know when you're not okay?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=2),
    BankQuestion("g_cm_015", "What signals does your body give you before a breakdown?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=2),
    BankQuestion("g_cm_016", "What do you need that you don't ask for?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=2),
    BankQuestion("g_cm_017", "What would self-care look like if you actually did it?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=1),
    BankQuestion("g_cm_018", "What's something that always makes you feel better, even a little?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=1),
    BankQuestion("g_cm_019", "What survival mechanism have you outgrown?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=3),
    BankQuestion("g_cm_020", "What would it look like to heal instead of just cope?", QuestionDomain.THERAPY, "coping_mechanisms", "ChatGPT", depth_level=3),

    # ATTACHMENT (20)
    BankQuestion("g_at_001", "Do you chase people or push them away?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=2),
    BankQuestion("g_at_002", "What does safety feel like in a relationship?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=2),
    BankQuestion("g_at_003", "When do you feel most secure with someone?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=1),
    BankQuestion("g_at_004", "When do you feel most anxious with someone?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=2),
    BankQuestion("g_at_005", "What's your biggest fear in relationships?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=2),
    BankQuestion("g_at_006", "Do you need more closeness or more space?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=1),
    BankQuestion("g_at_007", "What makes you want to run?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=2),
    BankQuestion("g_at_008", "What makes you hold on too tight?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=2),
    BankQuestion("g_at_009", "How do you test people before trusting them?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=2),
    BankQuestion("g_at_010", "What does abandonment look like to you?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=3),
    BankQuestion("g_at_011", "Who left you in a way that still affects you?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=3),
    BankQuestion("g_at_012", "What would secure love actually feel like?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=2),
    BankQuestion("g_at_013", "Do you fall in love quickly or slowly?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=1),
    BankQuestion("g_at_014", "What makes someone worth the risk of attachment?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=2),
    BankQuestion("g_at_015", "How do you know when you're becoming too dependent?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=2),
    BankQuestion("g_at_016", "How do you know when you're being too distant?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=2),
    BankQuestion("g_at_017", "What would change if you believed people would stay?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=3),
    BankQuestion("g_at_018", "What do you do when you feel someone pulling away?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=2),
    BankQuestion("g_at_019", "What's your attachment style, and how did you develop it?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=2),
    BankQuestion("g_at_020", "What would earned secure attachment look like for you?", QuestionDomain.THERAPY, "attachment", "ChatGPT", depth_level=3),

    # BOUNDARIES (15)
    BankQuestion("g_bo_001", "What boundary do you struggle to hold?", QuestionDomain.THERAPY, "boundaries", "ChatGPT", depth_level=2),
    BankQuestion("g_bo_002", "Who taught you that your needs don't matter?", QuestionDomain.THERAPY, "boundaries", "ChatGPT", depth_level=3),
    BankQuestion("g_bo_003", "When do you say yes when you mean no?", QuestionDomain.THERAPY, "boundaries", "ChatGPT", depth_level=2),
    BankQuestion("g_bo_004", "What would change if you stopped people-pleasing?", QuestionDomain.THERAPY, "boundaries", "ChatGPT", depth_level=2),
    BankQuestion("g_bo_005", "What's the hardest 'no' you've ever had to say?", QuestionDomain.THERAPY, "boundaries", "ChatGPT", depth_level=2),
    BankQuestion("g_bo_006", "What resentment are you holding because you didn't set a boundary?", QuestionDomain.THERAPY, "boundaries", "ChatGPT", depth_level=2),
    BankQuestion("g_bo_007", "What would self-respect look like in action?", QuestionDomain.THERAPY, "boundaries", "ChatGPT", depth_level=2),
    BankQuestion("g_bo_008", "Who do you give too much to?", QuestionDomain.THERAPY, "boundaries", "ChatGPT", depth_level=1),
    BankQuestion("g_bo_009", "What do you tolerate that you shouldn't?", QuestionDomain.THERAPY, "boundaries", "ChatGPT", depth_level=2),
    BankQuestion("g_bo_010", "What's the cost of not protecting your energy?", QuestionDomain.THERAPY, "boundaries", "ChatGPT", depth_level=2),
    BankQuestion("g_bo_011", "When did you learn that your boundaries weren't allowed?", QuestionDomain.THERAPY, "boundaries", "ChatGPT", depth_level=3),
    BankQuestion("g_bo_012", "What would you protect if you valued yourself more?", QuestionDomain.THERAPY, "boundaries", "ChatGPT", depth_level=2),
    BankQuestion("g_bo_013", "What relationship is draining you right now?", QuestionDomain.THERAPY, "boundaries", "ChatGPT", depth_level=1),
    BankQuestion("g_bo_014", "What guilt keeps you from saying no?", QuestionDomain.THERAPY, "boundaries", "ChatGPT", depth_level=2),
    BankQuestion("g_bo_015", "What boundary would change your life if you set it?", QuestionDomain.THERAPY, "boundaries", "ChatGPT", depth_level=2),

    # FORGIVENESS (15)
    BankQuestion("g_fo_001", "Who do you need to forgive?", QuestionDomain.THERAPY, "forgiveness", "ChatGPT", depth_level=2),
    BankQuestion("g_fo_002", "What would you have to accept to forgive them?", QuestionDomain.THERAPY, "forgiveness", "ChatGPT", depth_level=2),
    BankQuestion("g_fo_003", "What would forgiving yourself require?", QuestionDomain.THERAPY, "forgiveness", "ChatGPT", depth_level=3),
    BankQuestion("g_fo_004", "What grudge is poisoning you?", QuestionDomain.THERAPY, "forgiveness", "ChatGPT", depth_level=2),
    BankQuestion("g_fo_005", "Is there a difference between forgiving and excusing?", QuestionDomain.THERAPY, "forgiveness", "ChatGPT", depth_level=2),
    BankQuestion("g_fo_006", "What are you holding onto that's holding you back?", QuestionDomain.THERAPY, "forgiveness", "ChatGPT", depth_level=2),
    BankQuestion("g_fo_007", "What would freedom from this resentment feel like?", QuestionDomain.THERAPY, "forgiveness", "ChatGPT", depth_level=2),
    BankQuestion("g_fo_008", "What apology are you waiting for that may never come?", QuestionDomain.THERAPY, "forgiveness", "ChatGPT", depth_level=3),
    BankQuestion("g_fo_009", "What do you need to say before you can move on?", QuestionDomain.THERAPY, "forgiveness", "ChatGPT", depth_level=2),
    BankQuestion("g_fo_010", "What would change if you stopped waiting for them to understand?", QuestionDomain.THERAPY, "forgiveness", "ChatGPT", depth_level=2),
    BankQuestion("g_fo_011", "Can you forgive someone without reconciling with them?", QuestionDomain.THERAPY, "forgiveness", "ChatGPT", depth_level=2),
    BankQuestion("g_fo_012", "What part of your own past do you judge most harshly?", QuestionDomain.THERAPY, "forgiveness", "ChatGPT", depth_level=3),
    BankQuestion("g_fo_013", "What would compassion for yourself look like?", QuestionDomain.THERAPY, "forgiveness", "ChatGPT", depth_level=2),
    BankQuestion("g_fo_014", "What mistake taught you something valuable?", QuestionDomain.THERAPY, "forgiveness", "ChatGPT", depth_level=2),
    BankQuestion("g_fo_015", "What if they did the best they could with what they had?", QuestionDomain.THERAPY, "forgiveness", "ChatGPT", depth_level=3),
]


# =============================================================================
# GEMINI'S QUESTIONS: Harmony/Theory/Analysis (125)
# =============================================================================

GEMINI_MUSICIAN_QUESTIONS = [
    # HARMONY (30)
    BankQuestion("m_ha_001", "What key feels right for this emotion?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=1),
    BankQuestion("m_ha_002", "Major or minor? Or something modal?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=1),
    BankQuestion("m_ha_003", "Do you want the chords to resolve or stay unresolved?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_004", "Should the harmony feel stable or unstable?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=1),
    BankQuestion("m_ha_005", "Are you drawn to simple or complex chord progressions?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=1),
    BankQuestion("m_ha_006", "Do you want any borrowed chords from parallel modes?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_007", "Should there be any key changes in this song?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_008", "Do you want a deceptive cadence anywhere?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_009", "How much dissonance can this song handle?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_010", "Do you want any suspended chords to create tension?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=1),
    BankQuestion("m_ha_011", "Should the verse and chorus have different harmonic colors?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_012", "Do you want any secondary dominants?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_013", "How many chords should be in your main progression?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=1),
    BankQuestion("m_ha_014", "Do you want a pedal point anywhere?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_015", "Should the bass line be root-based or melodic?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_016", "Do you want any slash chords or inversions?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_017", "Is there a specific chord that should hit at the emotional peak?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_018", "Should the harmony support or contrast the lyrics?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_019", "Do you want any chromatic movement?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_020", "What chord progression cliche do you want to avoid?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_021", "Should the pre-chorus create harmonic tension?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_022", "Do you want the bridge to go somewhere harmonically unexpected?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_023", "How should the final chord feel? Resolved? Questioning?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_024", "Do you want any 7th, 9th, or extended chords?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_025", "Should the harmony be diatonic or chromatic?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_026", "What mode might match this emotion? Dorian? Mixolydian? Phrygian?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_027", "Do you want any tritone substitutions?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=3),
    BankQuestion("m_ha_028", "Should the harmonic rhythm be fast or slow?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),
    BankQuestion("m_ha_029", "Do you want any surprising chord changes?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=1),
    BankQuestion("m_ha_030", "How should the outro resolve harmonically?", QuestionDomain.MUSICIAN, "harmony", "Gemini", depth_level=2),

    # MELODY (25)
    BankQuestion("m_me_001", "Should the melody be singable or instrumental?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=1),
    BankQuestion("m_me_002", "What's the range of the melody? How high/low?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=1),
    BankQuestion("m_me_003", "Should the melody be stepwise or have big jumps?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),
    BankQuestion("m_me_004", "Where should the melodic climax be?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),
    BankQuestion("m_me_005", "Should the verse melody be lower than the chorus?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=1),
    BankQuestion("m_me_006", "Do you want a memorable hook or motif?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=1),
    BankQuestion("m_me_007", "Should the melody follow the natural speech rhythm?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),
    BankQuestion("m_me_008", "How much repetition should the melody have?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),
    BankQuestion("m_me_009", "Should there be any melodic surprises?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=1),
    BankQuestion("m_me_010", "Do you want call-and-response in the melody?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),
    BankQuestion("m_me_011", "Should the melody be syncopated or on the beat?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),
    BankQuestion("m_me_012", "What note should the melody start on?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),
    BankQuestion("m_me_013", "What note should the melody resolve to?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),
    BankQuestion("m_me_014", "Should the phrasing be long and flowing or short and punchy?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),
    BankQuestion("m_me_015", "Do you want any blue notes or chromatic notes?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),
    BankQuestion("m_me_016", "Should the melody outline the chords or move independently?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),
    BankQuestion("m_me_017", "How should the melody breathe? Where are the rests?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),
    BankQuestion("m_me_018", "Do you want any melodic sequences (repeated patterns)?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),
    BankQuestion("m_me_019", "Should the bridge have a completely different melody?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),
    BankQuestion("m_me_020", "What scale or mode should the melody come from?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),
    BankQuestion("m_me_021", "Should there be any melodic tension before resolution?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),
    BankQuestion("m_me_022", "Do you want any ornamentation (bends, slides, grace notes)?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),
    BankQuestion("m_me_023", "Should the melody have any surprise intervals?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),
    BankQuestion("m_me_024", "How catchy vs. subtle should the melody be?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=1),
    BankQuestion("m_me_025", "Should the final note feel complete or leave you wanting more?", QuestionDomain.MUSICIAN, "melody", "Gemini", depth_level=2),

    # THEORY (25)
    BankQuestion("m_th_001", "What time signature feels right? 4/4? 3/4? 6/8? Something unusual?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=1),
    BankQuestion("m_th_002", "Do you want any time signature changes?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=2),
    BankQuestion("m_th_003", "What tempo range are you thinking? BPM?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=1),
    BankQuestion("m_th_004", "Should the tempo stay constant or change?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=1),
    BankQuestion("m_th_005", "Should there be any rubato (tempo flexibility)?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=2),
    BankQuestion("m_th_006", "Do you want polyrhythms or cross-rhythms?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=3),
    BankQuestion("m_th_007", "Should the song have a swing feel or straight?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=1),
    BankQuestion("m_th_008", "Do you want any metric modulation?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=3),
    BankQuestion("m_th_009", "Should the phrasing be in 4-bar or 8-bar sections?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=2),
    BankQuestion("m_th_010", "Do you want any odd phrase lengths (5 bars, 7 bars)?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=2),
    BankQuestion("m_th_011", "Should there be any hemiola (3 against 2)?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=3),
    BankQuestion("m_th_012", "Do you want the downbeat to be emphasized or hidden?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=2),
    BankQuestion("m_th_013", "Should there be any drum fills before section changes?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=1),
    BankQuestion("m_th_014", "Do you want any half-time or double-time sections?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=2),
    BankQuestion("m_th_015", "Should the rhythm feel tight or loose?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=1),
    BankQuestion("m_th_016", "Do you want any tuplets (triplets, quintuplets)?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=2),
    BankQuestion("m_th_017", "Should there be any fermatas (held notes)?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=2),
    BankQuestion("m_th_018", "Do you want any stop-time moments?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=2),
    BankQuestion("m_th_019", "Should the rhythm section lock tight or play conversationally?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=2),
    BankQuestion("m_th_020", "Do you want any rhythmic displacement?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=3),
    BankQuestion("m_th_021", "Should the beat feel rushed, laid back, or right on?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=1),
    BankQuestion("m_th_022", "Do you want any accelerando or ritardando?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=2),
    BankQuestion("m_th_023", "Should there be any breakdowns or buildups?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=1),
    BankQuestion("m_th_024", "Do you want the groove to be human or machine-like?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=1),
    BankQuestion("m_th_025", "Should there be any polymetric elements?", QuestionDomain.MUSICIAN, "theory", "Gemini", depth_level=3),

    # KEY & MODE (20)
    BankQuestion("m_km_001", "Does this emotion feel sharp or flat? (Key choice)", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=1),
    BankQuestion("m_km_002", "Should this be in a singer-friendly key?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=1),
    BankQuestion("m_km_003", "Do certain instruments sound better in specific keys for this?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=2),
    BankQuestion("m_km_004", "Would a modal approach work better than major/minor?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=2),
    BankQuestion("m_km_005", "Should the relative major/minor be used anywhere?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=2),
    BankQuestion("m_km_006", "Does Dorian mode's bittersweet quality fit?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=2),
    BankQuestion("m_km_007", "Would Mixolydian's bluesy brightness work?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=2),
    BankQuestion("m_km_008", "Does Phrygian's dark, Spanish flavor fit?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=2),
    BankQuestion("m_km_009", "Would Lydian's dreamy brightness work?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=2),
    BankQuestion("m_km_010", "Should harmonic minor be used for its exotic quality?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=2),
    BankQuestion("m_km_011", "Would melodic minor add sophistication?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=2),
    BankQuestion("m_km_012", "Should the key match the mood (bright keys vs dark keys)?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=1),
    BankQuestion("m_km_013", "Do you want any modal mixture (combining modes)?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=2),
    BankQuestion("m_km_014", "Should there be a key change for the final chorus?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=1),
    BankQuestion("m_km_015", "Would pentatonic scales simplify or enhance this?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=2),
    BankQuestion("m_km_016", "Should blues scale be incorporated?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=2),
    BankQuestion("m_km_017", "Would whole tone scale's ambiguity fit anywhere?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=3),
    BankQuestion("m_km_018", "Should diminished scale be used for tension?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=3),
    BankQuestion("m_km_019", "Would chromatic scale passages add drama?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=2),
    BankQuestion("m_km_020", "Should the mode change between sections?", QuestionDomain.MUSICIAN, "key_mode", "Gemini", depth_level=2),

    # CHORD PROGRESSIONS (15)
    BankQuestion("m_cp_001", "Do you want a circular or linear progression?", QuestionDomain.MUSICIAN, "chord_progression", "Gemini", depth_level=2),
    BankQuestion("m_cp_002", "Should the progression feel familiar or unusual?", QuestionDomain.MUSICIAN, "chord_progression", "Gemini", depth_level=1),
    BankQuestion("m_cp_003", "Do you want any common progressions (I-V-vi-IV) or avoid them?", QuestionDomain.MUSICIAN, "chord_progression", "Gemini", depth_level=1),
    BankQuestion("m_cp_004", "Should the verse progression be more static or moving?", QuestionDomain.MUSICIAN, "chord_progression", "Gemini", depth_level=2),
    BankQuestion("m_cp_005", "Should the chorus progression feel more resolved?", QuestionDomain.MUSICIAN, "chord_progression", "Gemini", depth_level=2),
    BankQuestion("m_cp_006", "Do you want any plagal (IV-I) cadences?", QuestionDomain.MUSICIAN, "chord_progression", "Gemini", depth_level=2),
    BankQuestion("m_cp_007", "Should there be any backwards progressions?", QuestionDomain.MUSICIAN, "chord_progression", "Gemini", depth_level=2),
    BankQuestion("m_cp_008", "Do you want any ascending or descending bass lines?", QuestionDomain.MUSICIAN, "chord_progression", "Gemini", depth_level=2),
    BankQuestion("m_cp_009", "Should the progression repeat or evolve?", QuestionDomain.MUSICIAN, "chord_progression", "Gemini", depth_level=1),
    BankQuestion("m_cp_010", "Do you want any passing chords?", QuestionDomain.MUSICIAN, "chord_progression", "Gemini", depth_level=2),
    BankQuestion("m_cp_011", "Should there be any dramatic chord changes?", QuestionDomain.MUSICIAN, "chord_progression", "Gemini", depth_level=1),
    BankQuestion("m_cp_012", "Do you want the bridge to go to unexpected harmonic territory?", QuestionDomain.MUSICIAN, "chord_progression", "Gemini", depth_level=2),
    BankQuestion("m_cp_013", "Should the outro fade on a repeating progression?", QuestionDomain.MUSICIAN, "chord_progression", "Gemini", depth_level=1),
    BankQuestion("m_cp_014", "Do you want any chord substitutions?", QuestionDomain.MUSICIAN, "chord_progression", "Gemini", depth_level=2),
    BankQuestion("m_cp_015", "Should the progression serve the vocals or stand alone?", QuestionDomain.MUSICIAN, "chord_progression", "Gemini", depth_level=2),

    # VOICE LEADING (10)
    BankQuestion("m_vl_001", "Should the voice leading be smooth or have dramatic jumps?", QuestionDomain.MUSICIAN, "voice_leading", "Gemini", depth_level=2),
    BankQuestion("m_vl_002", "Do you want parallel motion or contrary motion?", QuestionDomain.MUSICIAN, "voice_leading", "Gemini", depth_level=2),
    BankQuestion("m_vl_003", "Should any voices sustain across chord changes?", QuestionDomain.MUSICIAN, "voice_leading", "Gemini", depth_level=2),
    BankQuestion("m_vl_004", "Do you want any voice crossing for texture?", QuestionDomain.MUSICIAN, "voice_leading", "Gemini", depth_level=2),
    BankQuestion("m_vl_005", "Should the inner voices be interesting or invisible?", QuestionDomain.MUSICIAN, "voice_leading", "Gemini", depth_level=2),
    BankQuestion("m_vl_006", "Do you want any chromatic voice leading?", QuestionDomain.MUSICIAN, "voice_leading", "Gemini", depth_level=2),
    BankQuestion("m_vl_007", "Should the bass line be melodic or just root-based?", QuestionDomain.MUSICIAN, "voice_leading", "Gemini", depth_level=2),
    BankQuestion("m_vl_008", "Do you want any suspensions that resolve?", QuestionDomain.MUSICIAN, "voice_leading", "Gemini", depth_level=2),
    BankQuestion("m_vl_009", "Should there be any close vs open voicings?", QuestionDomain.MUSICIAN, "voice_leading", "Gemini", depth_level=2),
    BankQuestion("m_vl_010", "Do you want any spread voicings for drama?", QuestionDomain.MUSICIAN, "voice_leading", "Gemini", depth_level=2),
]


# =============================================================================
# COPILOT'S QUESTIONS: Production/Arrangement/Technical (125)
# =============================================================================

COPILOT_MUSICIAN_QUESTIONS = [
    # PRODUCTION (30)
    BankQuestion("m_pr_001", "Should this sound polished or raw?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=1),
    BankQuestion("m_pr_002", "Do you want any lo-fi elements?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=1),
    BankQuestion("m_pr_003", "Should there be any vinyl/tape saturation?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_004", "Do you want room ambience or a dry sound?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=1),
    BankQuestion("m_pr_005", "Should there be any obvious production ear candy?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_006", "Do you want any reverse effects?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_007", "Should there be any risers or sweeps?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=1),
    BankQuestion("m_pr_008", "Do you want any glitch effects?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_009", "Should vocals have heavy processing or be natural?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=1),
    BankQuestion("m_pr_010", "Do you want any vocal chops or samples?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_011", "Should there be any sidechain pumping?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_012", "Do you want any filter sweeps?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_013", "Should the production feel modern or vintage?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=1),
    BankQuestion("m_pr_014", "Do you want any samples or should it be all original?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=1),
    BankQuestion("m_pr_015", "Should there be any automation rides?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_016", "Do you want any stereo effects (panning moves, width)?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_017", "Should the low end be tight or boomy?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_018", "Do you want any distortion or saturation?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_019", "Should there be any delays synced to tempo?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_020", "Do you want any reverb throws on specific words?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_021", "Should the production feel full or sparse?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=1),
    BankQuestion("m_pr_022", "Do you want any pitch effects (pitch shifting, formant)?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_023", "Should there be any granular/textural elements?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_024", "Do you want any modulation effects (chorus, phaser, flanger)?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_025", "Should the production reference a specific era?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=1),
    BankQuestion("m_pr_026", "Do you want any found sounds or field recordings?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_027", "Should there be any silence used as an effect?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_028", "Do you want any bass drops or sub moments?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_029", "Should any sounds feel intentionally imperfect?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=2),
    BankQuestion("m_pr_030", "Do you want any transitions between sections to be smooth or abrupt?", QuestionDomain.MUSICIAN, "production", "Copilot", depth_level=1),

    # ARRANGEMENT (30)
    BankQuestion("m_ar_001", "What's the song structure? (Verse-Chorus-Verse-Chorus-Bridge-Chorus?)", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=1),
    BankQuestion("m_ar_002", "Should there be an intro? How long?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=1),
    BankQuestion("m_ar_003", "Do you want a pre-chorus?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=1),
    BankQuestion("m_ar_004", "Should there be a bridge or breakdown?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=1),
    BankQuestion("m_ar_005", "Do you want an outro or should it end abruptly?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=1),
    BankQuestion("m_ar_006", "Should each section have different instrumentation?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=2),
    BankQuestion("m_ar_007", "Do you want the arrangement to build or stay consistent?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=1),
    BankQuestion("m_ar_008", "Should any section be stripped down to just vocals?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=2),
    BankQuestion("m_ar_009", "Do you want any instrumental sections?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=1),
    BankQuestion("m_ar_010", "Should the final chorus be bigger than the others?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=1),
    BankQuestion("m_ar_011", "Do you want any counter-melodies?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=2),
    BankQuestion("m_ar_012", "Should there be any gang vocals or group parts?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=2),
    BankQuestion("m_ar_013", "Do you want any ad-libs?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=2),
    BankQuestion("m_ar_014", "Should harmonies come in at specific points?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=2),
    BankQuestion("m_ar_015", "Do you want any solo sections?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=2),
    BankQuestion("m_ar_016", "Should elements drop out at any point?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=2),
    BankQuestion("m_ar_017", "Do you want any unexpected arrangement twists?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=2),
    BankQuestion("m_ar_018", "Should the song have dynamics (loud/quiet) or stay at one level?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=1),
    BankQuestion("m_ar_019", "Do you want any call-and-response sections?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=2),
    BankQuestion("m_ar_020", "Should the bridge contrast dramatically with the rest?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=2),
    BankQuestion("m_ar_021", "Do you want the song to fade out or end cold?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=1),
    BankQuestion("m_ar_022", "Should different verses have different arrangements?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=2),
    BankQuestion("m_ar_023", "Do you want any surprise elements (key change, tempo change)?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=2),
    BankQuestion("m_ar_024", "Should the arrangement leave space or fill everything?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=1),
    BankQuestion("m_ar_025", "Do you want any tension-building sections?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=2),
    BankQuestion("m_ar_026", "Should there be any false endings?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=2),
    BankQuestion("m_ar_027", "Do you want the hook to be in the verse, chorus, or both?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=2),
    BankQuestion("m_ar_028", "Should there be any a cappella moments?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=2),
    BankQuestion("m_ar_029", "Do you want any instrumental hooks/riffs?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=2),
    BankQuestion("m_ar_030", "Should the song structure be conventional or experimental?", QuestionDomain.MUSICIAN, "arrangement", "Copilot", depth_level=1),

    # RHYTHM & GROOVE (25)
    BankQuestion("m_rg_001", "What drum sounds fit this emotion? Acoustic? Electronic? Both?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=1),
    BankQuestion("m_rg_002", "Should the drums be tight/quantized or loose/human?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=1),
    BankQuestion("m_rg_003", "Do you want any 808s or heavy sub bass?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=2),
    BankQuestion("m_rg_004", "Should the snare be on 2 and 4, or somewhere else?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=2),
    BankQuestion("m_rg_005", "Do you want any ghost notes on the drums?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=2),
    BankQuestion("m_rg_006", "Should the hi-hats be busy or minimal?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=2),
    BankQuestion("m_rg_007", "Do you want any percussion beyond the main kit?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=2),
    BankQuestion("m_rg_008", "Should the kick pattern be four-on-the-floor or syncopated?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=2),
    BankQuestion("m_rg_009", "Do you want any claps or snaps?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=2),
    BankQuestion("m_rg_010", "Should the groove change between sections?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=2),
    BankQuestion("m_rg_011", "Do you want any half-time feel sections?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=2),
    BankQuestion("m_rg_012", "Should there be any breakdown sections without drums?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=2),
    BankQuestion("m_rg_013", "Do you want any programmed or live drums?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=1),
    BankQuestion("m_rg_014", "Should the groove feel aggressive or relaxed?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=1),
    BankQuestion("m_rg_015", "Do you want any swing or shuffle?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=1),
    BankQuestion("m_rg_016", "Should there be any drum fills? How busy?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=1),
    BankQuestion("m_rg_017", "Do you want any layered drum sounds?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=2),
    BankQuestion("m_rg_018", "Should the bass lock with the kick or play independently?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=2),
    BankQuestion("m_rg_019", "Do you want any rhythmic stabs or hits?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=2),
    BankQuestion("m_rg_020", "Should the groove be danceable or more listen-focused?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=1),
    BankQuestion("m_rg_021", "Do you want any tom fills or cymbal crashes?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=2),
    BankQuestion("m_rg_022", "Should the rhythm section feel live or programmed?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=1),
    BankQuestion("m_rg_023", "Do you want any tempo changes mid-song?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=2),
    BankQuestion("m_rg_024", "Should the groove have any world music influences?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=2),
    BankQuestion("m_rg_025", "Do you want any breakbeat or sampled drums?", QuestionDomain.MUSICIAN, "rhythm", "Copilot", depth_level=2),

    # SOUND DESIGN (20)
    BankQuestion("m_sd_001", "What synth sounds fit this emotion? Pads? Leads? Arps?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=1),
    BankQuestion("m_sd_002", "Should synths be analog-sounding or digital?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=2),
    BankQuestion("m_sd_003", "Do you want any atmospheric textures?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=2),
    BankQuestion("m_sd_004", "Should there be any drones or sustained notes?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=2),
    BankQuestion("m_sd_005", "Do you want any white noise or risers?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=2),
    BankQuestion("m_sd_006", "Should there be any vocoder or talkbox?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=2),
    BankQuestion("m_sd_007", "Do you want any glitchy or granular sounds?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=2),
    BankQuestion("m_sd_008", "Should there be any FM or additive synthesis tones?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=3),
    BankQuestion("m_sd_009", "Do you want any pluck or bell sounds?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=2),
    BankQuestion("m_sd_010", "Should there be any modular/experimental sounds?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=2),
    BankQuestion("m_sd_011", "Do you want any arpeggiated patterns?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=2),
    BankQuestion("m_sd_012", "Should synths evolve over time or stay static?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=2),
    BankQuestion("m_sd_013", "Do you want any wavetable scanning?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=3),
    BankQuestion("m_sd_014", "Should there be any supersaw or detuned sounds?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=2),
    BankQuestion("m_sd_015", "Do you want any bass synths? What character?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=2),
    BankQuestion("m_sd_016", "Should there be any organic/acoustic elements mixed with synths?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=2),
    BankQuestion("m_sd_017", "Do you want any bitcrushed or lo-fi digital sounds?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=2),
    BankQuestion("m_sd_018", "Should synth patches be preset-based or custom-designed?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=2),
    BankQuestion("m_sd_019", "Do you want any foley or real-world sound design?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=2),
    BankQuestion("m_sd_020", "Should any sounds feel otherworldly or grounded?", QuestionDomain.MUSICIAN, "sound_design", "Copilot", depth_level=2),

    # MIX (10)
    BankQuestion("m_mx_001", "Should the mix feel wide or narrow?", QuestionDomain.MUSICIAN, "mix", "Copilot", depth_level=2),
    BankQuestion("m_mx_002", "Do you want the vocals up front or blended?", QuestionDomain.MUSICIAN, "mix", "Copilot", depth_level=1),
    BankQuestion("m_mx_003", "Should the bass be prominent or supportive?", QuestionDomain.MUSICIAN, "mix", "Copilot", depth_level=2),
    BankQuestion("m_mx_004", "Do you want the mix to be loud/compressed or dynamic?", QuestionDomain.MUSICIAN, "mix", "Copilot", depth_level=2),
    BankQuestion("m_mx_005", "Should certain elements pan hard or stay centered?", QuestionDomain.MUSICIAN, "mix", "Copilot", depth_level=2),
    BankQuestion("m_mx_006", "Do you want any mid/side processing?", QuestionDomain.MUSICIAN, "mix", "Copilot", depth_level=3),
    BankQuestion("m_mx_007", "Should the mix reference a specific artist/song?", QuestionDomain.MUSICIAN, "mix", "Copilot", depth_level=2),
    BankQuestion("m_mx_008", "Do you want any parallel compression?", QuestionDomain.MUSICIAN, "mix", "Copilot", depth_level=3),
    BankQuestion("m_mx_009", "Should there be any frequency-specific effects (multiband)?", QuestionDomain.MUSICIAN, "mix", "Copilot", depth_level=3),
    BankQuestion("m_mx_010", "Do you want the mix to feel spacious or intimate?", QuestionDomain.MUSICIAN, "mix", "Copilot", depth_level=2),

    # GENRE (10)
    BankQuestion("m_ge_001", "What genre is this song closest to?", QuestionDomain.MUSICIAN, "genre", "Copilot", depth_level=1),
    BankQuestion("m_ge_002", "Are there any genre conventions you want to follow?", QuestionDomain.MUSICIAN, "genre", "Copilot", depth_level=2),
    BankQuestion("m_ge_003", "Are there any genre conventions you want to break?", QuestionDomain.MUSICIAN, "genre", "Copilot", depth_level=2),
    BankQuestion("m_ge_004", "Should this blend multiple genres?", QuestionDomain.MUSICIAN, "genre", "Copilot", depth_level=2),
    BankQuestion("m_ge_005", "What subgenre fits best?", QuestionDomain.MUSICIAN, "genre", "Copilot", depth_level=2),
    BankQuestion("m_ge_006", "What era of this genre are you channeling?", QuestionDomain.MUSICIAN, "genre", "Copilot", depth_level=2),
    BankQuestion("m_ge_007", "Should genre expectations be subverted?", QuestionDomain.MUSICIAN, "genre", "Copilot", depth_level=2),
    BankQuestion("m_ge_008", "What reference track captures the vibe?", QuestionDomain.MUSICIAN, "genre", "Copilot", depth_level=1),
    BankQuestion("m_ge_009", "Is this genre right for the emotion, or should we experiment?", QuestionDomain.MUSICIAN, "genre", "Copilot", depth_level=2),
    BankQuestion("m_ge_010", "How genre-pure vs genre-fluid should this be?", QuestionDomain.MUSICIAN, "genre", "Copilot", depth_level=2),
]


# =============================================================================
# COMBINED QUESTION BANK
# =============================================================================

ALL_THERAPY_QUESTIONS = CLAUDE_THERAPY_QUESTIONS + CHATGPT_THERAPY_QUESTIONS
ALL_MUSICIAN_QUESTIONS = GEMINI_MUSICIAN_QUESTIONS + COPILOT_MUSICIAN_QUESTIONS
ALL_QUESTIONS = ALL_THERAPY_QUESTIONS + ALL_MUSICIAN_QUESTIONS


def get_questions_by_ai(ai_name: str) -> List[BankQuestion]:
    """Get all questions assigned to a specific AI."""
    return [q for q in ALL_QUESTIONS if q.assigned_ai == ai_name]


def get_questions_by_domain(domain: QuestionDomain) -> List[BankQuestion]:
    """Get all questions in a domain (therapy or musician)."""
    return [q for q in ALL_QUESTIONS if q.domain == domain]


def get_questions_by_category(category: str) -> List[BankQuestion]:
    """Get all questions in a specific category."""
    return [q for q in ALL_QUESTIONS if q.category == category]


def get_questions_by_depth(depth: int) -> List[BankQuestion]:
    """Get questions at a specific depth level (1=surface, 2=deeper, 3=core)."""
    return [q for q in ALL_QUESTIONS if q.depth_level == depth]


def get_random_questions(n: int, domain: Optional[QuestionDomain] = None) -> List[BankQuestion]:
    """Get n random questions, optionally filtered by domain."""
    import random
    pool = get_questions_by_domain(domain) if domain else ALL_QUESTIONS
    return random.sample(pool, min(n, len(pool)))


# =============================================================================
# STATISTICS
# =============================================================================

def get_question_stats() -> dict:
    """Get statistics about the question bank."""
    return {
        "total_questions": len(ALL_QUESTIONS),
        "therapy_questions": len(ALL_THERAPY_QUESTIONS),
        "musician_questions": len(ALL_MUSICIAN_QUESTIONS),
        "by_ai": {
            "Claude": len(get_questions_by_ai("Claude")),
            "ChatGPT": len(get_questions_by_ai("ChatGPT")),
            "Gemini": len(get_questions_by_ai("Gemini")),
            "Copilot": len(get_questions_by_ai("Copilot")),
        },
        "by_depth": {
            "surface": len(get_questions_by_depth(1)),
            "deeper": len(get_questions_by_depth(2)),
            "core": len(get_questions_by_depth(3)),
        },
        "therapy_categories": list(set(q.category for q in ALL_THERAPY_QUESTIONS)),
        "musician_categories": list(set(q.category for q in ALL_MUSICIAN_QUESTIONS)),
    }


# Export
__all__ = [
    'QuestionDomain',
    'TherapyCategory',
    'MusicianCategory',
    'BankQuestion',
    'CLAUDE_THERAPY_QUESTIONS',
    'CHATGPT_THERAPY_QUESTIONS',
    'GEMINI_MUSICIAN_QUESTIONS',
    'COPILOT_MUSICIAN_QUESTIONS',
    'ALL_THERAPY_QUESTIONS',
    'ALL_MUSICIAN_QUESTIONS',
    'ALL_QUESTIONS',
    'get_questions_by_ai',
    'get_questions_by_domain',
    'get_questions_by_category',
    'get_questions_by_depth',
    'get_random_questions',
    'get_question_stats',
]


if __name__ == "__main__":
    stats = get_question_stats()
    print("\n" + "=" * 60)
    print("  QUESTION BANK STATISTICS")
    print("=" * 60)
    print(f"\n  Total Questions: {stats['total_questions']}")
    print(f"  Therapy Questions: {stats['therapy_questions']}")
    print(f"  Musician Questions: {stats['musician_questions']}")
    print(f"\n  By AI Assignment:")
    for ai, count in stats['by_ai'].items():
        print(f"    {ai}: {count}")
    print(f"\n  By Depth Level:")
    for depth, count in stats['by_depth'].items():
        print(f"    {depth}: {count}")
    print(f"\n  Therapy Categories: {len(stats['therapy_categories'])}")
    print(f"  Musician Categories: {len(stats['musician_categories'])}")
