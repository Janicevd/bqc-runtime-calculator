"""
Experiment Runtime Calculator for RSP and BQC Tests

This module provides functions to estimate experiment runtimes for:
- Local tests (A1.1, A1.2, A6.1, A6.2/A6.3)
- Entanglement generation tests (A2.1, A3.1, A4.1, A4.2)
- Remote State Preparation (RSP) tests (A2.2, A3.2, A4.3)
- Blind Quantum Computation (BQC) tests (A5, A6.4, A6.5)

All times are in milliseconds unless otherwise specified.
"""

from dataclasses import dataclass


@dataclass
class ExperimentParameters:
    """Default experimental parameters."""
    n_shots: int = 250            # Number of shots for statistical accuracy
    t_com: float = 0.25           # One-way communication time over 50 km [ms] (250 µs)
    t_emit: float = 0.1           # Time to initialize ion + emit photon [ms] (100 µs)
    t_cooling: float = 2.0        # Time for cooling every 50 attempts [ms]
    t_readout: float = 5.0        # Time for readout of ion qubit, RSP/entanglement [ms]
    p_total: float = 0.004        # Total probability (emission, coupling, conversion, transmission, detection)
    cooling_interval: int = 50    # Number of attempts between cooling cycles
    t_init: float = 3.0           # Re-initialize after readout, Doppler cooling [ms]
    t_read: float = 5.0           # Global readout [ms]
    t_Zrot: float = 0.01          # Individual Z rotation [ms] (10 µs)
    t_address: float = 0.015      # Time to switch between addressing ions [ms] (15 µs)
    t_globrot: float = 0.004      # Global X or Y rotation [ms] (4 µs)
    t_MS: float = 0.2             # MS gate [ms] (200 µs)
    t_hide: float = 0.056         # Hiding 1 ion in a 2-ion string [ms] (56 µs)
    t_wait: float = 0.5           # Time waiting for classical message [ms] (500 µs)


# ── Local tests ───────────────────────────────────────────────────────────────


def local_A1_1_time(params: ExperimentParameters = None) -> float:
    """
    Estimate runtime for test A1.1 (local).

    t_expt = (t_init + t_MS + t_hide + t_address + t_Zrot + t_globrot + t_read
              + t_address + t_hide + t_Zrot + t_globrot + t_read
              + t_cooling/50) * N_shots

    Returns:
        Experiment time in seconds.
    """
    if params is None:
        params = ExperimentParameters()

    per_shot = (
        params.t_init
        + params.t_MS
        + params.t_hide
        + params.t_address
        + params.t_Zrot
        + params.t_globrot
        + params.t_read
        + params.t_address
        + params.t_hide
        + params.t_Zrot
        + params.t_globrot
        + params.t_read
        + params.t_cooling / params.cooling_interval
    )
    return per_shot * params.n_shots / 1000


def local_A1_2_time(params: ExperimentParameters = None) -> float:
    """
    Estimate runtime for test A1.2 (local, adds t_wait per shot vs A1.1).

    t_expt = (t_A1.1_per_shot + t_wait) * N_shots

    Returns:
        Experiment time in seconds.
    """
    if params is None:
        params = ExperimentParameters()

    per_shot = (
        params.t_init
        + params.t_MS
        + params.t_hide
        + params.t_address
        + params.t_Zrot
        + params.t_globrot
        + params.t_read
        + params.t_address
        + params.t_hide
        + params.t_Zrot
        + params.t_globrot
        + params.t_read
        + params.t_wait
        + params.t_cooling / params.cooling_interval
    )
    return per_shot * params.n_shots / 1000


def local_A6_1_time(params: ExperimentParameters = None) -> float:
    """
    Estimate runtime for test A6.1 (local).

    t_expt = (t_init + t_Zrot + t_globrot + t_wait + t_hide + t_address
              + t_init + t_globrot + t_read
              + t_address + t_hide + t_Zrot + t_globrot + t_read
              + t_cooling/50) * N_shots

    Returns:
        Experiment time in seconds.
    """
    if params is None:
        params = ExperimentParameters()

    per_shot = (
        params.t_init
        + params.t_Zrot
        + params.t_globrot
        + params.t_wait
        + params.t_hide
        + params.t_address
        + params.t_init
        + params.t_globrot
        + params.t_read
        + params.t_address
        + params.t_hide
        + params.t_Zrot
        + params.t_globrot
        + params.t_read
        + params.t_cooling / params.cooling_interval
    )
    return per_shot * params.n_shots / 1000


