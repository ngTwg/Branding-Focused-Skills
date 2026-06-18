---
trigger: always_on
description: "User Preferences (Semantic Memory)"
---
# User Preferences (Semantic Memory)

## Coding & Development Style
- **Firmware/Hardware**: Prefers writing firmware/code from scratch over relying entirely on closed libraries (hands-on approach, core understanding).
- **Architecture**: Prefers extremely clean code organization with clear layering (Micro-kernel architecture, Lazy load, Tier-based routing). Does not accept messy code.

## AI Interaction Style
- Requires precise execution, absolute compliance with established rules and blueprints.
- **Evidence-based**: Dislikes guessing (No guessing). Every bug-fix decision must be based on evidence (Runtime > Tests > Source Code).
- **Anti-Sycophancy**: Accepts and expects the agent to proactively flag `[CONCERN]` if user makes a technical/architectural mistake.
- **Guardrails**: Always requires confirmation prompt before destructive actions or memory overwrites (False Memory Guard).

