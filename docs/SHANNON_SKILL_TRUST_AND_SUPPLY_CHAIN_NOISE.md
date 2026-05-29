# Shannon Skill Trust and Supply-Chain Noise

Status: Non-canonical concept note.
Authority: Explanatory only. Does not change skill approval policy, trust schema, scanner behavior, permission boundaries, or any registry artifact.

## BLUF

A skill is a transmitter inside the LawFirm OS channel. Imported skills, especially third-party skills, are potentially noisy and potentially adversarial sources. The current pipeline — discover → quarantine → static scan → semantic intent scan → grade → approve → install — is the kind of layered redundancy and error-control that information theory describes for transmission through an untrusted channel. This note explains the framing; it does not modify the pipeline, the threat rulepacks, the trust schema, or the approval policy.

Master conceptual reference: `../_shared/SHANNON_INFORMATION_THEORY_FOR_AI_GOVERNANCE_MASTER.md` (workspace-shared, non-canonical).

## Boundary

This note does **not**:

- modify any scanner code in `src/`;
- alter `quarantine/`, `registry/`, `security/`, or `evals/`;
- change threat rulepacks, severity policy, or scanner gates;
- modify trust schema, approval gates, or permission boundaries;
- redefine what counts as a malicious pattern, prompt injection, or hidden instruction.

The non-negotiable boundary from README — that a skill must not become a backdoor or a shadow source of truth — remains in force.

## Communication model

| Shannon layer | Skills-registry equivalent |
|---|---|
| Information source | The skill's intended capability (a documented, source-supported task it claims to perform) |
| Transmitter | The skill author / packager (first-party, internal, or third-party) |
| Channel | discover → quarantine → static scan → semantic intent scan → grade → approve → install |
| Noise | Malicious code, prompt injection, hidden instructions, secret exfiltration, telemetry disguise, image beacons, encoded payloads, instruction-hierarchy overrides, split network commands |
| Receiver | LawFirm OS runtimes that load installed skills (orchestrator, agent harnesses) |
| Destination | Governed AI workflows that consume the skill |
| Redundancy | Three scanner gates (static + semantic + rulepack-safety), independent grading, threat-rule severity validation, append-only audit, registry pinning |
| Error correction | Quarantine on suspicion, rulepack rollback if severity would drop, exception emission, removal from `.agents/skills` |
| Channel capacity | Scanner throughput, reviewer bandwidth, rulepack-validation depth, governance approval throughput |

## Real math used

Notation:

- $X$ = the skill's true intent (the actual side effects, exfiltration paths, network behavior, secret access).
- $Y_1, Y_2, Y_3$ = observations from the static scan, semantic intent scan, and rulepack-safety scan respectively.
- $\hat{X}$ = the registry's classification (safe / quarantined / rejected).

### Conditional entropy after layered scanning

For independent (or weakly dependent) scans:

```math
H\!\left(X \mid Y_1, Y_2, Y_3\right) \;\le\; H\!\left(X \mid Y_i\right) \quad \text{for each } i
```

Repo interpretation:

- Adding an independent gate cannot increase residual uncertainty about $X$. Three gates that each detect a partially different attack surface (syntactic, semantic, rule-policy) lower $H(X \mid Y_1, Y_2, Y_3)$ more than any one gate alone. This is exactly the engineering justification for the three-gate design.

### Mutual information

```math
I(X;Y) \;=\; H(X) - H(X \mid Y)
```

Repo interpretation:

- A scanner gate is valuable insofar as its output $Y$ carries mutual information with the skill's true intent $X$. A "scanner" that fires on every skill the same way carries zero mutual information and is pure overhead.

### Fano-style lower bound on missed-attack probability

For class set $\mathcal{X} = \{\text{safe}, \text{malicious}, \dots\}$ and classifier $\hat{X}$ with error probability $P_e$:

```math
H\!\left(X \mid \hat{X}\right) \;\le\; h_2(P_e) \;+\; P_e \log_2(|\mathcal{X}| - 1)
```

Repo interpretation:

- If residual uncertainty about a skill's intent is high after scanning, the probability of a wrong approval cannot be small. **Design rule:** when the gates leave high $H(X \mid \hat{X})$, do not approve. Send the skill back to quarantine, or require human review. This is what "deny-by-default" already implements; the inequality just says it cannot be otherwise.

