---
name: No deploy to runtime without explicit OK
description: For projects with a stateful runtime (hardware, prod servers, mid-test envs) — never push code or restart services without explicit user confirmation
type: feedback
---

Never write to the CHIP runtime, restart Flask, push to a deployed service, or run a destructive command on shared/stateful infra without an **explicit confirmation in the current conversation** ("OK go", "deploy", "yes restart").

**Why:** the CHIP runtime can be in the middle of a stability test, a long-running scan, or a 72h soak. Restarting Flask resets logs and breaks the test. Pushing untested firmware can brick the boot sequence. The cost of pausing to confirm is 10 seconds ; the cost of nuking a 24h test is hours of re-running it.

**How to apply:** when the next action would touch a service that's currently serving requests, holding state in `/tmp`, or running a multi-hour test : describe what you're about to do, list the side-effects, and ask explicitly. Don't assume that "user said earlier we'd fix it" = "user wants me to deploy now". Single-action authorization is for the action, not the scope.

This applies to : `firmware/deploy.sh`, `pkill python`, `systemctl restart *`, `ssh root@<chip> 'reboot'`, anything that resets process state or hits the NAND. It does NOT apply to read-only commands (`pgrep`, `cat /tmp/*.log`, `curl http://localhost/api/status`) — those are safe.
