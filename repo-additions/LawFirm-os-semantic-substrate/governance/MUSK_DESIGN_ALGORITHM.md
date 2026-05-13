# Musk-Style Design Algorithm for Skill Review

This repo embeds a five-step design review loop:

```text
1. Question every requirement.
2. Delete unnecessary parts or process steps.
3. Simplify and optimize what remains.
4. Accelerate cycle time.
5. Automate last.
```

## How to apply it to skills

### 1. Question every requirement

Every requirement in a skill must have an owner and a reason. If the skill says "must use tool X," ask why. If the skill says "must produce a 10-section report," ask who needs each section.

### 2. Delete

Delete instructions, examples, tools, scripts, and workflow branches that are not needed. If a deleted piece must be added back later, that is useful evidence.

### 3. Simplify and optimize

Only simplify what survived deletion. Convert vague prompts into contracts. Replace model judgment with deterministic validation where possible.

### 4. Accelerate

Reduce steps, context load, token use, review time, and handoff friction only after the skill is correct and minimal.

### 5. Automate

Automate only the stable part. Never automate semantic promotion, high-risk external writes, or ambiguous legal judgments.

## Scoring

The CLI `grade-algorithm` command scores each skill against this sequence.
