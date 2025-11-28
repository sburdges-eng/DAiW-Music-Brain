# DAiW-Music-Brain Development Roadmap

**Current Status:** Phase 1 at 92% → Target: 100%
**Last Updated:** 2025-11-28

---

## 🎯 Development Queue

### **Priority 1: Finish CLI Implementation** ⚡
**Goal:** Complete Phase 1 (92% → 100%)
**Estimated Time:** 2 hours
**Status:** In Progress

#### Files to Implement:
```
music_brain/cli/
├── commands.py          # CLI command implementations (NEW)
├── __init__.py          # CLI exports
└── cli.py               # Entry point (EXISTS - needs wrapper commands)

music_brain/harmony/
└── harmony_generator.py # (PARTIALLY EXISTS - in data/)

music_brain/groove/
└── groove_applicator.py # (EXISTS - in data/)

tests/
└── test_cli.py          # (NEW - comprehensive CLI tests)
```

#### Tasks:
- [x] Create `music_brain/cli/commands.py` - CLI command wrappers
- [ ] Move `data/harmony_generator.py` → `music_brain/harmony/harmony_generator.py`
- [ ] Move `data/groove_applicator.py` → `music_brain/groove/groove_applicator.py`
- [ ] Add CLI commands to `cli.py`:
  - [x] `daiw extract` (groove extraction) - basic exists
  - [x] `daiw apply` (groove application) - basic exists
  - [x] `daiw analyze` (chord analysis) - basic exists
  - [ ] `daiw generate` (harmony generation from intent)
  - [ ] `daiw diagnose` (chord progression diagnosis)
  - [ ] `daiw reharm` (reharmonization)
  - [ ] `daiw intent` subcommands (new, process, validate, suggest)
  - [ ] `daiw teach` (teaching mode)
- [ ] Create comprehensive test suite in `tests/test_cli.py`
- [ ] Update `__init__.py` exports

#### Acceptance Criteria:
- All CLI commands functional
- Test coverage ≥ 80%
- Examples run without errors
- Documentation updated

---

### **Priority 2: Expand MCP Tool Coverage** 🔧
**Goal:** Scale from 3 tools to 22+ MCP tools
**Estimated Time:** 1 week
**Status:** Planning

#### Current Status:
```
daiw_mcp/
├── server.py            # MCP server (3 tools registered)
├── tools/
│   ├── harmony.py       # ✅ Working (1 tool)
│   └── audio.py         # ✅ Working (2 tools)
└── tests/
    └── test_mcp_tools.py # Basic tests
```

#### Required Tools (22 total):

**Harmony Tools (6):**
- [x] `analyze_progression` - Analyze chord progression
- [ ] `generate_harmony` - Generate harmony from intent
- [ ] `diagnose_chords` - Diagnose harmonic issues
- [ ] `suggest_reharmonization` - Suggest chord substitutions
- [ ] `find_key` - Detect key from progression
- [ ] `voice_leading` - Optimize voice leading

**Groove Tools (5):**
- [x] `extract_groove` - Extract groove from MIDI
- [x] `apply_groove` - Apply groove template
- [ ] `analyze_pocket` - Analyze timing pocket
- [ ] `humanize_midi` - Add human feel
- [ ] `quantize_smart` - Smart quantization

**Intent Tools (4):**
- [ ] `create_intent` - Create song intent template
- [ ] `process_intent` - Process intent → music
- [ ] `validate_intent` - Validate intent schema
- [ ] `suggest_rulebreaks` - Suggest emotional rule-breaks

**Audio Analysis Tools (4):**
- [ ] `detect_bpm` - Detect tempo from audio
- [ ] `detect_key` - Detect key from audio
- [ ] `analyze_audio_feel` - Analyze groove feel from audio
- [ ] `extract_chords` - Extract chords from audio

**Teaching Tools (3):**
- [ ] `explain_rulebreak` - Explain rule-breaking technique
- [ ] `get_progression_info` - Get progression details
- [ ] `emotion_to_music` - Map emotion to musical parameters

#### Implementation Pattern:
```python
# tools/harmony.py example
@mcp_tool
async def analyze_progression(progression: str, key: str = None) -> dict:
    """
    Analyze a chord progression.

    Args:
        progression: Chord progression (e.g., "F-C-Dm-Bbm")
        key: Optional key context

    Returns:
        Analysis with emotional character, rule breaks, suggestions
    """
    from music_brain.structure.progression import diagnose_progression
    result = diagnose_progression(progression, key)
    return result.to_dict()
```

