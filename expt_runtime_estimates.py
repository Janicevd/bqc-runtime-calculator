"""
Experiment Runtime Calculator for RSP and BQC Tests

This module provides functions to estimate experiment runtimes for:
- Remote State Preparation (RSP) tests
- Blind Quantum Computation (BQC) tests

All times are in milliseconds unless otherwise specified.
"""

from dataclasses import dataclass


@dataclass
class ExperimentParameters:
    """Default experimental parameters."""
    t_com: float = 0.25        # One-way communication time over 50 km [ms]
    t_emit: float = 0.1        # Time to initialize ion + emit photon [ms]
    t_cooling: float = 2.0     # Time for cooling every 50 attempts [ms]
    t_readout: float = 5.0     # Time for readout of ion qubit [ms]
    p_total: float = 0.004     # Total probability (emission, coupling, conversion, transmission, detection)
    cooling_interval: int = 50 # Number of attempts between cooling cycles


def rsp_attempt_time(params: ExperimentParameters = None) -> float:
    """
    Calculate the average time per attempt for RSP tests.
    
    In RSP tests, the client measurement basis stays constant, so polarization
    controller rotation time is negligible.
    
    t_attempt = t_cooling/50 + t_emit + 2*t_com
    
    Returns:
        Average attempt time in milliseconds.
    """
    if params is None:
        params = ExperimentParameters()
    
    return (params.t_cooling / params.cooling_interval 
            + params.t_emit 
            + 2 * params.t_com)


def rsp_experiment_time(
    n_shots: int = 6000,
    params: ExperimentParameters = None,
    return_minutes: bool = True
) -> float:
    """
    Calculate the estimated RSP experiment runtime.
    
    t_expt = (t_attempt / p_total + t_readout) * N_shots
    
    Args:
        n_shots: Number of shots. Default is 250 shots × 3 bases × 8 target states = 6000.
        params: Experimental parameters. Uses defaults if None.
        return_minutes: If True, return time in minutes; otherwise in milliseconds.
    
    Returns:
        Estimated experiment time.
    """
    if params is None:
        params = ExperimentParameters()
    
    t_attempt = rsp_attempt_time(params)
    t_expt_ms = (t_attempt / params.p_total + params.t_readout) * n_shots
    
    if return_minutes:
        return t_expt_ms / 60_000
    return t_expt_ms


def bqc_attempt_time(t_pol: float, params: ExperimentParameters = None) -> float:
    """
    Calculate the average time per attempt for BQC tests.
    
    In BQC, the client changes measurement basis each attempt, so polarization
    controller rotation time matters.
    
    t_attempt = [max(t_cooling + t_emit + 2*t_com, t_pol) 
                 + 49 * max(t_emit + 2*t_com, t_pol)] / 50
    
    Args:
        t_pol: Time to change polarization controller rotation [ms].
        params: Experimental parameters. Uses defaults if None.
    
    Returns:
        Average attempt time in milliseconds.
    """
    if params is None:
        params = ExperimentParameters()
    
    # Time for attempt with cooling
    t_with_cooling = params.t_cooling + params.t_emit + 2 * params.t_com
    # Time for attempt without cooling
    t_without_cooling = params.t_emit + 2 * params.t_com
    
    t_attempt = (
        max(t_with_cooling, t_pol) 
        + (params.cooling_interval - 1) * max(t_without_cooling, t_pol)
    ) / params.cooling_interval
    
    return t_attempt


def bqc_experiment_time(
    t_pol: float,
    n_shots: int = 250,
    params: ExperimentParameters = None,
    return_hours: bool = True
) -> float:
    """
    Calculate the estimated BQC experiment runtime for a given polarization controller speed.
    
    t_expt = (t_attempt / p_total + t_readout) * N_shots
    
    Args:
        t_pol: Time to change polarization controller rotation [ms].
        n_shots: Number of shots. Default is 250.
        params: Experimental parameters. Uses defaults if None.
        return_hours: If True, return time in hours; otherwise in milliseconds.
    
    Returns:
        Estimated experiment time.
    """
    if params is None:
        params = ExperimentParameters()
    
    t_attempt = bqc_attempt_time(t_pol, params)
    t_expt_ms = (t_attempt / params.p_total + params.t_readout) * n_shots
    
    if return_hours:
        return t_expt_ms / 3_600_000
    return t_expt_ms


