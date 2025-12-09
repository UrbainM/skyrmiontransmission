"""
FAST SKYRMION DECAY DIAGNOSTIC (128x128 GRID)

Purpose: Quick diagnostics to 5000 steps to determine actual decay point
Uses 128x128 grid (4x faster than 256x256)

Key metrics every 100 steps to reach 5000 step mark in ~10 minutes
"""

import numpy as np
from skyrmion_simulator import SkyrmionSimulator, MicromagneticParams
import json
from pathlib import Path


def identify_skyrmions_quick(m_z, threshold_mz=-0.3):
    """Fast skyrmion identification"""
    skyrmion_mask = m_z < threshold_mz
    count = np.sum(skyrmion_mask)
    density = count / (m_z.shape[0] * m_z.shape[1])
    return count, density


def run_fast_decay_analysis(num_steps=5000, save_interval=100, grid_size=128):
    """
    Fast decay analysis on smaller grid
    """
    # Create params with smaller grid
    params = MicromagneticParams()
    params.grid_size = grid_size
    params.num_steps = num_steps
    
    sim = SkyrmionSimulator(params)
    
    metrics = {
        'step': [],
        'skyrmion_pixels': [],
        'skyrmion_density': [],
        'mz_mean': [],
        'mz_std': [],
        'mz_min': [],
        'mz_max': [],
        'energy': [],
    }
    
    print(f"\n{'='*90}")
    print(f"FAST SKYRMION DECAY DIAGNOSTIC (128×128 grid, 5000 steps)")
    print(f"{'='*90}")
    print(f"Parameters:")
    print(f"  Grid: {grid_size}×{grid_size} = {grid_size**2} cells")
    print(f"  A = {params.A} J/m")
    print(f"  D = {params.D} J/m²")
    print(f"  K_z = {params.K_z} J/m³")
    print(f"  B_z = {params.B_z} T")
    print(f"\nSave interval: every {save_interval} steps")
    print(f"Target: {num_steps} steps total")
    print(f"{'='*90}\n")
    
    print(f"{'Step':>6} | {'Pix':>6} | {'Density':>8} | {'Mz_mean':>8} | {'Mz_std':>8} | "
          f"{'Energy':>12} | Status")
    print(f"{'-'*90}")
    
    step_count = 0
    for step in range(num_steps):
        try:
            sim.step(use_euler=True)
            step_count += 1
            
            if step % save_interval == 0:
                m = sim.m.copy()
                m_z = m[:, :, 2]
                
                pix, dens = identify_skyrmions_quick(m_z)
                mz_mean = np.mean(m_z)
                mz_std = np.std(m_z)
                mz_min = np.min(m_z)
                mz_max = np.max(m_z)
                energy = sim._compute_energy()
                
                metrics['step'].append(step)
                metrics['skyrmion_pixels'].append(pix)
                metrics['skyrmion_density'].append(dens)
                metrics['mz_mean'].append(mz_mean)
                metrics['mz_std'].append(mz_std)
                metrics['mz_min'].append(mz_min)
                metrics['mz_max'].append(mz_max)
                metrics['energy'].append(energy)
                
                # Determine status
                if dens < 0.01:
                    status = "COLLAPSED"
                elif dens < 0.1:
                    status = "DECAYING"
                elif dens > 0.3:
                    status = "ROBUST"
                else:
                    status = "STABLE"
                
                print(f"{step:>6} | {pix:>6} | {dens:>8.4f} | {mz_mean:>8.4f} | {mz_std:>8.4f} | "
                      f"{energy:>12.6e} | {status}")
        
        except KeyboardInterrupt:
            print(f"\n\nInterrupted at step {step_count}")
            break
        except Exception as e:
            print(f"\nError at step {step}: {e}")
            break
    
    print(f"{'-'*90}")
    print(f"Total steps completed: {step_count} / {num_steps}\n")
    
    return sim.m.copy(), metrics


