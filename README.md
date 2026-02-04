# BQC Runtime Calculator

Estimate experiment runtimes for Remote State Preparation (RSP) and Blind Quantum Computation (BQC) tests.

## Usage

```python
from expt_runtime_estimates import rsp_experiment_time, bqc_experiment_time

# RSP experiment time (returns minutes)
rsp_time = rsp_experiment_time(n_shots=6000)

# BQC experiment time (returns hours)
bqc_time = bqc_experiment_time(t_pol=100, n_shots=250)
```

Run the module directly for a summary with default parameters:

```bash
python expt_runtime_estimates.py
```

## Citation

```bibtex
@software{vandam2026bqc,
  author       = {van Dam, Janice},
  title        = {{BQC Runtime Calculator}},
  year         = {2026},
  publisher    = {GitHub},
  url          = {https://github.com/Janicevd/bqc-runtime-calculator}
}
```
