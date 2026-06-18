---
trigger: model_decision
description: "LAYER 4: LESSONS LEARNED (KNOWN FAILURES)"
---
# LAYER 4: LESSONS LEARNED (KNOWN FAILURES)

*Storage for major bugs, architectural errors, or recurring failures. Serves as a Regression Database to prevent Agent from repeating past mistakes. (Updated via Rule 19).*

## Lesson History

*(AI will automatically propose additions here after Failure Postmortem phases - Rule 17)*

**Issue ID: #001**
- **Symptoms:** Git commits pushed to GitHub displayed the author/contributor as host system default `lengo` / `lengolee` instead of the correct user account `ngTwg`.
- **Root Cause:** AI failed to explicitly set Git identity variables (`user.name` and `user.email`) in PowerShell before running `git commit`, falling back to host system config.
- **Prevention:** Always run `git config user.name "ngTwg"` and `git config user.email "taikhoanpubg200@gmail.com"` locally in the workspace before any git commit and push actions. Verify Git configuration state to prevent developer identity leaks.

