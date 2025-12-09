#!/usr/bin/env python3
"""Quick test of magnetization evolution."""

from skyrmion_simulator import SkyrmionSimulator, MicromagneticParams
import numpy as np

# Create small simulation
params = MicromagneticParams(grid_size=64, num_steps=50)
sim = SkyrmionSimulator(params)

print(f"Initial state:")
print(f"  m_z range: [{sim.m[:,:,2].min():.4f}, {sim.m[:,:,2].max():.4f}]")
print(f"  m norm range: [{np.linalg.norm(sim.m, axis=2).min():.6f}, {np.linalg.norm(sim.m, axis=2).max():.6f}]")

e1 = sim._compute_energy()
print(f"  Energy: {e1:.6f} J/m²\n")

print("Running 10 steps:")
for step in range(10):
    sim.step()
    sim._normalize_magnetization()
    e = sim._compute_energy()
    m_z_min, m_z_max = sim.m[:,:,2].min(), sim.m[:,:,2].max()
    print(f"  Step {step+1:2d}: E={e:10.6f} J/m², m_z=[{m_z_min:.4f}, {m_z_max:.4f}]")

print("\nFinal statistics:")
print(f"  m_z mean: {sim.m[:,:,2].mean():.4f}")
print(f"  m_z std:  {sim.m[:,:,2].std():.4f}")
print(f"  Skyrmion-like features emerging: {'Yes' if (sim.m[:,:,2].min() < 0.5 and sim.m[:,:,2].max() > 0.5) else 'No'}")