def local_A6_23_time(params: ExperimentParameters = None) -> float:
    """
    Estimate runtime for tests A6.2/A6.3 (local, adds one t_globrot vs A6.1).

    Returns:
        Experiment time in seconds.
    """
    if params is None:
        params = ExperimentParameters()

    per_shot = (
        params.t_init
        + params.t_Zrot
        + params.t_globrot
        + params.t_wait
        + params.t_hide
        + params.t_address
        + params.t_init
        + params.t_globrot
        + params.t_read
        + params.t_address
        + params.t_hide
        + params.t_Zrot
        + params.t_globrot
        + params.t_read
        + params.t_globrot  # extra global rotation vs A6.1
        + params.t_cooling / params.cooling_interval
    )
    return per_shot * params.n_shots / 1000


# ── Entanglement / RSP attempt time ──────────────────────────────────────────


def attempt_time(params: ExperimentParameters = None) -> float:
    """
    Average time per attempt for entanglement generation and RSP tests.

    t_attempt = t_cooling/50 + t_emit + 2*t_com

    Returns:
        Average attempt time in milliseconds.
    """
    if params is None:
        params = ExperimentParameters()

    return (
        params.t_cooling / params.cooling_interval
        + params.t_emit
        + 2 * params.t_com
    )


# ── Entanglement generation ───────────────────────────────────────────────────


def entanglement_experiment_time(
    params: ExperimentParameters = None,
    return_minutes: bool = True,
) -> float:
    """
    Estimated runtime for entanglement generation tests (A2.1, A3.1, A4.1, A4.2).

    N_clicks = N_shots * 3  (3 measurement bases: XX, YY, ZZ)
    t_expt = (t_attempt / p_total + t_readout) * N_clicks

    Returns:
        Estimated experiment time.
    """
    if params is None:
        params = ExperimentParameters()

    n_clicks = params.n_shots * 3
    t_expt_ms = (attempt_time(params) / params.p_total + params.t_readout) * n_clicks

    return t_expt_ms / 60_000 if return_minutes else t_expt_ms


# ── RSP ───────────────────────────────────────────────────────────────────────


def rsp_experiment_time(
    params: ExperimentParameters = None,
    return_minutes: bool = True,
) -> float:
    """
    Estimated runtime for RSP tests (A2.2, A3.2, A4.3).

    N_clicks = N_shots * 3 bases * 8 target states
    t_expt = (t_attempt / p_total + t_readout) * N_clicks

    Returns:
        Estimated experiment time.
    """
    if params is None:
        params = ExperimentParameters()

    n_clicks = params.n_shots * 3 * 8
    t_expt_ms = (attempt_time(params) / params.p_total + params.t_readout) * n_clicks

    return t_expt_ms / 60_000 if return_minutes else t_expt_ms


# ── BQC ───────────────────────────────────────────────────────────────────────


def bqc_attempt_time(t_pol: float, params: ExperimentParameters = None) -> float:
    """
    Average time per attempt for BQC tests.

    In BQC the client changes measurement basis each attempt, so polarization
    controller rotation time determines the attempt rate.

    t_attempt = [max(t_cooling + t_emit + 2*t_com, t_pol)
                 + 49 * max(t_emit + 2*t_com, t_pol)] / 50

    Args:
        t_pol: Time to change polarization controller rotation [ms].

    Returns:
        Average attempt time in milliseconds.
    """
    if params is None:
        params = ExperimentParameters()

    t_with_cooling = params.t_cooling + params.t_emit + 2 * params.t_com
    t_without_cooling = params.t_emit + 2 * params.t_com

    return (
        max(t_with_cooling, t_pol)
        + (params.cooling_interval - 1) * max(t_without_cooling, t_pol)
    ) / params.cooling_interval


def bqc_experiment_time(
    t_pol: float,
    params: ExperimentParameters = None,
    return_hours: bool = True,
) -> float:
    """
    Estimated BQC experiment runtime for a given polarization controller speed.

    t_expt = (t_attempt / p_total + t_hide + t_wait + t_Zrot + t_globrot + t_read) * N_shots

    Args:
        t_pol: Time to change polarization controller rotation [ms].

    Returns:
        Estimated experiment time.
    """
    if params is None:
        params = ExperimentParameters()

    t_local = (
        params.t_hide + params.t_wait + params.t_Zrot + params.t_globrot + params.t_read
    )
    t_expt_ms = (
        bqc_attempt_time(t_pol, params) / params.p_total + t_local
    ) * params.n_shots

    return t_expt_ms / 3_600_000 if return_hours else t_expt_ms


