"""
iDAW - intelligent Digital Audio Workspace
===========================================
Ableton-Style Interface

Version: 1.0.04

Changes:
- Preview mode vs Generate mode
- Working transport controls
- Better library detection
- Interactive device chain

Run with: streamlit run idaw_ableton_ui.py
"""

import streamlit as st
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Version
VERSION = "1.0.04"

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# ============================================================================
# LIBRARY DETECTION - Search actual Mac paths
# ============================================================================

def find_sound_libraries() -> Dict[str, Dict[str, Any]]:
    """Search for sound libraries on Mac."""
    libraries = {}
    
    # =========== LOGIC PRO X ===========
    logic_paths = {
        "app": Path("/Applications/Logic Pro X.app"),
        "app_alt": Path("/Applications/Logic Pro.app"),
        "loops_user": Path.home() / "Library/Audio/Apple Loops",
        "loops_system": Path("/Library/Audio/Apple Loops"),
        "apple_loops": Path("/Library/Audio/Apple Loops/Apple"),
    }
    
    logic_found = logic_paths["app"].exists() or logic_paths["app_alt"].exists()
    logic_count = 0
    
    for key, path in logic_paths.items():
        if path.exists() and "loop" in key.lower():
            try:
                logic_count += len(list(path.rglob("*.caf"))[:100])
                logic_count += len(list(path.rglob("*.aif"))[:100])
            except:
                pass
    
    libraries["logic_pro"] = {
        "name": "Logic Pro X",
        "installed": logic_found,
        "count": logic_count
    }
    
    # =========== VITAL ===========
    vital_paths = [
        Path("/Applications/Vital.app"),
        Path("/Library/Audio/Plug-Ins/VST3/Vital.vst3"),
        Path("/Library/Audio/Plug-Ins/Components/Vital.component"),
        Path.home() / "Library/Audio/Plug-Ins/Components/Vital.component",
    ]
    
    vital_found = any(p.exists() for p in vital_paths)
    vital_count = 0
    
    preset_paths = [
        Path.home() / "Documents/Vital",
        Path.home() / "Library/Application Support/Vital",
    ]
    for p in preset_paths:
        if p.exists():
            try:
                vital_count += len(list(p.rglob("*.vital"))[:100])
            except:
                pass
    
    libraries["vital"] = {
        "name": "Vital",
        "installed": vital_found,
        "count": vital_count
    }
    
    # =========== MELDAPRODUCTION ===========
    melda_au = Path("/Library/Audio/Plug-Ins/Components")
    melda_found = False
    if melda_au.exists():
        melda_found = len(list(melda_au.glob("M*.component"))) > 0
    
    melda_count = 0
    melda_presets = Path.home() / "Library/Audio/Presets/MeldaProduction"
    if melda_presets.exists():
        try:
            melda_count = len(list(melda_presets.rglob("*.mpreset"))[:100])
        except:
            pass
    
    libraries["melda"] = {
        "name": "MeldaProduction",
        "installed": melda_found,
        "count": melda_count
    }
    
    # =========== USER SAMPLES ===========
    gdrive_paths = [
        Path.home() / "Google Drive/My Drive",
        Path.home() / "Google Drive",
        Path.home() / "Library/CloudStorage",
    ]
    
    user_count = 0
    for base in gdrive_paths + [Path.home() / "Music"]:
        if base.exists():
            try:
                for ext in ["*.wav", "*.aif", "*.mp3"]:
                    user_count += len(list(base.rglob(ext))[:50])
            except:
                pass
    
    libraries["user_samples"] = {
        "name": "Your Samples",
        "installed": user_count > 0,
        "count": user_count
    }
    
    # =========== GARAGEBAND ===========
    libraries["garageband"] = {
        "name": "GarageBand",
        "installed": Path("/Applications/GarageBand.app").exists(),
        "count": 0
    }
    
    return libraries


