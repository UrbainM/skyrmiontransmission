"""
SKYRMION DECAY DIAGNOSTIC TOOL

Purpose: Understand why skyrmions collapse to m_z = +1 after ~500 steps
Metrics: Skyrmion count, density, size, winding number, energy per skyrmion

Output: Detailed time-series data for parameter optimization
"""

import numpy as np
from skyrmion_simulator import SkyrmionSimulator, MicromagneticParams
import json
from pathlib import Path


def compute_winding_number(m):
    """
    Compute skyrmion winding number (topological charge)
    
    Q = (1/4π) ∫ m · (∂m/∂x × ∂m/∂y) dA
    
    Skyrmion: Q = ±1
    Background: Q = 0
    """
    ny, nx, _ = m.shape
    
    # Compute derivatives (with periodic boundary conditions)
    m_x = np.roll(m, -1, axis=1) - np.roll(m, 1, axis=1)  # ∂m/∂x
    m_y = np.roll(m, -1, axis=0) - np.roll(m, 1, axis=0)  # ∂m/∂y
    
    # Cross product: ∂m/∂x × ∂m/∂y
    cross = np.cross(m_x.reshape(-1, 3), m_y.reshape(-1, 3)).reshape(ny, nx, 3)
    
    # Dot product: m · (∂m/∂x × ∂m/∂y)
    integrand = np.sum(m * cross, axis=2)
    
    # Total winding number
    Q_total = np.sum(integrand) / (4 * np.pi)
    
    return Q_total


def identify_skyrmions(m, threshold_mz=-0.3):
    """
    Identify skyrmion locations: regions where m_z < threshold_mz
    
    Returns: count, density, average size, positions
    """
    m_z = m[:, :, 2]
    
    # Skyrmion cores: m_z significantly negative (reversed)
    skyrmion_mask = m_z < threshold_mz
    count = np.sum(skyrmion_mask)
    density = count / (m_z.shape[0] * m_z.shape[1])
    
    # Find connected components (skyrmion clusters)
    from scipy import ndimage
    labeled_array, num_features = ndimage.label(skyrmion_mask)
    
    # Compute size of each skyrmion
    if num_features > 0:
        sizes = ndimage.sum(skyrmion_mask, labeled_array, range(1, num_features + 1))
        avg_size = np.mean(sizes)
        max_size = np.max(sizes)
        min_size = np.min(sizes)
    else:
        avg_size = 0
        max_size = 0
        min_size = 0
    
    # Find positions (center of mass)
    if num_features > 0:
        positions = ndimage.center_of_mass(skyrmion_mask, labeled_array, range(1, num_features + 1))
    else:
        positions = []
    
    return {
        'count': count,
        'num_skyrmions': num_features,
        'density': density,
        'avg_size': avg_size,
        'max_size': max_size,
        'min_size': min_size,
        'positions': positions
    }


def compute_energy_per_skyrmion(sim, m):
    """
    Estimate energy per skyrmion using the simulator's energy calculation
    """
    # Get current energy from simulator (uses sim.m internally)
    E_total = sim._compute_energy()
    
    # Skyrmion contribution (rough estimate)
    skyrmion_info = identify_skyrmions(m)
    num_skyrmions = max(1, skyrmion_info['num_skyrmions'])
    E_per_skyrmion = E_total / num_skyrmions
    
    return E_per_skyrmion, E_total, 0.0, 0.0