#### Tasks:
- [ ] Create `tools/intent.py` (4 tools)
- [ ] Create `tools/groove.py` (expand to 5 tools)
- [ ] Create `tools/audio_analysis.py` (4 tools)
- [ ] Create `tools/teaching.py` (3 tools)
- [ ] Update `server.py` to register all tools
- [ ] Add tests for each tool in `test_mcp_tools.py`
- [ ] Update MCP documentation

---

### **Priority 3: Audio Analysis Implementation** 🎵
**Goal:** Complete audio analysis module with librosa integration
**Estimated Time:** 1 week
**Status:** Starter Complete

#### Current Status:
```
music_brain/audio/
├── feel.py              # ✅ Audio feel analysis (EXISTS)
├── analyzer.py          # 🔄 Starter module (NEEDS EXPANSION)
├── chord_detection.py   # ❌ Not implemented
├── frequency.py         # ❌ Not implemented
└── __init__.py

tools/audio_cataloger/   # ✅ Separate tool (EXISTS)
└── audio_cataloger.py   # BPM/key detection with librosa
```

#### Required Modules:

**1. `analyzer.py` - Main audio analysis interface**
```python
class AudioAnalyzer:
    def analyze_file(self, filepath: str) -> AudioAnalysis
    def detect_bpm(self, audio_data: np.ndarray, sr: int) -> float
    def detect_key(self, audio_data: np.ndarray, sr: int) -> str
    def extract_features(self, audio_data: np.ndarray, sr: int) -> dict
```

**2. `chord_detection.py` - Chord detection from audio**
```python
class ChordDetector:
    def detect_chords(self, audio_data: np.ndarray, sr: int) -> List[Chord]
    def detect_progression(self, filepath: str) -> ChordProgression
    def confidence_score(self, detection: Chord) -> float
```

**3. `frequency.py` - Frequency analysis utilities**
```python
class FrequencyAnalyzer:
    def fft_analysis(self, audio_data: np.ndarray) -> np.ndarray
    def pitch_detection(self, audio_data: np.ndarray, sr: int) -> float
    def harmonic_content(self, audio_data: np.ndarray) -> dict
```

#### Integration Points:
- Integrate with existing `audio_cataloger.py` (already has BPM/key detection)
- Use librosa for DSP
- Connect to `structure/chord.py` for chord representation
- Feed into `session/intent_processor.py` for reverse-engineering intent

#### Tasks:
- [ ] Expand `analyzer.py` with full AudioAnalyzer class
- [ ] Implement `chord_detection.py` with ChordDetector
- [ ] Implement `frequency.py` with FrequencyAnalyzer
- [ ] Integrate audio_cataloger patterns
- [ ] Create comprehensive tests in `tests/test_audio.py`
- [ ] Add CLI command: `daiw analyze-audio <file>`
- [ ] Documentation with examples

#### Dependencies:
```
librosa>=0.10.0   # Audio analysis
soundfile>=0.12.0 # Audio I/O
numpy>=1.24.0     # Numerical operations
scipy>=1.10.0     # Signal processing
```

---

## 📊 Phase Completion Roadmap

### Phase 1: Core Systems (92% → 100%)
**Target:** Complete by end of this week

- [x] Groove extraction & application (DONE)
- [x] Chord analysis & diagnosis (DONE)
- [x] Intent schema & processor (DONE)
- [x] Emotional mapping (DONE)
- [x] Teaching module (DONE)
- [ ] CLI wrapper commands (IN PROGRESS - 8%)
- [ ] Test suite expansion (IN PROGRESS - 50%)

**Remaining:**
- CLI implementation: 2 hours
- Test coverage: 1 hour
- Integration testing: 30 minutes

### Phase 2: Expansion & Integration (0% → 50%)
**Target:** Complete by next month

- [ ] MCP tool coverage (3 → 22 tools)
- [ ] Audio analysis module
- [ ] Desktop app integration
- [ ] Streamlit UI enhancements
- [ ] API endpoint expansion

### Phase 3: Advanced Features (0%)
**Target:** Q1 2026

- [ ] Real-time MIDI processing
- [ ] DAW plugin integration
- [ ] Machine learning for intent classification
- [ ] Collaborative features
- [ ] Mobile app

---

## 🔧 Implementation Guidelines