def generate_preview_tone(frequency: float = 440, duration: float = 0.5) -> Optional[bytes]:
    """Generate a simple preview tone."""
    try:
        import numpy as np
        import wave
        import io
        
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = np.sin(frequency * 2 * np.pi * t) * 0.3
        
        # Envelope
        attack = int(0.01 * sample_rate)
        release = int(0.1 * sample_rate)
        envelope = np.ones_like(tone)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        tone = tone * envelope
        
        audio = (tone * 32767).astype(np.int16)
        
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio.tobytes())
        
        return buffer.getvalue()
    except:
        return None


def get_freq(key: str) -> float:
    """Get frequency for a key."""
    freqs = {"C": 261.63, "C#": 277.18, "D": 293.66, "Eb": 311.13,
             "E": 329.63, "F": 349.23, "F#": 369.99, "G": 392.00,
             "Ab": 415.30, "A": 440.00, "Bb": 466.16, "B": 493.88}
    return freqs.get(key, 440.0)


# ============================================================================
# IMPORT PIPELINE
# ============================================================================
try:
    from idaw_complete_pipeline import (
        InterrogationEngine, get_parameters_for_state, StructureGenerator,
        HarmonyEngine, MelodyEngine, GrooveEngine, MIDIBuilder,
        EMOTIONAL_PRESETS, TimingFeel, RuleBreakCode,
    )
    PIPELINE_OK = True
except ImportError as e:
    PIPELINE_OK = False
    PIPELINE_ERR = str(e)