def run_decay_analysis(params=None, num_steps=2000, save_interval=50):
    """
    Run detailed skyrmion decay analysis
    
    Records metrics every save_interval steps
    """
    if params is None:
        params = MicromagneticParams()
    
    sim = SkyrmionSimulator(params)
    
    # m is already initialized with noise in constructor
    
    metrics = {
        'step': [],
        'skyrmion_count': [],
        'skyrmion_num': [],
        'skyrmion_density': [],
        'skyrmion_avg_size': [],
        'winding_number': [],
        'total_energy': [],
        'energy_per_skyrmion': [],
        'mz_mean': [],
        'mz_std': [],
        'mz_min': [],
        'mz_max': [],
    }
    
    print(f"\n{'='*80}")
    print(f"SKYRMION DECAY ANALYSIS")
    print(f"{'='*80}")
    print(f"Parameters:")
    print(f"  A = {params.A} J/m")
    print(f"  D = {params.D} J/m²")
    print(f"  K_z = {params.K_z} J/m³")
    print(f"  B_z = {params.B_z} T")
    print(f"  dt = {params.dt} s")
    print(f"\nSimulation: {num_steps} steps, metric every {save_interval} steps")
    print(f"{'='*80}\n")
    
    print(f"{'Step':>6} | {'Skyrmions':>10} | {'Density':>8} | {'Winding#':>10} | "
          f"{'Energy':>12} | {'E/Skyr':>10} | {'Mz_mean':>8} | {'Mz_std':>8}")
    print(f"{'-'*110}")
    
    for step in range(num_steps):
        # Evolve
        sim.step(use_euler=True)
        m = sim.m.copy()
        
        # Record metrics every save_interval
        if step % save_interval == 0:
            skyrmion_info = identify_skyrmions(m)
            Q = compute_winding_number(m)
            E_per_skyr, E_total, E_bg, E_skyr = compute_energy_per_skyrmion(sim, m)
            
            m_z = m[:, :, 2]
            mz_mean = np.mean(m_z)
            mz_std = np.std(m_z)
            mz_min = np.min(m_z)
            mz_max = np.max(m_z)
            
            metrics['step'].append(step)
            metrics['skyrmion_count'].append(skyrmion_info['count'])
            metrics['skyrmion_num'].append(skyrmion_info['num_skyrmions'])
            metrics['skyrmion_density'].append(skyrmion_info['density'])
            metrics['skyrmion_avg_size'].append(skyrmion_info['avg_size'])
            metrics['winding_number'].append(Q)
            metrics['total_energy'].append(E_total)
            metrics['energy_per_skyrmion'].append(E_per_skyr)
            metrics['mz_mean'].append(mz_mean)
            metrics['mz_std'].append(mz_std)
            metrics['mz_min'].append(mz_min)
            metrics['mz_max'].append(mz_max)
            
            print(f"{step:>6} | {skyrmion_info['num_skyrmions']:>10} | "
                  f"{skyrmion_info['density']:>8.4f} | {Q:>10.4f} | "
                  f"{E_total:>12.6e} | {E_per_skyr:>10.6e} | "
                  f"{mz_mean:>8.4f} | {mz_std:>8.4f}")
    
    print(f"{'-'*110}\n")
    
    return sim.m.copy(), metrics


def analyze_metrics(metrics):
    """
    Analyze decay metrics and identify when skyrmions disappear
    """
    steps = np.array(metrics['step'])
    densities = np.array(metrics['skyrmion_density'])
    counts = np.array(metrics['skyrmion_num'])
    winding = np.array(metrics['winding_number'])
    
    print(f"\n{'='*80}")
    print(f"DECAY ANALYSIS SUMMARY")
    print(f"{'='*80}\n")
    
    # Find when density drops below threshold
    threshold_density = 0.05
    below_threshold = np.where(densities < threshold_density)[0]
    
    if len(below_threshold) > 0:
        collapse_step = steps[below_threshold[0]]
        print(f"Skyrmion COLLAPSE occurred at step: {collapse_step}")
        print(f"  (Density dropped below {threshold_density})")
    else:
        collapse_step = None
        print(f"Skyrmions PERSISTED throughout simulation (density > {threshold_density})")
    
    # Initial conditions
    print(f"\nInitial state (step {steps[0]}):")
    print(f"  Skyrmion count: {counts[0]}")
    print(f"  Skyrmion density: {densities[0]:.4f}")
    print(f"  Total winding: {winding[0]:.4f}")
    
    # Final state
    print(f"\nFinal state (step {steps[-1]}):")
    print(f"  Skyrmion count: {counts[-1]}")
    print(f"  Skyrmion density: {densities[-1]:.4f}")
    print(f"  Total winding: {winding[-1]:.4f}")
    
    # Persistence to 2000 steps
    if steps[-1] >= 2000:
        idx_2000 = np.argmin(np.abs(steps - 2000))
        print(f"\nAt step 2000:")
        print(f"  Skyrmion count: {counts[idx_2000]}")
        print(f"  Skyrmion density: {densities[idx_2000]:.4f}")
        print(f"  Total winding: {winding[idx_2000]:.4f}")
        print(f"  Persistence: {(densities[idx_2000] / densities[0] * 100):.1f}% of initial")
    
    print(f"\n{'='*80}\n")
    
    return collapse_step


def save_metrics(metrics, filename='skyrmion_decay_metrics.json'):
    """Save metrics to JSON for plotting"""
    # Convert numpy arrays to lists
    metrics_serializable = {}
    for key, value in metrics.items():
        if isinstance(value, list):
            metrics_serializable[key] = [float(v) if isinstance(v, (np.floating, np.integer)) else v for v in value]
        else:
            metrics_serializable[key] = value
    
    with open(filename, 'w') as f:
        json.dump(metrics_serializable, f, indent=2)
    
    print(f"Metrics saved to: {filename}")


if __name__ == "__main__":
    # Test with current parameters
    params = MicromagneticParams()
    
    m_final, metrics = run_decay_analysis(params, num_steps=2000, save_interval=50)
    
    collapse_step = analyze_metrics(metrics)
    
    save_metrics(metrics)
    
    print("\nNext steps:")
    print("1. If skyrmions collapse before step 2000:")
    print("   - Increase DMI (D) to stabilize cores")
    print("   - Reduce B_z to decrease positive field bias")
    print("   - Increase K_z for stronger anisotropy stabilization")
    print("\n2. If skyrmions persist:")
    print("   - Verify they are MOBILE (not just static)")
    print("   - Measure drift velocity")
    print("   - Run 5000-step transport test")
