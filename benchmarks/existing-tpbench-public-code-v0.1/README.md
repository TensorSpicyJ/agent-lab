# existing-tpbench-public-code-v0.1

This benchmark uses public TPBench problems in their code-answer style.

Current local task:
- `tpbench-public-mini-3`
- per-problem attributes in `tasks/tpbench-public-mini-3/problem-metadata.yaml`

Included public TPBench problems:
- `Blackbody in d Dimensions`
- `Boosted Parabolic Trajectory`
- `A 3-State QM Problem`

Design:
- original public TPBench problem statements
- answer as Python functions, matching TPBench answer requirements
- local verifier executes the submitted functions on hidden numerical checks

Source:
- [TPBench website](https://tpbench.org/)
- [TPBench public problems page](https://tpbench.org/?page_id=2)
- [ZhiqiGao/TPBench on Hugging Face](https://huggingface.co/datasets/ZhiqiGao/TPBench)
