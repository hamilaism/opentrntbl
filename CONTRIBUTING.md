# Contributing to openTRNTBL

## The project

openTRNTBL revives TRNTBL by VNYL turntables after the shutdown of the VNYL servers.
The goal is to provide a complete open-source firmware so anyone can bring their
turntable back to life.

## How to contribute

### You have a TRNTBL?

1. Flash the CHIP by following `docs/FLASH-GUIDE.md`
2. Install openTRNTBL with `docs/INSTALL-GUIDE.md`
3. Test it and open issues for bugs

### You want to improve the code?

1. Fork the repo
2. Create a branch (`git checkout -b fix/my-fix`)
3. Test on a real CHIP (no simulator available)
4. Open a PR

### Conventions

- Python 2.7 (Jessie constraint)
- Bash scripts compatible with sh/bash
- No npm/pip dependencies — everything via apt
- Vanilla HTML/CSS/JS — no framework, no build step
- CSS variables for theming

### Structure

```
firmware/   → What runs on the CHIP
docs/       → Documentation
design/     → Tokens, components, Storybook
```

## Help wanted on

- [ ] Support for other speakers (non-Sonos, via UPnP/DLNA)
- [ ] Bluetooth A2DP source
- [ ] Improved interface (design v2)
- [ ] Tests on other TRNTBL variants
- [ ] Hardware documentation (photos, schematics)
