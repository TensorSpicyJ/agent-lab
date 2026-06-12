# Coverage Matrix

Legend:
- `direct`: directly usable locally now or with light extraction
- `candidate`: useful but needs download/access/filtering work
- `limited`: only partial public access or non-ideal format
- `gap`: not well covered by off-the-shelf benchmarks found so far

| Physics field | Current included/local | Existing registered | New open candidates | v0.1 status |
| --- | --- | --- | --- | --- |
| Classical mechanics | SciBench, TPBench public | OlympiadBench, LeanPhysBench | UGPhysics, HiPhO, PHYSICS, PHYBench, MMLU, C-Eval, AGIEval | covered; expand count |
| Electromagnetism | SciBench light | OlympiadBench, LeanPhysBench | UGPhysics, HiPhO, PHYSICS, PHYBench, C-Eval | needs extraction |
| Thermodynamics | SciBench light, Open Physics Diverse core | OlympiadBench, LeanPhysBench | UGPhysics, HiPhO, PHYSICS, PHYBench, ThermoQA, C-Eval | local applied expansion added |
| Statistical mechanics | SciBench light, TPBench public, Open Physics Diverse core, CMT Hard Stress | GPQA, LeanPhysBench light | CMPhysBench, CMT-Benchmark, CritPt | local hard stress expansion added |
| Waves and optics | SciBench light | OlympiadBench, LeanPhysBench | UGPhysics, HiPhO, PHYSICS, PHYBench | needs extraction |
| Modern physics | SciBench | OlympiadBench, LeanPhysBench | UGPhysics, HiPhO, PHYSICS, PHYBench | covered lightly; expand |
| Atomic / AMO physics | SciBench light | GPQA | CritPt | needs frontier extraction |
| Nuclear physics | none local | OlympiadBench, GPQA | CritPt | gap but candidate exists |
| Basic quantum mechanics | SciBench, TPBench public, Open Physics Diverse core | GPQA, LeanPhysBench | UGPhysics, TheoremQA, CMPhysBench | local graduate-symbolic expansion added |
| Advanced quantum mechanics | Open Physics Diverse core light, CMT Hard Stress | GPQA, TPBench | CMPhysBench, CMT-Benchmark, CritPt | local hard stress expansion added |
| Condensed matter | Open Physics Diverse core, CMT Hard Stress | GPQA light | CMPhysBench, CMT-Benchmark, CritPt | local hard stress expansion added |
| Superconductivity | none local | GPQA light | CMPhysBench, CMT-Benchmark | major gap now has open candidates |
| Topological order / topological phases | none local | GPQA/TPBench possible | CMT-Benchmark maybe partial, custom still needed | still gap |
| Quantum information | none local | GPQA, PhysLib/QuantumInfo library | TheoremQA possible, CritPt possible | gap |
| General relativity | TPBench public light | GPQA, TPBench full | CritPt possible | frontier candidate |
| Cosmology | TPBench public light | GPQA, TPBench full | CritPt possible | frontier candidate |
| High-energy theory | TPBench public light | GPQA, TPBench full | CritPt | frontier candidate |
| Mathematical physics | TPBench public light, Open Physics Diverse core light, CMT Hard Stress | GPQA, TPBench, LeanPhysBench | TheoremQA, CritPt, CMT-Benchmark | local hard stress expansion added |
| XRD / crystallography | none local | none | OpenXRD | new experimental candidate |
| Engineering thermodynamics | Open Physics Diverse core | none | ThermoQA | local applied lane added |

Current conclusion:
- Existing local benchmarks still cover basic/intermediate physics more than frontier physics.
- The 2026-06-03 scan adds serious open candidates for condensed matter, superconductivity, XRD, and applied thermodynamics; the local suite now materializes ThermoQA/CMPhysBench samples and the full 50-row CMT-Benchmark hard stress task.
- Topological order/topological phases and thesis-specific oxide thin-film reasoning still need custom additions after the off-the-shelf baselines are stable.
