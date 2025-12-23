"""
QUICK START: LIVE SKYRMION VISUALIZATION

Run this to see the skyrmion simulation with real-time visualization.

Features:
- Live magnetization field display (updated every N steps)
- Real-time energy evolution plot
- Skyrmion density tracking
- M_z statistics with uncertainty bands
- Status indicator showing step count and current metrics

Usage:
    python quickstart_live.py
    
Then watch the plots update as simulation progresses!
"""

from skyrmion_simulator import SkyrmionSimulator, MicromagneticParams
from skyrmion_live_view import LiveSkyrmionVisualizer
import matplotlib.pyplot as plt


def main():
    """Run simulation with live visualization."""
    
    # Create parameters (using optimized defaults)
    params = MicromagneticParams()
    
    # For faster visualization, use smaller grid
    params.grid_size = 128  # Instead of 256
    
    print("\n" + "="*80)
    print("SKYRMION MANIFOLD: LIVE VISUALIZATION")
    print("="*80)
    print(f"\nParameters:")
    print(f"  Grid:      {params.grid_size}×{params.grid_size} cells")
    print(f"  Cell size: {params.cell_size} nm")
    print(f"  Thickness: {params.thickness} nm")
    print(f"  A:         {params.A} J/m")
    print(f"  D:         {params.D} J/m²")
    print(f"  K_z:       {params.K_z} J/m³")
    print(f"  B_z:       {params.B_z} T (positive = stable skyrmions)")
    print(f"  alpha:     {params.alpha}")
    print(f"  dt:        {params.dt} s (1 ps per step)")
    
    # Create simulator
    sim = SkyrmionSimulator(params)
    
    # Create live visualizer
    # update_interval = display refreshes every N steps
    # window_size = keep last N measurements in rolling plot
    visualizer = LiveSkyrmionVisualizer(sim, update_interval=20, window_size=200)
    
    # Total simulation time
    num_steps = 2000
    
    print(f"\n  Total steps: {num_steps}")
    print(f"  Total time: {num_steps * params.dt * 1e9:.1f} ns")
    print(f"  Update interval: every 20 steps")
    print(f"  Display will refresh approximately every 0.2 ms of simulation time")
    print(f"\n" + "="*80)
    print(f"Starting simulation...")
    print(f"Close plot window to stop\n")
    
    try:
        for step in range(num_steps):
            # Execute one simulation step
            sim.step(use_euler=True)
            
            # Update visualization (happens every update_interval steps)
            visualizer.update(step)
            
            # Print progress occasionally
            if step % 200 == 0 and step > 0:
                print(f"  Step {step:4d} / {num_steps} ({100*step/num_steps:5.1f}%)")
        
        print(f"\nSimulation completed: {num_steps} steps")
    
    except KeyboardInterrupt:
        print(f"\nInterrupted at step {step}")
    
    except Exception as e:
        print(f"Error during simulation: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print(f"\nFinal state:")
        m_z = sim.m[:, :, 2]
        print(f"  Skyrmion density: {np.sum(m_z < -0.3) / (params.grid_size**2):.4f}")
        print(f"  Energy: {sim._compute_energy():.6e} J/m²")
        print(f"  M_z mean: {np.mean(m_z):+.4f}")
        print(f"  M_z std: {np.std(m_z):.4f}")
        print(f"\nKeep plot window open to inspect.")
        print(f"Close window to exit.")
        
        plt.show()


if __name__ == "__main__":
    import numpy as np
    main()
