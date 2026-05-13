# Skill Intake and Elegance Gate

The Orchestrator should consume only approved skills. It should not search GitHub during normal runs.

Before a skill may be invoked by the Orchestrator, it must have:

1. malicious-skill scan report;
2. skill quality review;
3. algorithmic elegance grade;
4. Semantic Substrate authority entry;
5. human approval record.

The Orchestrator must deny skills that request external writes, unapproved scripts, or canonical mutation.

## Security hardening note

The Orchestrator must consume only skills that have passed both static malicious-skill scanning and semantic malicious-intent scanning. It must not call quarantined skills, candidate skills, imported skills, or skills with `recommendation` other than `safe_for_eval` plus approved registry status. Threat-rule updates are governance inputs, not runtime instructions, and may not self-promote.