def bqc_polarization_allowance(
    target_time_hours: float,
    params: ExperimentParameters = None,
) -> float:
    """
    Maximum allowable polarization controller rotation time for a target BQC runtime.

    Inverts the BQC experiment time formula (assuming t_pol dominates):
    t_pol = (t_expt / N_shots - t_hide - t_wait - t_Zrot - t_globrot - t_read) * p_total

    Note: Assumes t_pol > t_cooling + t_emit + 2*t_com (= 2.6 ms), which holds
    for most commercial polarization controllers.

    Args:
        target_time_hours: Target experiment time in hours.

    Returns:
        Maximum polarization controller rotation time in milliseconds.
    """
    if params is None:
        params = ExperimentParameters()

    target_time_ms = target_time_hours * 3_600_000
    t_local = (
        params.t_hide + params.t_wait + params.t_Zrot + params.t_globrot + params.t_read
    )
    t_pol = (target_time_ms / params.n_shots - t_local) * params.p_total

    t_threshold = params.t_cooling + params.t_emit + 2 * params.t_com
    if t_pol < t_threshold:
        print(
            f"Warning: Calculated t_pol ({t_pol:.2f} ms) is less than threshold "
            f"({t_threshold:.2f} ms). The simplified formula may not be accurate."
        )

    return t_pol


# ── Summary ───────────────────────────────────────────────────────────────────


def print_summary(params: ExperimentParameters = None):
    """Print a summary of all calculations with the given parameters."""
    if params is None:
        params = ExperimentParameters()

    print("=" * 60)
    print("Experiment Runtime Calculator")
    print("=" * 60)
    print("\nParameters:")
    print(f"  N_shots:    {params.n_shots}")
    print(f"  t_com:      {params.t_com} ms")
    print(f"  t_emit:     {params.t_emit} ms")
    print(f"  t_cooling:  {params.t_cooling} ms")
    print(f"  t_readout:  {params.t_readout} ms")
    print(f"  p_total:    {params.p_total}")
    print(f"  t_init:     {params.t_init} ms")
    print(f"  t_read:     {params.t_read} ms")
    print(f"  t_Zrot:     {params.t_Zrot} ms")
    print(f"  t_address:  {params.t_address} ms")
    print(f"  t_globrot:  {params.t_globrot} ms")
    print(f"  t_MS:       {params.t_MS} ms")
    print(f"  t_hide:     {params.t_hide} ms")
    print(f"  t_wait:     {params.t_wait} ms")

    print("\n" + "-" * 60)
    print("Local Tests")
    print("-" * 60)
    print(f"  A1.1:    {local_A1_1_time(params):.2f} s")
    print(f"  A1.2:    {local_A1_2_time(params):.2f} s")
    print(f"  A6.1:    {local_A6_1_time(params):.2f} s")
    print(f"  A6.2/3:  {local_A6_23_time(params):.2f} s")

    print("\n" + "-" * 60)
    print("Entanglement Generation Tests (A2.1, A3.1, A4.1, A4.2)")
    print("-" * 60)
    t_att = attempt_time(params)
    print(f"  N_clicks:  {params.n_shots * 3} ({params.n_shots} shots × 3 bases)")
    print(f"  t_attempt: {t_att:.3f} ms")
    print(f"  Runtime:   {entanglement_experiment_time(params):.1f} minutes")

    print("\n" + "-" * 60)
    print("RSP Tests (A2.2, A3.2, A4.3)")
    print("-" * 60)
    print(f"  N_clicks:  {params.n_shots * 3 * 8} ({params.n_shots} shots × 3 bases × 8 states)")
    print(f"  t_attempt: {t_att:.3f} ms")
    print(f"  Runtime:   {rsp_experiment_time(params):.1f} minutes")

    print("\n" + "-" * 60)
    print("BQC Tests (A5, A6.4, A6.5)")
    print("-" * 60)
    for t_pol in [50, 100, 173, 200]:
        t_expt_bqc = bqc_experiment_time(t_pol=t_pol, params=params)
        print(f"  t_pol = {t_pol:3d} ms  →  runtime = {t_expt_bqc:.2f} hours")

    print("\n" + "-" * 60)
    print("Polarization Controller Allowance")
    print("-" * 60)
    for target_hours in [1, 2, 3, 4]:
        t_pol_max = bqc_polarization_allowance(target_hours, params=params)
        print(f"  Target {target_hours} hour(s)  →  t_pol ≤ {t_pol_max:.1f} ms")

    print("=" * 60)


if __name__ == "__main__":
    print_summary()