### Hamming-style redundancy

For a code with minimum Hamming distance $d_{\min}$:

```math
\text{detectable errors} = d_{\min} - 1, \qquad \text{correctable errors} = \left\lfloor \frac{d_{\min}-1}{2} \right\rfloor
```

Repo interpretation:

- Three independent gates with overlapping coverage approximate $d_{\min} = 3$ for the kinds of attacks they each detect. That is enough redundancy to detect single-pattern bypass attempts, even if no single gate catches them. Correction comes from policy (quarantine, rejection), not from the gates themselves.

### Data processing inequality

If $X \to Y_1, Y_2, Y_3 \to \hat{X}$:

```math
I(X; \hat{X}) \;\le\; I(X; Y_1, Y_2, Y_3)
```

Repo interpretation:

- The final approval classification cannot carry more information about the skill's true intent than the union of the three scan observations. If the scans are weak, approval cannot be strong. No amount of grading prose makes up for a thin observation channel.

### Drift across rulepack versions (optional, data-dependent)

```math
D_{\mathrm{KL}}(P_{\text{current rulepack alerts}} \,\Vert\, P_{\text{previous rulepack alerts}})
```

Repo interpretation:

- When a rulepack changes severity or category coverage, $D_{\mathrm{KL}}$ between the alert distribution before and after is a candidate drift signal. **Today this is conceptual; use only with a published baseline and zero-count smoothing.** Never let drift auto-update severity.

## Integration implications

These are conceptual implications, not new requirements:

1. **The three-gate design is structured redundancy.** It is what allows the registry to claim *layered* detection rather than relying on any one gate. The inequality $H(X \mid Y_1, Y_2, Y_3) \le H(X \mid Y_i)$ is the formal justification.
2. **Deny-by-default is the Fano consequence.** Where residual uncertainty after scanning is high, the unavoidable error probability is non-trivial. Refusing approval is the only choice that does not silently absorb that error rate.
3. **Threat-rule severity validation matters.** A rulepack that lowers active severity is a downgrade of $I(X; \hat{X})$ across the channel. Preventing rulepacks from silently reducing severity preserves the channel's coding strength.
4. **Skills must not become shadow sources of truth.** The data processing inequality says they cannot legitimately carry more authority downstream than substrate granted upstream. A skill that asserts canonical claims is exceeding its position in the Markov chain.
5. **Generic skills carry low mutual information.** A skill that "does everything" lowers $I(X;Y)$ for any specific task. Best-in-class skill doctrine, including the Musk-style design algorithm, is in part a mutual-information argument: delete what is generic so the remainder is specific.

## Safe design questions

For each candidate skill, rulepack change, or scanner update:

1. What is the authoritative source for this skill's claimed capability?
2. How is the skill encoded so the channel preserves intent (manifest, permissions, declared tools)?
3. Where can supply-chain noise enter (third-party origin, hidden instructions, encoded payloads, split network calls)?
4. Are the gates inside capacity (scanner throughput, reviewer bandwidth, rulepack-validation depth)?
5. What independent redundancy exists (three gates, independent grading, audit log)?
6. What error-correction path applies (quarantine, rejection, rulepack rollback, exception emission)?
7. What is the residual classification uncertainty after gates, and is the approval decision consistent with it?

## Non-goals

- This note does not propose new scanner categories, new threat-rule types, or new severity levels.
- This note does not reduce, raise, or rearrange any existing severity classification.
- This note does not authorize cross-repo skill mutation of substrate canon.
- This note does not propose any $D_{\mathrm{KL}}$ or Fano gauge as a required runtime metric today.

## References

Conceptual only.

- Claude E. Shannon, "A Mathematical Theory of Communication," 1948.
- Thomas M. Cover and Joy A. Thomas, *Elements of Information Theory*, Wiley.
- David J. C. MacKay, *Information Theory, Inference, and Learning Algorithms*, Cambridge University Press.
- Workspace-shared master file: `../_shared/SHANNON_INFORMATION_THEORY_FOR_AI_GOVERNANCE_MASTER.md`.