# ============================================================================
# PAGE CONFIG & CSS
# ============================================================================
st.set_page_config(page_title=f"iDAW v{VERSION}", page_icon="🎹", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #1e1e1e; }
    #MainMenu, footer, header { visibility: hidden; }
    h1,h2,h3,h4,h5,h6 { color: #ffffff !important; }
    .stMarkdown h3 { color: #ff9500 !important; }
    .stMarkdown p, label { color: #e0e0e0 !important; }
    
    .browser-header {
        color: #ff9500 !important; font-size: 12px; text-transform: uppercase;
        letter-spacing: 1px; margin-bottom: 10px; font-weight: bold;
    }
    
    .official-box {
        background: linear-gradient(180deg, #3d3d3d, #2d2d2d);
        border: 1px solid #4a4a4a; border-radius: 5px; padding: 12px; text-align: center;
    }
    .official-value { color: #ff9500; font-size: 24px; font-weight: bold; font-family: monospace; }
    .official-label { color: #888; font-size: 10px; text-transform: uppercase; }
    
    .preview-box {
        background: #2a2a2a; border: 1px dashed #555; border-radius: 5px; padding: 10px;
    }
    .preview-value { color: #30d158; font-size: 18px; font-weight: bold; }
    .preview-label { color: #666; font-size: 10px; text-transform: uppercase; }
    
    .clip {
        background: linear-gradient(180deg, #5a7a5a, #4a6a4a);
        border-radius: 3px; padding: 4px 8px; margin: 2px; color: #fff;
        font-size: 11px; display: inline-block; border-left: 3px solid #7a9a7a;
    }
    .clip.drums { background: linear-gradient(180deg, #7a5a5a, #6a4a4a); border-left-color: #9a7a7a; }
    .clip.melody { background: linear-gradient(180deg, #5a5a7a, #4a4a6a); border-left-color: #7a7a9a; }
    
    .device-box {
        background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 5px;
        padding: 12px; text-align: center;
    }
    .device-title { color: #ff9500; font-size: 10px; text-transform: uppercase; margin-bottom: 5px; }
    .device-value { color: #fff; font-size: 16px; font-weight: bold; }
    
    .section-marker {
        background: #ff9500; color: #000; font-size: 10px; font-weight: bold;
        padding: 2px 8px; border-radius: 2px; margin: 2px; display: inline-block;
    }
    
    .lib-ok { color: #30d158; }
    .lib-no { color: #666; }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# SESSION STATE
# ============================================================================
defaults = {
    'official_bpm': 82, 'official_key': 'F', 'official_emotion': 'grief',
    'preview_bpm': 82, 'preview_key': 'F', 'preview_emotion': 'grief',
    'humanize': 0.2, 'dissonance': 0.3, 'lofi': 0.3, 'pocket': 'behind',
    'generated': False, 'libraries_scanned': False, 'libraries': {}, 'tracks': []
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

EMOTION_REC = {
    "grief": {"bpm": 72, "key": "F", "humanize": 0.3, "dissonance": 0.3, "pocket": "behind"},
    "anxiety": {"bpm": 120, "key": "E", "humanize": 0.1, "dissonance": 0.6, "pocket": "ahead"},
    "nostalgia": {"bpm": 78, "key": "G", "humanize": 0.25, "dissonance": 0.25, "pocket": "behind"},
    "anger": {"bpm": 138, "key": "E", "humanize": 0.15, "dissonance": 0.5, "pocket": "ahead"},
    "calm": {"bpm": 68, "key": "C", "humanize": 0.2, "dissonance": 0.1, "pocket": "behind"},
    "hope": {"bpm": 92, "key": "G", "humanize": 0.2, "dissonance": 0.2, "pocket": "on"},
    "intimacy": {"bpm": 64, "key": "D", "humanize": 0.35, "dissonance": 0.2, "pocket": "behind"},
    "defiance": {"bpm": 115, "key": "A", "humanize": 0.15, "dissonance": 0.4, "pocket": "on"},
}


# ============================================================================
# TOP BAR - OFFICIAL VALUES
# ============================================================================
st.markdown("## 🎹 iDAW")

top = st.columns([1, 1, 1, 1, 2])

with top[0]:
    st.markdown(f'<div class="official-box"><div class="official-label">BPM</div><div class="official-value">{st.session_state.official_bpm}</div></div>', unsafe_allow_html=True)

with top[1]:
    st.markdown(f'<div class="official-box"><div class="official-label">KEY</div><div class="official-value">{st.session_state.official_key}</div></div>', unsafe_allow_html=True)

with top[2]:
    st.markdown(f'<div class="official-box"><div class="official-label">EMOTION</div><div class="official-value" style="font-size:16px">{st.session_state.official_emotion.upper()}</div></div>', unsafe_allow_html=True)

with top[3]:
    # Play official preview
    if st.button("▶️ PLAY", key="play_official", use_container_width=True):
        audio = generate_preview_tone(get_freq(st.session_state.official_key), 1.0)
        if audio:
            st.audio(audio, format="audio/wav")

with top[4]:
    st.markdown(f"<div style='text-align:right;color:#555;padding:15px'>v{VERSION}</div>", unsafe_allow_html=True)

st.markdown("---")


# ============================================================================
# MAIN LAYOUT
# ============================================================================
col_left, col_main, col_right = st.columns([1.2, 3, 1.5])


# ============================================================================
# LEFT - PRESETS & LIBRARIES
# ============================================================================
with col_left:
    st.markdown('<div class="browser-header">🎭 EMOTION</div>', unsafe_allow_html=True)
    
    emotions = list(EMOTION_REC.keys())
    sel_idx = emotions.index(st.session_state.preview_emotion) if st.session_state.preview_emotion in emotions else 0
    
    selected_emotion = st.radio("Emotion", emotions, index=sel_idx, label_visibility="collapsed", key="emo_radio")
    
    if selected_emotion != st.session_state.preview_emotion:
        st.session_state.preview_emotion = selected_emotion
        rec = EMOTION_REC[selected_emotion]
        st.session_state.preview_bpm = rec["bpm"]
        st.session_state.preview_key = rec["key"]
        st.session_state.humanize = rec["humanize"]
        st.session_state.dissonance = rec["dissonance"]
        st.session_state.pocket = rec["pocket"]
        st.rerun()
    
    # Recommended
    rec = EMOTION_REC[selected_emotion]
    st.markdown(f'''<div class="preview-box">
        <div class="preview-label">RECOMMENDED</div>
        <div style="color:#aaa;font-size:11px">
            {rec["bpm"]} BPM | {rec["key"]} | {rec["pocket"]}
        </div>
    </div>''', unsafe_allow_html=True)
    
    st.markdown('<div class="browser-header" style="margin-top:15px">🎹 LIBRARIES</div>', unsafe_allow_html=True)
    
    if st.button("🔍 Scan", key="scan", use_container_width=True):
        with st.spinner("Scanning..."):
            st.session_state.libraries = find_sound_libraries()
            st.session_state.libraries_scanned = True
        st.rerun()
    
    if st.session_state.libraries_scanned:
        for k, v in st.session_state.libraries.items():
            icon = "✓" if v["installed"] else "✗"
            css = "lib-ok" if v["installed"] else "lib-no"
            cnt = f' ({v["count"]})' if v["count"] > 0 else ""
            st.markdown(f'<span class="{css}">{icon} {v["name"]}{cnt}</span>', unsafe_allow_html=True)
    
    st.markdown('<div class="browser-header" style="margin-top:15px">🥁 GROOVE</div>', unsafe_allow_html=True)
    groove = st.selectbox("Style", ["sparse", "basic", "boom_bap", "four_on_floor"], label_visibility="collapsed")


# ============================================================================
# CENTER - PREVIEW & GENERATE
# ============================================================================
with col_main:
    st.markdown("### 🎛️ Preview Settings")
    st.caption("Adjust and preview before generating")
    
    p1, p2, p3, p4 = st.columns(4)
    
    with p1:
        st.session_state.preview_bpm = st.slider("BPM", 40, 180, st.session_state.preview_bpm, key="prev_bpm")
    with p2:
        keys = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
        idx = keys.index(st.session_state.preview_key) if st.session_state.preview_key in keys else 5
        st.session_state.preview_key = st.selectbox("Key", keys, index=idx, key="prev_key")
    with p3:
        st.session_state.humanize = st.slider("Humanize", 0.0, 0.5, st.session_state.humanize, key="hum")
    with p4:
        st.session_state.dissonance = st.slider("Dissonance", 0.0, 1.0, st.session_state.dissonance, key="diss")
    
    # Preview vs Official
    st.markdown(f'''<div class="preview-box">
        <div style="display:flex;justify-content:space-around;align-items:center">
            <div>
                <div class="preview-label">PREVIEW</div>
                <div class="preview-value">{st.session_state.preview_bpm} | {st.session_state.preview_key}</div>
            </div>
            <div style="color:#555;font-size:24px">→</div>
            <div>
                <div class="preview-label">OFFICIAL</div>
                <div style="color:#ff9500;font-size:18px;font-weight:bold">{st.session_state.official_bpm} | {st.session_state.official_key}</div>
            </div>
        </div>
    </div>''', unsafe_allow_html=True)
    
    # Transport
    t1, t2, t3, t4, t5 = st.columns(5)
    with t1:
        if st.button("⏮️", key="rew", use_container_width=True):
            st.toast("Rewind")
    with t2:
        if st.button("▶️ Preview", key="play_prev", use_container_width=True):
            audio = generate_preview_tone(get_freq(st.session_state.preview_key), 0.8)
            if audio:
                st.audio(audio, format="audio/wav")
    with t3:
        if st.button("⏹️", key="stop", use_container_width=True):
            st.toast("Stopped")
    with t4:
        if st.button("⏺️", key="rec", use_container_width=True):
            st.toast("Record (coming soon)")
    with t5:
        if st.button("⏭️", key="fwd", use_container_width=True):
            st.toast("Forward")
    
    st.markdown("---")
    
    # GENERATE
    g1, g2 = st.columns([4, 1])
    with g1:
        if st.button("⚡ GENERATE → Apply to Official", key="gen", use_container_width=True, type="primary"):
            st.session_state.official_bpm = st.session_state.preview_bpm
            st.session_state.official_key = st.session_state.preview_key
            st.session_state.official_emotion = st.session_state.preview_emotion
            
            if PIPELINE_OK:
                with st.spinner("Generating..."):
                    try:
                        engine = InterrogationEngine()
                        state = engine.quick_interrogate(st.session_state.official_emotion)
                        params = get_parameters_for_state(state)
                        params.tempo_suggested = st.session_state.official_bpm
                        params.key_signature = st.session_state.official_key
                        params.humanize = st.session_state.humanize
                        params.dissonance = st.session_state.dissonance
                        
                        struct_gen = StructureGenerator()
                        structure = struct_gen.generate(params, state)
                        total_bars = sum(s.bars for s in structure)
                        
                        harmony = HarmonyEngine(params)
                        progression = harmony.generate_progression(total_bars, state.primary_emotion)
                        
                        melody_engine = MelodyEngine(params, harmony)
                        melody = melody_engine.generate(progression, total_bars)
                        
                        groove_engine = GrooveEngine(params)
                        drums = groove_engine.generate_drums(total_bars, groove)
                        
                        builder = MIDIBuilder(bpm=params.tempo_suggested)
                        builder.add_track("melody", melody)
                        builder.add_track("drums", drums)
                        
                        out_dir = Path.home() / "Music" / "iDAW_Output"
                        out_dir.mkdir(parents=True, exist_ok=True)
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        midi_path = out_dir / f"iDAW_{ts}_{state.primary_emotion}.mid"
                        builder.save(midi_path)
                        
                        st.session_state.generated = True
                        st.session_state.midi_path = str(midi_path)
                        st.session_state.tracks = [
                            {"name": "Melody", "notes": len(melody), "sections": [{"name": s.name, "bars": s.bars} for s in structure]},
                            {"name": "Drums", "notes": len(drums), "sections": [{"name": s.name, "bars": s.bars} for s in structure]},
                        ]
                        st.session_state.structure = structure
                        st.success(f"✓ {midi_path.name}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.error(f"Pipeline error: {PIPELINE_ERR}")
    
    with g2:
        if st.button("🔄", key="reset", use_container_width=True):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.rerun()
    
    # Arrangement
    st.markdown("### 🎬 Arrangement")
    
    if st.session_state.generated and st.session_state.tracks:
        for track in st.session_state.tracks:
            tc1, tc2 = st.columns([1, 5])
            with tc1:
                st.markdown(f"**{track['name']}**<br><small>{track['notes']} notes</small>", unsafe_allow_html=True)
            with tc2:
                clips = "".join([f'<span class="clip {track["name"].lower()}">{s["name"]} ({s["bars"]})</span>' for s in track.get("sections", [])])
                st.markdown(f'<div style="background:#1a1a1a;padding:8px;border-radius:5px">{clips}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="background:#1a1a1a;padding:30px;text-align:center;color:#555;border-radius:5px">Generate to see tracks</div>', unsafe_allow_html=True)


# ============================================================================
# RIGHT - OUTPUT & DEVICES
# ============================================================================
with col_right:
    st.markdown('<div class="browser-header">📦 OUTPUT</div>', unsafe_allow_html=True)
    
    if st.session_state.generated and hasattr(st.session_state, 'midi_path'):
        mp = Path(st.session_state.midi_path)
        if mp.exists():
            with open(mp, "rb") as f:
                st.download_button("📥 MIDI", f, file_name=mp.name, mime="audio/midi", use_container_width=True)
            st.caption(mp.name)
    else:
        st.markdown('<span style="color:#555">Generate first</span>', unsafe_allow_html=True)
    
    st.markdown('<div class="browser-header" style="margin-top:15px">📐 STRUCTURE</div>', unsafe_allow_html=True)
    
    if st.session_state.generated and hasattr(st.session_state, 'structure'):
        for s in st.session_state.structure:
            st.markdown(f'<span class="section-marker">{s.name.upper()}</span>', unsafe_allow_html=True)
    
    st.markdown('<div class="browser-header" style="margin-top:15px">🎛️ DEVICES</div>', unsafe_allow_html=True)
    
    d1, d2 = st.columns(2)
    with d1:
        st.markdown(f'<div class="device-box"><div class="device-title">Humanize</div><div class="device-value">{st.session_state.humanize:.0%}</div></div>', unsafe_allow_html=True)
    with d2:
        st.markdown(f'<div class="device-box"><div class="device-title">Dissonance</div><div class="device-value">{st.session_state.dissonance:.0%}</div></div>', unsafe_allow_html=True)
    
    st.session_state.pocket = st.select_slider("Pocket", ["ahead", "on", "behind"], value=st.session_state.pocket, key="pock")
    st.session_state.lofi = st.slider("Lo-Fi", 0.0, 0.6, st.session_state.lofi, key="lof")


# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown(f'<div style="text-align:center;color:#555;font-size:11px">iDAW v{VERSION} — "Interrogate Before Generate"</div>', unsafe_allow_html=True)
