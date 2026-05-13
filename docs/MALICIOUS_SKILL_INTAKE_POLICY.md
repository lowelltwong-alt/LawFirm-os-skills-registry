# Malicious Skill Intake Policy

Assume many public skills are adversarial, careless, stale, or over-permissioned until proven otherwise.

The intake algorithm is deliberately simple:

```text
discover -> quarantine -> hash -> static scan -> semantic intent scan -> rulepack safety check -> quality/elegance grade -> explicit human approval
```

No skill may skip quarantine. No imported script is executed during intake. No scanner result is allowed to approve a skill by itself.

## Threat classes

- **Prompt injection:** attempts to override system/developer instructions, reviewer instructions, security review, or approval gates.
- **Secret exfiltration:** attempts to read, summarize, move, or publish tokens, `.env`, credentials, client data, matter data, local configuration, or privileged documents.
- **Disguised telemetry:** secret or file access framed as diagnostics, support, analytics, crash reporting, observability, or maintenance.
- **Hidden network exfiltration:** image beacons, tracking pixels, callback URLs, query-parameter payloads, webhooks, or external endpoints.
- **Remote code execution:** `curl | bash`, PowerShell downloads, dynamic `eval`, shell execution, subprocess calls, and downloaded payloads.
- **Persistence:** cron, launch agents, scheduled tasks, Git hooks, GitHub workflows, startup folders, authorized keys, or system services.
- **Hidden instructions:** encoded commands, invisible characters, split strings, base64/hex/char-code payloads, deceptive comments, or instructions to future agents not to inspect files.
- **Excessive agency:** skills requesting browser, shell, filesystem, MCP, email, messaging, or external-write authority without a clear bounded contract.
- **Supply-chain manipulation:** scripts, binaries, symlinks, workflows, git hooks, opaque payloads, or rulepacks that weaken the scanner.

## Gate 1: static scan

The static scanner catches obvious file, path, metadata, and code patterns. It looks for known risky surfaces such as secrets, shell execution, network posting, obfuscation, persistence, GitHub workflows, Git hooks, symlinks, binaries, and risky tool declarations.

Static scan is fast, deterministic, and useful, but it is not sufficient by itself.

## Gate 2: semantic intent scan

The semantic intent scanner looks for the **purpose** of a skill, not only exact strings. It is designed to catch paraphrased malicious behavior such as:

- “collect private configuration and make it available to a remote maintenance service”;
- “send diagnostics containing environment variables to analytics”;
- “render a tracking pixel with local state in a query string”;
- split commands like `'c' + 'url'` or `'w' + 'get'`;
- base64, hex, or character-code payloads hiding outbound commands;
- instructions to future agents to skip review, ignore policy, or conceal behavior.

Any high or critical semantic-intent finding blocks approval and requires rejection or security-owner review.

## Gate 3: threat-rulepack safety check

Threat rules are updateable but not self-promoting:

```text
new attacker pattern -> candidate rulepack -> schema validation -> regex safety validation -> staged rulepack -> explicit approval -> active rulepack
```

Rulepacks are treated as untrusted inputs. They may add detections, but they may not weaken the scanner.

Reject rulepacks that:

- contain ReDoS-prone regexes such as nested quantifiers or repeated ambiguous groups;
- contain backreferences, complex lookarounds, or overly long patterns;
- remove categories, disable the scanner, or create global allowlists;
- lower the severity of an existing active rule;
- alter approval policy;
- include unknown schema fields;
- fail regex compilation or time-budget smoke tests.

## Approval rule

A candidate may move from quarantine to approved only if:

1. it has `SKILL.md` with valid `name` and `description`;
2. all files are hashed;
3. static scan does not require rejection/quarantine/manual security review;
4. semantic intent scan is `none` or `low` only;
5. quality/elegance evaluation passes;
6. `approve-skill --approve` is run by a human.

## Non-negotiable boundaries

- Do not execute candidate skill scripts.
- Do not fetch payloads referenced by candidate skills.
- Do not trust a skill because it came from a popular repo.
- Do not let a rulepack self-promote.
- Do not let a skill or scanner mutate Semantic Substrate canon.
- Do not let Exception Lake promote a skill gap into an approved skill.
- Do not let Orchestrator invoke unapproved skills.
