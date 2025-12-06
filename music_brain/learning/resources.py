"""
Resource Fetcher - Retrieve and cache training content from web sources.

Provides:
- ResourceFetcher for downloading content from known educational sites
- ResourceCache for storing fetched content
- Content parsing and normalization
- Rate limiting and respectful crawling

Philosophy: "Stand on the shoulders of giants - learn from the best educators."
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib
import time
import re
from urllib.parse import urlparse, urljoin


class ResourceType(Enum):
    """Types of learning resources."""
    ARTICLE = auto()           # Text-based tutorial/lesson
    VIDEO = auto()             # Video tutorial
    INTERACTIVE = auto()       # Interactive exercise
    SHEET_MUSIC = auto()       # Notation/tabs
    AUDIO = auto()             # Audio example/backing track
    EXERCISE = auto()          # Practice exercise
    COURSE = auto()            # Multi-part course
    LESSON_PLAN = auto()       # Structured lesson
    REFERENCE = auto()         # Reference material (scales, chords, etc.)
    TOOL = auto()              # Online tool (metronome, tuner, etc.)


@dataclass
class LearningResource:
    """A fetched learning resource."""
    id: str
    url: str
    title: str
    resource_type: ResourceType
    source_name: str

    # Content
    description: str = ""
    content_text: str = ""          # Main text content
    content_html: str = ""          # Raw HTML (for parsing)
    content_markdown: str = ""      # Converted to markdown

    # Classification
    instrument: str = ""
    difficulty_estimate: int = 5    # 1-10 scale
    skill_categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    # Media
    video_urls: List[str] = field(default_factory=list)
    audio_urls: List[str] = field(default_factory=list)
    image_urls: List[str] = field(default_factory=list)

    # Metadata
    author: str = ""
    publish_date: Optional[str] = None
    last_fetched: Optional[str] = None
    language: str = "en"

    # Quality indicators
    has_video: bool = False
    has_audio: bool = False
    has_notation: bool = False
    estimated_duration_minutes: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "url": self.url,
            "title": self.title,
            "resource_type": self.resource_type.name,
            "source_name": self.source_name,
            "description": self.description,
            "content_text": self.content_text,
            "content_markdown": self.content_markdown,
            "instrument": self.instrument,
            "difficulty_estimate": self.difficulty_estimate,
            "skill_categories": self.skill_categories,
            "tags": self.tags,
            "video_urls": self.video_urls,
            "audio_urls": self.audio_urls,
            "image_urls": self.image_urls,
            "author": self.author,
            "publish_date": self.publish_date,
            "last_fetched": self.last_fetched,
            "language": self.language,
            "has_video": self.has_video,
            "has_audio": self.has_audio,
            "has_notation": self.has_notation,
            "estimated_duration_minutes": self.estimated_duration_minutes,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LearningResource':
        return cls(
            id=data["id"],
            url=data["url"],
            title=data["title"],
            resource_type=ResourceType[data["resource_type"]],
            source_name=data["source_name"],
            description=data.get("description", ""),
            content_text=data.get("content_text", ""),
            content_markdown=data.get("content_markdown", ""),
            instrument=data.get("instrument", ""),
            difficulty_estimate=data.get("difficulty_estimate", 5),
            skill_categories=data.get("skill_categories", []),
            tags=data.get("tags", []),
            video_urls=data.get("video_urls", []),
            audio_urls=data.get("audio_urls", []),
            image_urls=data.get("image_urls", []),
            author=data.get("author", ""),
            publish_date=data.get("publish_date"),
            last_fetched=data.get("last_fetched"),
            language=data.get("language", "en"),
            has_video=data.get("has_video", False),
            has_audio=data.get("has_audio", False),
            has_notation=data.get("has_notation", False),
            estimated_duration_minutes=data.get("estimated_duration_minutes", 0),
        )


# Known educational sources with metadata
KNOWN_SOURCES = {
    # Guitar Resources
    "justinguitar": {
        "name": "JustinGuitar",
        "base_url": "https://www.justinguitar.com",
        "instruments": ["guitar", "acoustic_guitar", "electric_guitar"],
        "content_types": [ResourceType.VIDEO, ResourceType.LESSON_PLAN, ResourceType.COURSE],
        "difficulty_range": (1, 7),
        "quality_score": 9,
        "description": "Free guitar lessons from beginner to advanced",
        "search_patterns": {
            "beginner": "/categories/beginner-guitar-lessons",
            "intermediate": "/categories/intermediate-guitar",
            "songs": "/categories/songs",
        },
    },
    "guitarlessons": {
        "name": "GuitarLessons.com",
        "base_url": "https://www.guitarlessons.com",
        "instruments": ["guitar"],
        "content_types": [ResourceType.VIDEO, ResourceType.ARTICLE],
        "difficulty_range": (1, 8),
        "quality_score": 8,
        "description": "Structured guitar curriculum",
    },
    "ultimate_guitar": {
        "name": "Ultimate Guitar",
        "base_url": "https://www.ultimate-guitar.com",
        "instruments": ["guitar", "bass", "ukulele"],
        "content_types": [ResourceType.SHEET_MUSIC, ResourceType.REFERENCE],
        "difficulty_range": (1, 10),
        "quality_score": 7,
        "description": "Tabs and chords for thousands of songs",
    },

    # Piano Resources
    "pianote": {
        "name": "Pianote",
        "base_url": "https://www.pianote.com",
        "instruments": ["piano", "keyboard"],
        "content_types": [ResourceType.VIDEO, ResourceType.COURSE],
        "difficulty_range": (1, 8),
        "quality_score": 9,
        "description": "Modern piano lessons for all levels",
    },
    "pianolessons": {
        "name": "PianoLessons.com",
        "base_url": "https://www.pianolessons.com",
        "instruments": ["piano"],
        "content_types": [ResourceType.VIDEO, ResourceType.ARTICLE],
        "difficulty_range": (1, 6),
        "quality_score": 7,
        "description": "Free piano tutorials",
    },
    "musictheory_net": {
        "name": "MusicTheory.net",
        "base_url": "https://www.musictheory.net",
        "instruments": ["piano", "theory"],
        "content_types": [ResourceType.INTERACTIVE, ResourceType.REFERENCE],
        "difficulty_range": (1, 7),
        "quality_score": 9,
        "description": "Interactive music theory lessons",
    },

    # Drums Resources
    "drumeo": {
        "name": "Drumeo",
        "base_url": "https://www.drumeo.com",
        "instruments": ["drums", "percussion"],
        "content_types": [ResourceType.VIDEO, ResourceType.COURSE],
        "difficulty_range": (1, 10),
        "quality_score": 10,
        "description": "World-class drum education",
    },
    "freedrumlessons": {
        "name": "FreeDrumLessons",
        "base_url": "https://www.freedrumlessons.com",
        "instruments": ["drums"],
        "content_types": [ResourceType.VIDEO, ResourceType.ARTICLE],
        "difficulty_range": (1, 7),
        "quality_score": 7,
        "description": "Free drum tutorials and exercises",
    },

    # Bass Resources
    "studybass": {
        "name": "StudyBass",
        "base_url": "https://www.studybass.com",
        "instruments": ["bass", "electric_bass"],
        "content_types": [ResourceType.ARTICLE, ResourceType.INTERACTIVE],
        "difficulty_range": (1, 8),
        "quality_score": 9,
        "description": "Comprehensive bass guitar curriculum",
    },
    "talkingbass": {
        "name": "TalkingBass",
        "base_url": "https://www.talkingbass.net",
        "instruments": ["bass"],
        "content_types": [ResourceType.VIDEO, ResourceType.COURSE],
        "difficulty_range": (1, 9),
        "quality_score": 9,
        "description": "Professional bass education",
    },

    # Voice/Singing Resources
    "singwise": {
        "name": "SingWise",
        "base_url": "https://www.singwise.com",
        "instruments": ["voice", "vocals"],
        "content_types": [ResourceType.ARTICLE, ResourceType.EXERCISE],
        "difficulty_range": (1, 10),
        "quality_score": 8,
        "description": "Vocal technique and singing lessons",
    },

    # Multi-Instrument / General
    "musicradar": {
        "name": "MusicRadar",
        "base_url": "https://www.musicradar.com",
        "instruments": ["guitar", "bass", "drums", "keyboard", "production"],
        "content_types": [ResourceType.ARTICLE, ResourceType.VIDEO],
        "difficulty_range": (1, 8),
        "quality_score": 7,
        "description": "Tutorials for multiple instruments",
    },
    "fender_play": {
        "name": "Fender Play",
        "base_url": "https://www.fender.com/play",
        "instruments": ["guitar", "bass", "ukulele"],
        "content_types": [ResourceType.VIDEO, ResourceType.COURSE],
        "difficulty_range": (1, 5),
        "quality_score": 8,
        "description": "Beginner-focused guitar and bass lessons",
    },
    "yousician": {
        "name": "Yousician",
        "base_url": "https://yousician.com",
        "instruments": ["guitar", "piano", "bass", "ukulele", "voice"],
        "content_types": [ResourceType.INTERACTIVE, ResourceType.COURSE],
        "difficulty_range": (1, 6),
        "quality_score": 8,
        "description": "Gamified music learning",
    },

    # Theory and Ear Training
    "teoria": {
        "name": "Teoria",
        "base_url": "https://www.teoria.com",
        "instruments": ["theory"],
        "content_types": [ResourceType.INTERACTIVE, ResourceType.REFERENCE],
        "difficulty_range": (1, 8),
        "quality_score": 8,
        "description": "Music theory tutorials and exercises",
    },
    "tonedear": {
        "name": "ToneDear",
        "base_url": "https://tonedear.com",
        "instruments": ["ear_training"],
        "content_types": [ResourceType.INTERACTIVE, ResourceType.TOOL],
        "difficulty_range": (1, 10),
        "quality_score": 8,
        "description": "Ear training exercises",
    },
    "musictheory_net_exercises": {
        "name": "MusicTheory.net Exercises",
        "base_url": "https://www.musictheory.net/exercises",
        "instruments": ["theory", "ear_training"],
        "content_types": [ResourceType.INTERACTIVE],
        "difficulty_range": (1, 7),
        "quality_score": 9,
        "description": "Interactive theory and ear training",
    },

    # Orchestral/Classical
    "imslp": {
        "name": "IMSLP",
        "base_url": "https://imslp.org",
        "instruments": ["violin", "viola", "cello", "flute", "clarinet", "piano", "orchestra"],
        "content_types": [ResourceType.SHEET_MUSIC],
        "difficulty_range": (3, 10),
        "quality_score": 10,
        "description": "Free public domain sheet music",
    },
    "8notes": {
        "name": "8notes",
        "base_url": "https://www.8notes.com",
        "instruments": ["violin", "flute", "clarinet", "saxophone", "trumpet", "piano"],
        "content_types": [ResourceType.SHEET_MUSIC, ResourceType.ARTICLE],
        "difficulty_range": (1, 7),
        "quality_score": 7,
        "description": "Free sheet music and lessons",
    },

    # Production/DAW
    "soundonsound": {
        "name": "Sound On Sound",
        "base_url": "https://www.soundonsound.com",
        "instruments": ["production", "mixing", "mastering"],
        "content_types": [ResourceType.ARTICLE, ResourceType.REFERENCE],
        "difficulty_range": (3, 10),
        "quality_score": 10,
        "description": "Professional audio production techniques",
    },
    "groove3": {
        "name": "Groove3",
        "base_url": "https://www.groove3.com",
        "instruments": ["production", "synthesizer"],
        "content_types": [ResourceType.VIDEO, ResourceType.COURSE],
        "difficulty_range": (2, 9),
        "quality_score": 9,
        "description": "DAW and plugin tutorials",
    },
}


class ResourceCache:
    """Cache for fetched resources with expiration."""

    def __init__(self, cache_dir: Optional[Path] = None, max_age_days: int = 30):
        self.cache_dir = cache_dir or Path.home() / ".daiw" / "learning_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_age = timedelta(days=max_age_days)
        self.index_file = self.cache_dir / "index.json"
        self._index: Dict[str, Dict[str, Any]] = self._load_index()

    def _load_index(self) -> Dict[str, Dict[str, Any]]:
        """Load the cache index."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_index(self) -> None:
        """Save the cache index."""
        with open(self.index_file, 'w') as f:
            json.dump(self._index, f, indent=2)

    def _get_cache_key(self, url: str) -> str:
        """Generate a cache key from URL."""
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def _is_expired(self, cached_date: str) -> bool:
        """Check if a cached item is expired."""
        try:
            cached = datetime.fromisoformat(cached_date)
            return datetime.now() - cached > self.max_age
        except (ValueError, TypeError):
            return True

    def get(self, url: str) -> Optional[LearningResource]:
        """Retrieve a resource from cache."""
        cache_key = self._get_cache_key(url)

        if cache_key not in self._index:
            return None

        entry = self._index[cache_key]
        if self._is_expired(entry.get("cached_at", "")):
            self.remove(url)
            return None

        cache_file = self.cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r') as f:
                return LearningResource.from_dict(json.load(f))
        except (json.JSONDecodeError, IOError):
            return None

    def put(self, resource: LearningResource) -> None:
        """Store a resource in cache."""
        cache_key = self._get_cache_key(resource.url)
        cache_file = self.cache_dir / f"{cache_key}.json"

        with open(cache_file, 'w') as f:
            json.dump(resource.to_dict(), f, indent=2)

        self._index[cache_key] = {
            "url": resource.url,
            "title": resource.title,
            "cached_at": datetime.now().isoformat(),
            "instrument": resource.instrument,
            "source": resource.source_name,
        }
        self._save_index()

    def remove(self, url: str) -> None:
        """Remove a resource from cache."""
        cache_key = self._get_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            cache_file.unlink()

        if cache_key in self._index:
            del self._index[cache_key]
            self._save_index()

    def clear(self) -> None:
        """Clear all cached resources."""
        for file in self.cache_dir.glob("*.json"):
            file.unlink()
        self._index = {}
        self._save_index()

    def list_cached(
        self,
        instrument: Optional[str] = None,
        source: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List cached resources with optional filtering."""
        results = []
        for entry in self._index.values():
            if instrument and entry.get("instrument") != instrument:
                continue
            if source and entry.get("source") != source:
                continue
            if not self._is_expired(entry.get("cached_at", "")):
                results.append(entry)
        return results


class ResourceFetcher:
    """
    Fetcher for learning resources from educational websites.

    Uses AI-assisted parsing to extract structured content from web pages.
    Implements rate limiting and respectful crawling practices.
    """

    def __init__(
        self,
        cache: Optional[ResourceCache] = None,
        rate_limit_seconds: float = 2.0,
        user_agent: str = "DAiW-Learning-Module/1.0 (Educational Research)",
    ):
        self.cache = cache or ResourceCache()
        self.rate_limit = rate_limit_seconds
        self.user_agent = user_agent
        self._last_request_time: Dict[str, float] = {}

    def _respect_rate_limit(self, domain: str) -> None:
        """Wait if necessary to respect rate limiting."""
        last_time = self._last_request_time.get(domain, 0)
        elapsed = time.time() - last_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self._last_request_time[domain] = time.time()

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        parsed = urlparse(url)
        return parsed.netloc

    def get_sources_for_instrument(self, instrument: str) -> List[Dict[str, Any]]:
        """Get known sources that teach a specific instrument."""
        results = []
        instrument_lower = instrument.lower()
        for source_id, source in KNOWN_SOURCES.items():
            if instrument_lower in [i.lower() for i in source["instruments"]]:
                results.append({
                    "id": source_id,
                    **source,
                })
        return sorted(results, key=lambda x: x.get("quality_score", 0), reverse=True)

    def get_sources_by_difficulty(
        self,
        min_difficulty: int = 1,
        max_difficulty: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get sources that cover a specific difficulty range."""
        results = []
        for source_id, source in KNOWN_SOURCES.items():
            source_min, source_max = source.get("difficulty_range", (1, 10))
            if source_min <= max_difficulty and source_max >= min_difficulty:
                results.append({
                    "id": source_id,
                    **source,
                })
        return results

    def build_search_query(
        self,
        instrument: str,
        difficulty: int,
        skill_focus: Optional[str] = None,
        topic: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build a search query for finding resources.

        Returns a query object that can be used with AI-powered search.
        """
        difficulty_terms = {
            1: ["absolute beginner", "first lesson", "getting started"],
            2: ["beginner", "basics", "fundamentals"],
            3: ["beginner", "easy", "simple"],
            4: ["easy intermediate", "progressing"],
            5: ["intermediate", "developing"],
            6: ["late intermediate", "advancing"],
            7: ["early advanced", "challenging"],
            8: ["advanced", "complex"],
            9: ["very advanced", "virtuoso"],
            10: ["master class", "professional", "expert"],
        }

        query = {
            "instrument": instrument,
            "difficulty": difficulty,
            "difficulty_terms": difficulty_terms.get(difficulty, ["intermediate"]),
            "skill_focus": skill_focus,
            "topic": topic,
            "suggested_sources": self.get_sources_for_instrument(instrument),
        }

        # Build search strings for AI to use
        search_terms = [instrument, *difficulty_terms.get(difficulty, [])]
        if skill_focus:
            search_terms.append(skill_focus)
        if topic:
            search_terms.append(topic)

        query["search_string"] = " ".join(search_terms) + " lesson tutorial"
        query["search_string_beginner"] = f"{instrument} beginner lesson how to start"
        query["search_string_advanced"] = f"{instrument} advanced technique masterclass"

        return query

    def generate_fetch_prompt(
        self,
        url: str,
        instrument: str,
        expected_type: ResourceType = ResourceType.ARTICLE,
    ) -> str:
        """
        Generate a prompt for AI to use when fetching and parsing a resource.

        This prompt instructs the AI on how to extract structured content.
        """
        return f"""Fetch and analyze the content at: {url}

Extract the following information for a {instrument} learning resource:

1. TITLE: The main title of the lesson/article
2. DESCRIPTION: A 2-3 sentence summary
3. DIFFICULTY: Estimate 1-10 (1=absolute beginner, 10=expert)
4. CONTENT TYPE: {expected_type.name} or identify the actual type
5. SKILL CATEGORIES: Which skills does this teach? (technique, rhythm, theory, etc.)
6. MAIN CONTENT: The key teaching points and instructions
7. EXERCISES: Any practice exercises mentioned
8. VIDEO URLS: Any embedded video URLs
9. PREREQUISITES: What should the student know before this?
10. NEXT STEPS: What should the student learn after this?

Format your response as JSON with these fields:
{{
    "title": "",
    "description": "",
    "difficulty_estimate": 5,
    "resource_type": "ARTICLE",
    "skill_categories": [],
    "content_summary": "",
    "key_points": [],
    "exercises": [],
    "video_urls": [],
    "prerequisites": [],
    "next_steps": [],
    "tags": []
}}

Focus on extracting actionable learning content. Skip navigation, ads, and irrelevant content."""

    def parse_ai_response(
        self,
        response: str,
        url: str,
        source_name: str,
        instrument: str,
    ) -> LearningResource:
        """
        Parse an AI response into a LearningResource.

        The AI should have returned JSON matching our expected format.
        """
        # Try to extract JSON from the response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                data = json.loads(json_match.group())
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}

        # Generate a unique ID
        resource_id = hashlib.sha256(f"{url}:{datetime.now().isoformat()}".encode()).hexdigest()[:12]

        # Map resource type
        type_str = data.get("resource_type", "ARTICLE").upper()
        try:
            resource_type = ResourceType[type_str]
        except KeyError:
            resource_type = ResourceType.ARTICLE

        return LearningResource(
            id=resource_id,
            url=url,
            title=data.get("title", "Untitled Resource"),
            resource_type=resource_type,
            source_name=source_name,
            description=data.get("description", ""),
            content_text=data.get("content_summary", ""),
            content_markdown=self._format_as_markdown(data),
            instrument=instrument,
            difficulty_estimate=data.get("difficulty_estimate", 5),
            skill_categories=data.get("skill_categories", []),
            tags=data.get("tags", []),
            video_urls=data.get("video_urls", []),
            has_video=len(data.get("video_urls", [])) > 0,
            last_fetched=datetime.now().isoformat(),
        )

    def _format_as_markdown(self, data: Dict[str, Any]) -> str:
        """Format parsed data as markdown for storage."""
        lines = []

        if data.get("title"):
            lines.append(f"# {data['title']}")
            lines.append("")

        if data.get("description"):
            lines.append(data["description"])
            lines.append("")

        if data.get("key_points"):
            lines.append("## Key Points")
            for point in data["key_points"]:
                lines.append(f"- {point}")
            lines.append("")

        if data.get("exercises"):
            lines.append("## Exercises")
            for i, exercise in enumerate(data["exercises"], 1):
                if isinstance(exercise, dict):
                    lines.append(f"{i}. **{exercise.get('title', 'Exercise')}**")
                    lines.append(f"   {exercise.get('instructions', '')}")
                else:
                    lines.append(f"{i}. {exercise}")
            lines.append("")

        if data.get("prerequisites"):
            lines.append("## Prerequisites")
            for prereq in data["prerequisites"]:
                lines.append(f"- {prereq}")
            lines.append("")

        if data.get("next_steps"):
            lines.append("## Next Steps")
            for step in data["next_steps"]:
                lines.append(f"- {step}")

        return "\n".join(lines)

    def create_curriculum_from_resources(
        self,
        resources: List[LearningResource],
        instrument: str,
        curriculum_title: str,
    ) -> Dict[str, Any]:
        """
        Create a curriculum structure from fetched resources.

        Groups resources by difficulty and skill category.
        """
        from music_brain.learning.curriculum import (
            CurriculumBuilder,
            DifficultyLevel,
            SkillCategory,
        )

        # Group resources by difficulty
        by_difficulty: Dict[int, List[LearningResource]] = {}
        for resource in resources:
            diff = resource.difficulty_estimate
            if diff not in by_difficulty:
                by_difficulty[diff] = []
            by_difficulty[diff].append(resource)

        builder = CurriculumBuilder(instrument)

        # Create modules for each difficulty level
        for diff_level in sorted(by_difficulty.keys()):
            level_resources = by_difficulty[diff_level]
            difficulty = DifficultyLevel(min(max(diff_level, 1), 10))

            builder.start_module(
                module_id=f"{instrument}_level_{diff_level}",
                title=f"{difficulty.name_friendly} {instrument.title()}",
                description=f"Level {diff_level} content for {instrument}",
                difficulty_range=(diff_level, diff_level),
            )

            for resource in level_resources:
                builder.add_lesson(
                    lesson_id=resource.id,
                    title=resource.title,
                    description=resource.description,
                    difficulty=difficulty,
                    duration_minutes=resource.estimated_duration_minutes or 30,
                )

                # Add resource as external link
                builder.add_resource(
                    url=resource.url,
                    title=resource.title,
                    resource_type=resource.resource_type.name.lower(),
                )

            builder.finish_module()

        curriculum = builder.build(
            curriculum_id=f"{instrument}_curriculum",
            title=curriculum_title,
            description=f"AI-curated curriculum for learning {instrument}",
        )

        return curriculum.to_dict()


def get_recommended_sources(
    instrument: str,
    difficulty: int = 1,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """
    Get recommended learning sources for an instrument and difficulty level.

    Returns sources sorted by quality score.
    """
    fetcher = ResourceFetcher()
    sources = fetcher.get_sources_for_instrument(instrument)

    # Filter by difficulty range
    filtered = []
    for source in sources:
        min_d, max_d = source.get("difficulty_range", (1, 10))
        if min_d <= difficulty <= max_d:
            filtered.append(source)

    return filtered[:limit]


def generate_learning_plan(
    instrument: str,
    current_level: int = 1,
    target_level: int = 5,
    weekly_hours: float = 5.0,
) -> Dict[str, Any]:
    """
    Generate a learning plan based on available resources.

    Returns a structured plan with recommended sources and timeline.
    """
    fetcher = ResourceFetcher()
    plan = {
        "instrument": instrument,
        "current_level": current_level,
        "target_level": target_level,
        "weekly_hours": weekly_hours,
        "phases": [],
    }

    for level in range(current_level, target_level + 1):
        sources = fetcher.get_sources_for_instrument(instrument)
        level_sources = [
            s for s in sources
            if s.get("difficulty_range", (1, 10))[0] <= level <= s.get("difficulty_range", (1, 10))[1]
        ]

        phase = {
            "level": level,
            "level_name": DifficultyLevel(level).name_friendly if level <= 10 else "Expert",
            "focus_areas": [],
            "recommended_sources": level_sources[:3],
            "estimated_weeks": 4 + (level * 2),  # Rough estimate
        }

        # Add focus areas based on level
        if level <= 3:
            phase["focus_areas"] = ["technique", "rhythm", "basic_repertoire"]
        elif level <= 6:
            phase["focus_areas"] = ["scales", "theory", "intermediate_repertoire"]
        else:
            phase["focus_areas"] = ["improvisation", "advanced_technique", "performance"]

        plan["phases"].append(phase)

    return plan


# Import DifficultyLevel for generate_learning_plan
from music_brain.learning.curriculum import DifficultyLevel
