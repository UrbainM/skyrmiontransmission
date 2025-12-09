#!/usr/bin/env python3
"""Simplified quickstart test - skip fancy printing, focus on simulation."""

import os
import sys
import numpy as np
from pathlib import Path

# Ensure UTF-8 encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from skyrmion_simulator import SkyrmionSimulator, MicromagneticParams

def main():
    print("Starting simplified quickstart...\n")
    
    # Configuration
    print("Configuring simulation...")
    params = MicromagneticParams(
        grid_size=128,
        num_steps=5000,  # Reduced from 15000 for faster testing
        cell_size=1.0,
        thickness=10.0,
        K_z=0.8e6,
        B_z=-0.01,
        alpha=0.3,
        D=4e-3,
        A=15e-12,
    )
    
    print(f"  Grid: {params.grid_size}×{params.grid_size}")
    print(f"  Steps: {params.num_steps}")
    print(f"  Cell size: {params.cell_size} nm")
    print(f"  Thickness: {params.thickness} nm")
    print(f"  K_z: {params.K_z:.2e} J/m³")
    print(f"  B_z: {params.B_z} T")
    print(f"  D: {params.D} J/m²")
    print()
    
    # Create simulator
    print("Initializing simulator...")
    sim = SkyrmionSimulator(params)
    print(f"  Initial energy: {sim._compute_energy():.6f} J/m²")
    print(f"  Initial m_z range: [{sim.m[:,:,2].min():.4f}, {sim.m[:,:,2].max():.4f}]")
    print()
    
    # Run simulation
    print("Running simulation...")
    try:
        sim.run()
        print("✓ Simulation completed successfully!")
    except Exception as e:
        print(f"✗ Simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Print results
    print(f"\nResults:")
    print(f"  Final energy: {sim.energy_history[-1]:.6f} J/m²")
    print(f"  Final m_z range: [{sim.m[:,:,2].min():.4f}, {sim.m[:,:,2].max():.4f}]")
    print(f"  Final m_z mean: {sim.m[:,:,2].mean():.4f}")
    print(f"  Final m_z std: {sim.m[:,:,2].std():.4f}")
    print(f"  Skyrmion feature strength: {1 - sim.m[:,:,2].mean():.4f}")
    print()
    
    # Save results
    print("Saving results...")
    output_dir = Path("outputs/skyrmion_results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save energy history
    np.save(output_dir / "energy_history.npy", sim.energy_history)
    print(f"  ✓ Energy history saved")
    
    # Save final magnetization
    np.save(output_dir / "m_z_final.npy", sim.m[:,:,2])
    print(f"  ✓ Magnetization field saved")
    
    # Save parameters
    import json
    from dataclasses import asdict
    with open(output_dir / "parameters.json", "w") as f:
        json.dump(asdict(params), f, indent=2)
    print(f"  ✓ Parameters saved")
    
    print("\n✓ All done!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