def bqc_polarization_allowance(
    target_time_hours: float,
    n_shots: int = 250,
    params: ExperimentParameters = None
) -> float:
    """
    Calculate the maximum allowable polarization controller rotation time
    to achieve a target BQC experiment runtime.
    
    This inverts the BQC experiment time calculation:
    t_pol = (t_expt / N_shots - t_readout) * p_total
    
    Note: This assumes t_pol > t_cooling + t_emit + 2*t_com, which is typically
    valid for commercial polarization controllers.
    
    Args:
        target_time_hours: Target experiment time in hours.
        n_shots: Number of shots. Default is 250.
        params: Experimental parameters. Uses defaults if None.
    
    Returns:
        Maximum polarization controller rotation time in milliseconds.
    """
    if params is None:
        params = ExperimentParameters()
    
    target_time_ms = target_time_hours * 3_600_000
    t_pol = (target_time_ms / n_shots - params.t_readout) * params.p_total
    
    # Check if assumption is valid
    t_threshold = params.t_cooling + params.t_emit + 2 * params.t_com
    if t_pol < t_threshold:
        print(f"Warning: Calculated t_pol ({t_pol:.2f} ms) is less than threshold "
              f"({t_threshold:.2f} ms). The simplified formula may not be accurate.")
    
    return t_pol


def print_summary(params: ExperimentParameters = None):
    """Print a summary of calculations with default parameters."""
    if params is None:
        params = ExperimentParameters()
    
    print("=" * 60)
    print("Experiment Runtime Calculator")
    print("=" * 60)
    print("\nParameters:")
    print(f"  t_com (communication time):    {params.t_com} ms")
    print(f"  t_emit (emission time):        {params.t_emit} ms")
    print(f"  t_cooling (cooling time):      {params.t_cooling} ms")
    print(f"  t_readout (readout time):      {params.t_readout} ms")
    print(f"  p_total (success probability): {params.p_total}")
    
    print("\n" + "-" * 60)
    print("RSP Test Estimates")
    print("-" * 60)
    t_attempt_rsp = rsp_attempt_time(params)
    t_expt_rsp = rsp_experiment_time(n_shots=6000, params=params)
    print(f"  N_shots: 6000 (250 shots × 3 bases × 8 states)")
    print(f"  t_attempt: {t_attempt_rsp:.3f} ms")
    print(f"  Estimated runtime: {t_expt_rsp:.1f} minutes")
    
    print("\n" + "-" * 60)
    print("BQC Test Estimates")
    print("-" * 60)
    for t_pol in [50, 100, 172, 200]:
        t_expt_bqc = bqc_experiment_time(t_pol=t_pol, n_shots=250, params=params)
        print(f"  t_pol = {t_pol:3d} ms  →  runtime = {t_expt_bqc:.2f} hours")
    
    print("\n" + "-" * 60)
    print("Polarization Controller Allowance")
    print("-" * 60)
    for target_hours in [1, 2, 3, 4]:
        t_pol_max = bqc_polarization_allowance(target_hours, n_shots=250, params=params)
        print(f"  Target {target_hours} hour(s)  →  t_pol ≤ {t_pol_max:.1f} ms")
    
    print("=" * 60)


if __name__ == "__main__":
    print_summary()
    
    # Example: Custom parameters
    print("\n\nExample with custom parameters:")
    custom_params = ExperimentParameters(
        p_total=0.01,  # Higher success probability
        t_readout=3.0  # Faster readout
    )
    print(f"RSP time with p_total=0.01: {rsp_experiment_time(params=custom_params):.1f} minutes")