### For CLI Commands:
```python
# music_brain/cli/commands.py

import click
from music_brain.harmony import harmony_generator
from music_brain.groove import groove_applicator

@click.command()
@click.argument('progression')
@click.option('--key', help='Key context')
def diagnose(progression, key):
    """Diagnose chord progression for harmonic issues."""
    from music_brain.structure.progression import diagnose_progression
    result = diagnose_progression(progression, key)
    click.echo(f"Progression: {result.progression}")
    click.echo(f"Emotional Character: {result.emotional_character}")
    # ... more output
```

### For MCP Tools:
```python
# daiw_mcp/tools/harmony.py

from mcp import Tool, tool

@tool
async def generate_harmony(
    emotion: str,
    key: str = "C",
    genre: str = "pop"
) -> dict:
    """Generate harmony from emotional intent."""
    from music_brain.session.intent_processor import process_intent
    # Implementation
    return result
```

### For Audio Analysis:
```python
# music_brain/audio/analyzer.py

import librosa
import numpy as np

class AudioAnalyzer:
    def detect_bpm(self, filepath: str) -> float:
        """Detect BPM using librosa onset detection."""
        y, sr = librosa.load(filepath, mono=True, duration=60)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo = librosa.feature.tempo(onset_envelope=onset_env, sr=sr)
        return float(tempo[0])
```

---

## 🧪 Testing Strategy

### CLI Tests:
```python
# tests/test_cli.py

def test_diagnose_command():
    """Test daiw diagnose command."""
    result = runner.invoke(cli, ['diagnose', 'F-C-Dm-Bbm', '--key', 'F major'])
    assert result.exit_code == 0
    assert 'Modal Interchange' in result.output
```

### MCP Tool Tests:
```python
# tests/test_mcp_tools.py

async def test_analyze_progression_tool():
    """Test MCP analyze_progression tool."""
    result = await tools.analyze_progression("F-C-Dm-Bbm", "F major")
    assert result['emotional_character'] == 'complex, emotionally ambiguous'
    assert 'HARMONY_ModalInterchange' in result['rule_breaks']
```

### Audio Tests:
```python
# tests/test_audio.py

def test_bpm_detection():
    """Test BPM detection accuracy."""
    analyzer = AudioAnalyzer()
    bpm = analyzer.detect_bpm('tests/fixtures/120bpm.wav')
    assert 118 <= bpm <= 122  # Allow ±2 BPM tolerance
```

---

## 📝 Documentation Requirements

For each completed feature:
- [ ] Docstrings (Google style)
- [ ] Usage examples
- [ ] CLI help text
- [ ] API documentation
- [ ] Tutorial in vault/
- [ ] Update CLAUDE.md

---

## 🎯 Success Metrics

### Phase 1 Complete:
- All CLI commands functional ✓
- Test coverage ≥ 80% ✓
- No critical bugs ✓
- Documentation complete ✓

### Phase 2 Complete:
- 22+ MCP tools working ✓
- Audio analysis accurate (±2 BPM, ±1 semitone key) ✓
- Integration tests passing ✓

---

## 🚀 Quick Start for Development

### Setup Development Environment:
```bash
cd ~/Desktop/DAiW-Music-Brain

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev,audio,all]"

# Run tests
pytest tests/ -v

# Run CLI
daiw --help
```

### Enable GitHub Copilot:
1. Open VS Code in DAiW-Music-Brain folder
2. Cmd/Ctrl+Shift+P → "Copilot: Enable Copilot Spaces"
3. Select workspace: DAiW-Music-Brain
4. Copilot will read `.github/copilot-instructions.md`

### Start Coding:
```bash
# Priority 1: CLI Implementation
code music_brain/cli/commands.py

# Priority 2: MCP Tools
code daiw_mcp/tools/intent.py

# Priority 3: Audio Analysis
code music_brain/audio/analyzer.py
```

---

## 📚 Resources

- **Main Documentation:** `docs/CLAUDE.md`
- **Copilot Instructions:** `.github/copilot-instructions.md`
- **Emotional Mapping:** `data/emotional_mapping.py`
- **Groove Guide:** `docs/GROOVE_MODULE_GUIDE.md`
- **Kelly Song Example:** `vault/Songs/when-i-found-you-sleeping/`
- **Start Here:** `docs/START_HERE.txt`

---

*Last Updated: 2025-11-28*
*Phase 1 Status: 92% → Target 100% by end of week*
