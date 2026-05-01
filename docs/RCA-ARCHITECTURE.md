# RCA Output — Architecture & Design Decisions

## Problem Statement

The TRNTBL main board outputs a **very weak analog signal** from the motor control circuitry. The original design (VNYL era) was WiFi-only, so this signal was ignored. With the openTRNTBL firmware, we revived it as a **bonus local RCA output** for users who want direct analog playback without network dependency.

## Signal Chain Decision: NE5532 → PAM8403 → RCA

### Why NE5532 BEFORE PAM8403 (not after, not skipped)

**Architecture:**
```
TRNTBL motor signal (weak, ~50mV, noisy)
  ↓
NE5532 preampli (low-noise gain stage, volume potentiometer)
  ↓
PAM8403 power amplifier (boosts to speaker level, ~2W @ 8Ω)
  ↓
RCA output connectors
```

**Why this order:**
- PAM8403 is a **power amplifier**, not a preamp
  - It expects a "hot" input signal (~500mV+)
  - If you feed it the weak TRNTBL signal directly, it amplifies noise + signal equally
  - Result: extremely high noise floor, barely usable
  
- NE5532 is an **op-amp preamp** with:
  - Low input impedance (can handle weak signals cleanly)
  - Programmable gain via resistor network
  - **Volume potentiometer** for user control
  - Amplifies signal cleanly *before* sending to PAM
  
- **Why pot on NE5532, not PAM:**
  - Potentiometer at the input (before gain stage) = clean, low-noise control
  - If pot is at minimum → zero signal leaves NE5532 → zero enters PAM
  - PAM stays powered but silent (no parasitic noise bleed)

### What We Considered (and Rejected)

**Option: PAM8403 only (no NE5532)**
- ❌ Amplifies weak signal + all noise together
- ❌ No practical volume control without PWM (adds complexity)
- ❌ Noise floor unacceptable for audio playback

**Option: GPIO-controlled PAM power kill**
- ❌ Would require power management circuitry
- ❌ Overkill for a bonus feature
- ❌ Boot timing becomes critical

## Software Control: `rca_enabled` vs `rca_show_ui`

### `rca_enabled` (config.json)
**What:** Hardware presence flag
- `false` = PAM8403 not installed, section never visible in UI
- `true` = PAM8403 installed and ready to use

**Set at:** Deployment time (deploy.sh)
**User can't change:** No (requires reflash)

### `rca_show_ui` (Settings toggle)
**What:** UI visibility flag for users who have hardware but don't want to see it
- `true` = show RCA section (if `rca_enabled: true`)
- `false` = hide RCA section (even if hardware present)

**Set at:** Runtime (Settings page toggle)
**User can change:** Yes

### Logic in UI

```javascript
if (!rca_enabled) {
  // Hardware not installed → never show
  return;
}

if (!rca_show_ui) {
  // Hardware present but user hides it
  return;
}

// Show RCA section
```

## UX Decision: Two Separate Sections (not unified mode toggle)

### Option A: Keep RCA + Sonos sections visible always
- ✅ Transparent: user sees all available outputs
- ✅ No extra clicks required
- ✅ WiFi is primary function, RCA is bonus → showing both is honest
- ✅ Zero UI complexity
- ❌ Slightly "noisy" visually (but acceptable)

### Option B: Add mode switch "WiFi / RCA" at top
- ✅ Cleaner visual separation
- ✅ Only relevant section shows at a time
- ❌ Extra layer of indirection
- ❌ Switching modes = extra clicks (not natural)
- ❌ WiFi is 99% of use case, RCA is one-time setup

**Decision: Option A** (keep sections separate, visible always)
- Rationale: RCA is architectural debt recovery (TRNTBL was poorly designed), not a primary feature
- Users should see what's available without hidden modes
- Adding mode toggle would suggest RCA is first-class, when it's really a fallback

## Boot Behavior

At `start-trntbl.sh` boot time:
1. Check `config.json` for `rca_enabled`
2. If `true`: launch `alsaloop` to feed signal into audio chain
3. If `false`: skip RCA initialization entirely

NE5532 potentiometer: set to **minimum at boot** (via amixer DAC controls, or left at hardware default if pot is manual).

User adjusts NE5532 pot manually based on use case.

## Hardware Soldering Points

- **Source:** TRNTBL main board audio output pads (visible on board bottom, left side)
- **Destination:** NE5532 input (Hallege board, or custom)
- **Cable:** Shielded audio cable, ~10cm, 3.5mm jack to PCB pads

## Testing & Validation

See `docs/TEST-PLAN.md` sections 7 (Output Mode Switch) and 8 (Bitrate Selection).

## Future: GPIO Control of NE5532 Potentiometer

**Not implemented in V1** (overkill for beta). If needed later:
- Use CHIP GPIO pin to control analog pot via digital potentiometer IC (e.g., MCP4017)
- Allows software-controlled volume on RCA
- Trade-off: adds BOM cost + soldering complexity
- Revisit if users report need for remote RCA volume control

## Why This Approach Is "Clean"

1. **Hardware responsibility:** NE5532 pot handles all RCA signal gating
   - Minimum pot = zero signal, zero noise
   - No software-only "muting" of analog signal

2. **Software responsibility:** Control whether alsaloop runs
   - `rca_enabled` toggle in Settings on/off
   - Toggle ON/OFF controls CPU load and signal flow

3. **Separation of concerns:** Software controls source (CPU), hardware controls level (pot)
   - Either can fail independently
   - Both must be "on" for audio to play (redundancy)

4. **User mental model:** Clear two-step setup
   - Install hardware + configure in settings
   - Adjust pot to desired level
   - Done
