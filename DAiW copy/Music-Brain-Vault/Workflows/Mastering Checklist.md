# Mastering Checklist

## Pre-Mastering Requirements

### From the Mix
- [ ] Mix bounce at 24-bit or higher
- [ ] Same sample rate as session
- [ ] Peak headroom: -3 to -6 dB
- [ ] No limiting on mix bus
- [ ] No clipping
- [ ] All automation printed

---

## Mastering Signal Chain (Typical Order)

```
1. Gain/Trim
2. Corrective EQ (cuts)
3. Compression (gentle)
4. Tonal EQ (character)
5. Stereo Enhancement (if needed)
6. Saturation (optional)
7. Limiter
8. Dither (on export)
```

---

## Logic Pro Mastering Assistant

Logic Pro includes a built-in Mastering Assistant:
1. Create stereo audio track
2. Import your mix
3. Add Mastering Assistant plugin
4. Choose style/reference
5. Adjust to taste

*Good starting point, then refine manually*

---

## Manual Mastering Process

### 1. Listen First
- [ ] Full listen without touching anything
- [ ] Note issues: balance, dynamics, frequency problems
- [ ] Compare to reference tracks

### 2. Corrective EQ
- [ ] Fix any frequency issues from mix
- [ ] Gentle moves (0.5-2 dB max)
- [ ] High-pass if needed (usually not)

### 3. Compression
- [ ] Glue compression: 1.5:1 to 2:1
- [ ] Slow attack (30ms+)
- [ ] Auto or medium release
- [ ] 1-3 dB gain reduction max

### 4. Tonal EQ
- [ ] Add air if needed (shelf at 10kHz+)
- [ ] Add warmth if needed (shelf at 100Hz)
- [ ] Broad, gentle moves

### 5. Limiting
- [ ] Target loudness (see below)
- [ ] True peak ceiling: -1.0 dB (streaming) or -0.3 dB (CD)
- [ ] Avoid pumping/distortion

---

## Target Loudness

| Platform | Target LUFS | True Peak |
|----------|-------------|-----------|
| Spotify | -14 LUFS | -1.0 dB |
| Apple Music | -16 LUFS | -1.0 dB |
| YouTube | -14 LUFS | -1.0 dB |
| CD | -9 to -12 LUFS | -0.3 dB |
| Club/DJ | -6 to -9 LUFS | -0.3 dB |

*Recommended: Master to -14 LUFS for streaming*

---

## Quality Checks

- [ ] A/B with reference at matched loudness
- [ ] Check in mono
- [ ] Check on multiple systems
- [ ] Check at low volume
- [ ] Check for clipping/distortion
- [ ] Verify LUFS target

---

## Export Settings

### Streaming/Digital
- Format: WAV or AIFF
- Bit Depth: 24-bit (or 16-bit with dither)
- Sample Rate: 44.1 kHz
- True Peak Ceiling: -1.0 dB
- Dither: POW-r #2 or similar

### CD
- Format: WAV or AIFF
- Bit Depth: 16-bit (with dither)
- Sample Rate: 44.1 kHz
- True Peak Ceiling: -0.3 dB

---

## Metadata

- [ ] Track title
- [ ] Artist name
- [ ] Album name
- [ ] Year
- [ ] Genre
- [ ] ISRC code (if distributing)

---

## Related
- [[Mixing Workflow Checklist]]
- [[Theory/Audio Recording Vocabulary]]

