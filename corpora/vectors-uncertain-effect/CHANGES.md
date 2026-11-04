# Uncertain-effect corpus changes

## Unreleased — billing evidence and effect authority

Adds the generated P04 F04/F08 examples and their safe controls requested in
[issue #435](https://github.com/probityai/agent-evidence-vectors/issues/435).
The manifest derives the new population and digest. Earlier case files remain
unchanged; no check, reason code, runtime scenario or default-corpus revision is
redefined. A release/tag is a separate maintainer action.

Expected invariant: an unresolved attempt is retried only with the existing
owner-backed protection, and an unknown effect is not reported as settled.
Failure condition: a final invoice is substituted for an owner reconciliation,
or a zero invoice is treated as evidence that the effect did not occur.
Observable: retry_after_unknown or outcome_settled_without_authority; the paired
controls return allow/effect_held. The synthetic billing annotation is not
itself a source of authority. These are record checks, not authentic billing,
production runtime experiments or validation of the sibling billing contract.

Source and case design: Mohammed Messaoudene, P04 at
[c7edf5a](https://github.com/mohammedmessaoudene-cmd/agent-evidence-lab/tree/c7edf5abbdb920e115d791f686bc04cf0524b481/collaborations/open-evidence-lab/p04-execution-billing).
Scope and mapping: astrogilda in issue #435. The separate X1/M4 challenge is
credited to piiiico (Agent Errata) and remains outside these record additions.
Implementation and validation of this contribution used AI assistance; it is
not an independently authored reader or independent human validation.