def analyze_fast_metrics(metrics):
    """Quick analysis of decay metrics"""
    if not metrics['step']:
        print("No metrics collected!")
        return
    
    steps = np.array(metrics['step'])
    densities = np.array(metrics['skyrmion_density'])
    energies = np.array(metrics['energy'])
    mz_means = np.array(metrics['mz_mean'])
    
    print(f"\n{'='*90}")
    print(f"FAST ANALYSIS SUMMARY")
    print(f"{'='*90}\n")
    
    # Initial state
    print(f"Initial state (step {steps[0]}):")
    print(f"  Skyrmion density: {densities[0]:.4f}")
    print(f"  Energy: {energies[0]:.6e} J/m²")
    print(f"  M_z mean: {mz_means[0]:.4f}\n")
    
    # Final state
    print(f"Final state (step {steps[-1]}):")
    print(f"  Skyrmion density: {densities[-1]:.4f}")
    print(f"  Energy: {energies[-1]:.6e} J/m²")
    print(f"  M_z mean: {mz_means[-1]:.4f}\n")
    
    # Collapse point
    threshold = 0.05
    below_threshold = np.where(densities < threshold)[0]
    if len(below_threshold) > 0:
        collapse_idx = below_threshold[0]
        collapse_step = steps[collapse_idx]
        print(f"COLLAPSE EVENT: Step {collapse_step}")
        print(f"  (Density dropped below {threshold})\n")
    else:
        print(f"NO COLLAPSE: Density remained above {threshold} throughout\n")
    
    # Stability
    if len(energies) > 10:
        energy_late = energies[-10:]
        energy_early = energies[:10]
        energy_change = np.mean(energy_late) - np.mean(energy_early)
        print(f"Energy change (first vs last):")
        print(f"  Early avg: {np.mean(energy_early):.6e} J/m²")
        print(f"  Late avg: {np.mean(energy_late):.6e} J/m²")
        print(f"  Change: {energy_change:+.6e} J/m²")
        print(f"  Status: {'STABLE' if abs(energy_change) < 1e-3 else 'DRIFTING'}\n")
    
    print(f"{'='*90}\n")
    
    return steps, densities


def save_fast_metrics(metrics, filename='fast_decay_metrics.json'):
    """Save metrics"""
    metrics_serializable = {}
    for key, value in metrics.items():
        if isinstance(value, list):
            metrics_serializable[key] = [float(v) if isinstance(v, (np.floating, np.integer)) else v for v in value]
        else:
            metrics_serializable[key] = value
    
    with open(filename, 'w') as f:
        json.dump(metrics_serializable, f, indent=2)
    
    print(f"Metrics saved to: {filename}\n")


if __name__ == "__main__":
    print("Starting fast skyrmion decay diagnostic...")
    print("(128×128 grid, 5000 steps, ~10-15 minutes)\n")
    
    m_final, metrics = run_fast_decay_analysis(num_steps=5000, save_interval=100, grid_size=128)
    
    result = analyze_fast_metrics(metrics)
    if result is not None:
        steps, densities = result
    else:
        steps, densities = [], []
    
    save_fast_metrics(metrics)
    
    print("\n" + "="*90)
    print("RECOMMENDATIONS")
    print("="*90 + "\n")
    
    if len(densities) > 0:
        if densities[-1] > 0.2:
            print("[GOOD] Skyrmions are PERSISTENT!")
            print("Next step: Check if skyrmions are MOBILE (drifting/moving)")
            print("\nAdd to next test:")
            print("  - Track skyrmion center of mass position")
            print("  - Compute drift velocity")
            print("  - Consider adding AC field for intentional driving\n")
        elif densities[-1] > 0.05:
            print("[PARTIAL] Skyrmions persist but DECAYING")
            print("Next step: Increase stabilization")
            print("\nTry:")
            print("  - Increase DMI: D = 5e-3 → 8e-3 J/m²")
            print("  - Increase anisotropy: K_z = 0.8e6 → 1.2e6 J/m³")
            print("  - Reduce field: B_z = 0.010 → 0.005 T\n")
        else:
            print("[BAD] Skyrmions COLLAPSED")
            print("Current parameters are unstable!")
            print("\nImmediately try:")
            print("  - Increase DMI significantly: D = 8e-3 J/m²")
            print("  - Increase anisotropy: K_z = 1.5e6 J/m³")
            print("  - Reduce field to near zero or negative: B_z = 0.0 T\n")
