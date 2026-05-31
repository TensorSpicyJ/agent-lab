# Physics IR Related Work Scan

Date: 2026-05-31

## Short Conclusion

There is substantial adjacent work, but I did not find a single framework that directly matches the proposed target:

- phase or effective-theory objects as typed low-energy equivalence classes;
- morphisms as phase transitions, RG flows, dualities, approximations, measurements, and derivation bridges;
- assumption and validity labels as first-class objects;
- verifier-backed benchmark tasks for research agents.

The closest path is to combine four existing lines: scientific/materials ontologies, qualitative physics, applied category theory/resource theories, and formal or benchmark-based physics reasoning.

## Related Work Map

| Line | Representative work | What it gives us | What it does not give us |
| --- | --- | --- | --- |
| Scientific and materials ontologies | EMMO, MDO, Materials Ontology, materials graph ontology | Typed physical/material objects, properties, processes, measurements, models, and FAIR semantics | Usually not a derivation IR; phase equivalence, RG, duality, and benchmark verification are not central |
| Materials knowledge graphs | MatKG, materials experiment knowledge graph | Source-grounded entities and relations extracted from papers or experiments | Good for retrieval/provenance; weak for exact derivation legality and assumption control |
| Qualitative physics | Qualitative Process Theory, QSIM, QPC | State/process/influence/transition representations for physical reasoning under incomplete knowledge | Older AI formalism; qualitative rather than modern typed mathematical derivation; can produce spurious or coarse behavior |
| Applied category theory | Decorated/structured cospans, compositional open systems, Catlab | Object/morphism/composition language for systems, interfaces, and model transformations | General compositional modeling, not a ready physics-agent benchmark or phase-transition IR |
| Resource theories | Quantum thermodynamics and quantum information resource theories | States/resources plus allowed transformations; monotones/invariants as legality checks | Domain-specific transformation theories, not a general ontology for phases and derivations |
| Mathematical/scientific semantic representation | OMDoc/MMT, OntoMathPRO, QUDT/OM units ontologies | Structured mathematical theories, theory morphisms, quantities, units, dimensions | Captures math and units better than physical modelling assumptions and effective-theory validity |
| Formal physics in Lean | Formalizing chemical physics, PhysLib/PhysLean, quantum information formalizations, dimensional-analysis Lean work | Hard correctness for mathematical sub-claims, assumptions, and units | Does not cover all natural-language physical modelling choices; too heavy as the only representation layer |
| Physics LLM benchmarks | SciBench, PHYBench, TPBench, CMT-Benchmark, CritPt, PRL-Bench, PRBench, Hartree-Fock derivation benchmarks | Evaluation harnesses, answer checks, expert rubrics, paper-level reproduction tasks | Mostly judge final answers, calculations, or workflows; rarely use a typed physics IR to attribute failure |

## Design Implication

Our useful niche is not "invent physics ontology from zero." It is a bridge layer:

1. Use ontology/KG ideas for typed objects and provenance.
2. Use categorical/compositional ideas for legal edge composition and invariant transport.
3. Use qualitative physics for state/process/transition patterns when exact equations are unavailable.
4. Use Lean/CAS/numerics/unit checks as backend verifiers, not as the whole language.
5. Use benchmark tasks to force the IR to be operational: type legality, assumption legality, invariant preservation or change, source grounding, and final-answer checks.

## Source Pointers

- EMMO: https://emmc.eu/emmo/
- Materials Design Ontology: https://journals.sagepub.com/doi/10.3233/SW-233340
- Materials graph ontology: https://doi.org/10.1016/j.matlet.2021.129836
- MatKG: https://pmc.ncbi.nlm.nih.gov/articles/PMC10874416/
- QSIM overview: https://web.eecs.umich.edu/~kuipers/research/qsim/qsim-overview.html
- QPC: https://aaai-24.aaai.org/Library/AAAI/1990/aaai90-056.php
- Compositional framework for reaction networks: https://arxiv.org/abs/1704.02051
- Catlab: https://algebraicjulia.github.io/Catlab.jl/
- General resource theories: https://arxiv.org/abs/1901.08127
- OMDoc/MMT: https://docs.mathhub.info/legacy/omdoc-mmt.html
- OntoMathPRO: https://arxiv.org/abs/1407.4833
- QUDT: https://www.qudt.org/
- Formalizing chemical physics in Lean: https://arxiv.org/abs/2210.12150
- PhysLib: https://physlib.io/
- SciBench: https://arxiv.org/abs/2307.10635
- TPBench: https://huggingface.co/datasets/ZhiqiGao/TPBench
- CMT-Benchmark: https://papers.cool/arxiv/2510.05228
- CritPt: https://arxiv.org/abs/2509.26574
- PRL-Bench: https://arxiv.org/abs/2604.15411
- PRBench: https://huggingface.co/papers/2603.27646
- Quantum many-body physics calculations with LLMs: https://www.nature.com/articles/s42005-025-01956-y

## Working Hypothesis

The first benchmarkable version should not try to formalize all physics. It should define a small IR for one controlled domain, such as topological order K-matrix derivations or mean-field/Hartree-Fock derivations:

- object types: model, phase/effective theory, state family, observable, source claim, assumption, verifier result;
- edge types: derives, approximates, preserves invariant, changes invariant, measures, specializes, coarse-grains, dual-to, equivalent-under;
- verifier hooks: algebra/CAS, unit/dimension checks, source excerpt matching, hidden numeric instances, and invariant checks;
- failure tags: object typing error, illegal edge, missing assumption, invalid approximation, invariant mismatch, source hallucination, final-answer mismatch.
