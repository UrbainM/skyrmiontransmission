"""
LIVE SKYRMION VISUALIZATION DURING SIMULATION

Display magnetization and metrics in real-time as simulation runs,
allowing diagnosis of skyrmion behavior concurrent with computation.

Usage:
    sim = SkyrmionSimulator(params)
    visualizer = LiveSkyrmionVisualizer(sim, update_interval=50)
    
    for step in range(num_steps):
        sim.step()
        visualizer.update(step)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
import matplotlib.gridspec as gridspec
from collections import deque
from pathlib import Path


class LiveSkyrmionVisualizer:
    """
    Real-time visualization of skyrmion simulation during execution.
    
    Displays:
    - m_z field (color map)
    - Energy evolution (line plot)
    - Skyrmion density (line plot)
    - M_z statistics (text)
    """
    
    def __init__(self, simulator, update_interval=50, window_size=200):
        """
        Initialize live visualizer.
        
        Args:
            simulator: SkyrmionSimulator instance
            update_interval: Update display every N steps
            window_size: Keep last N measurements for scrolling plots
        """
        self.sim = simulator
        self.update_interval = update_interval
        self.window_size = window_size
        
        # Data buffers (rolling windows)
        self.steps_buffer = deque(maxlen=window_size)
        self.energy_buffer = deque(maxlen=window_size)
        self.density_buffer = deque(maxlen=window_size)
        self.mz_mean_buffer = deque(maxlen=window_size)
        self.mz_std_buffer = deque(maxlen=window_size)
        
        # Setup figure
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.suptitle('Real-Time Skyrmion Simulation', fontsize=16, weight='bold')
        
        gs = gridspec.GridSpec(3, 2, figure=self.fig, hspace=0.35, wspace=0.3)
        
        # Magnetization field (left, top)
        self.ax_m_z = self.fig.add_subplot(gs[0:2, 0])
        self.im_m_z = self.ax_m_z.imshow(
            np.ones((simulator.N, simulator.N)), 
            cmap='RdBu_r', 
            vmin=-1, vmax=1,
            origin='lower'
        )
        self.ax_m_z.set_title('Out-of-Plane Magnetization m_z(x,y)')
        self.ax_m_z.set_xlabel('X (grid cells)')
        self.ax_m_z.set_ylabel('Y (grid cells)')
        cbar = plt.colorbar(self.im_m_z, ax=self.ax_m_z, label='m_z')
        
        # Energy plot (right, top)
        self.ax_energy = self.fig.add_subplot(gs[0, 1])
        self.line_energy, = self.ax_energy.plot([], [], 'b-', linewidth=2, label='Energy')
        self.ax_energy.set_xlabel('Step')
        self.ax_energy.set_ylabel('Energy (J/m²)')
        self.ax_energy.set_title('Energy Evolution')
        self.ax_energy.grid(True, alpha=0.3)
        self.ax_energy.legend(loc='upper left')
        self.energy_text = self.ax_energy.text(0.98, 0.95, '', 
                                               transform=self.ax_energy.transAxes,
                                               ha='right', va='top',
                                               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                                               fontfamily='monospace', fontsize=9)
        
        # Skyrmion density plot (right, middle)
        self.ax_density = self.fig.add_subplot(gs[1, 1])
        self.line_density, = self.ax_density.plot([], [], 'g-', linewidth=2, label='Skyrmion Density')
        self.ax_density.set_xlabel('Step')
        self.ax_density.set_ylabel('Density (fraction)')
        self.ax_density.set_title('Skyrmion Density Over Time')
        self.ax_density.set_ylim(-0.05, 0.5)
        self.ax_density.grid(True, alpha=0.3)
        self.ax_density.legend(loc='upper left')
        
        # M_z statistics (bottom)
        self.ax_mz_stats = self.fig.add_subplot(gs[2, :])
        self.line_mz_mean, = self.ax_mz_stats.plot([], [], 'b-', linewidth=2, label='M_z mean', alpha=0.7)
        self.line_mz_plus_std, = self.ax_mz_stats.plot([], [], 'b--', linewidth=1, label='±1 std', alpha=0.5)
        self.line_mz_minus_std, = self.ax_mz_stats.plot([], [], 'b--', linewidth=1, alpha=0.5)
        self.ax_mz_stats.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
        self.ax_mz_stats.set_xlabel('Step')
        self.ax_mz_stats.set_ylabel('M_z')
        self.ax_mz_stats.set_title('M_z Statistics (Mean ± Std Dev)')
        self.ax_mz_stats.set_ylim(-1.1, 1.1)
        self.ax_mz_stats.grid(True, alpha=0.3)
        self.ax_mz_stats.legend(loc='upper left', ncol=3)
        
        # Status text (bottom right)
        self.status_text = self.fig.text(0.99, 0.01, '', 
                                         ha='right', va='bottom',
                                         fontfamily='monospace', fontsize=10,
                                         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
        
        self.step_counter = 0
        self.last_update = 0
        
        plt.ion()  # Turn on interactive mode
    
    def update(self, step):
        """
        Update visualization with current simulation state.
        
        Call this every simulation step (or every N steps).
        
        Args:
            step: Current simulation step number
        """
        self.step_counter = step
        
        # Only update display every update_interval steps
        if step % self.update_interval != 0 and step > 0:
            return
        
        # Get current state
        m = self.sim.m.copy()
        m_z = m[:, :, 2]
        
        # Compute metrics
        energy = self.sim._compute_energy()
        density = np.sum(m_z < -0.3) / (self.sim.N ** 2)
        mz_mean = np.mean(m_z)
        mz_std = np.std(m_z)
        
        # Add to buffers
        self.steps_buffer.append(step)
        self.energy_buffer.append(energy)
        self.density_buffer.append(density)
        self.mz_mean_buffer.append(mz_mean)
        self.mz_std_buffer.append(mz_std)
        
        # Update magnetization field image
        self.im_m_z.set_array(m_z)
        
        # Update energy plot
        steps_array = np.array(self.steps_buffer)
        energy_array = np.array(self.energy_buffer)
        self.line_energy.set_data(steps_array, energy_array)
        self.ax_energy.set_xlim(max(0, steps_array[0] - 100), steps_array[-1] + 10)
        self.ax_energy.set_ylim(np.min(energy_array) * 0.9, np.max(energy_array) * 1.1)
        
        # Update energy text
        energy_text = f"E = {energy:.6e} J/m²"
        self.energy_text.set_text(energy_text)
        
        # Update density plot
        density_array = np.array(self.density_buffer)
        self.line_density.set_data(steps_array, density_array)
        self.ax_density.set_xlim(max(0, steps_array[0] - 100), steps_array[-1] + 10)
        
        # Update M_z statistics
        mz_mean_array = np.array(self.mz_mean_buffer)
        mz_std_array = np.array(self.mz_std_buffer)
        
        self.line_mz_mean.set_data(steps_array, mz_mean_array)
        self.line_mz_plus_std.set_data(steps_array, mz_mean_array + mz_std_array)
        self.line_mz_minus_std.set_data(steps_array, mz_mean_array - mz_std_array)
        self.ax_mz_stats.set_xlim(max(0, steps_array[0] - 100), steps_array[-1] + 10)
        
        # Update status text
        status_lines = [
            f"Step: {step:6d}",
            f"E:    {energy:+.4e} J/m²",
            f"Dens: {density:6.4f}",
            f"Mz:   {mz_mean:+.4f} ± {mz_std:.4f}",
        ]
        self.status_text.set_text('\n'.join(status_lines))
        
        # Redraw
        self.fig.canvas.draw_idle()
        plt.pause(0.001)  # Small pause for display update
    
    def close(self):
        """Close the visualization window."""
        plt.close(self.fig)


def run_simulation_with_visualization(params=None, num_steps=5000, update_interval=50):
    """
    Run simulation with concurrent live visualization.
    
    Args:
        params: MicromagneticParams (or None for defaults)
        num_steps: Total simulation steps
        update_interval: Update display every N steps
    """
    from skyrmion_simulator import SkyrmionSimulator, MicromagneticParams
    
    if params is None:
        params = MicromagneticParams()
    
    sim = SkyrmionSimulator(params)
    visualizer = LiveSkyrmionVisualizer(sim, update_interval=update_interval)
    
    print(f"\n{'='*80}")
    print(f"LIVE SKYRMION VISUALIZATION")
    print(f"{'='*80}")
    print(f"Simulation: {num_steps} steps")
    print(f"Update interval: Every {update_interval} steps")
    print(f"Grid size: {params.grid_size}×{params.grid_size}")
    print(f"Parameters: A={params.A}, D={params.D}, K_z={params.K_z}, B_z={params.B_z}")
    print(f"\nClose the plot window to stop simulation")
    print(f"Or Ctrl+C in terminal")
    print(f"{'='*80}\n")
    
    try:
        for step in range(num_steps):
            sim.step(use_euler=True)
            visualizer.update(step)
            
            if step % 500 == 0 and step > 0:
                print(f"Completed {step} / {num_steps} steps")
    
    except KeyboardInterrupt:
        print(f"\nInterrupted at step {step}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"\nSimulation completed: {step} steps")
        print("Keep plot window open to inspect final state")
        print("Close window to exit")
        
        # Keep window open
        plt.show()
        visualizer.close()


if __name__ == "__main__":
    # Run with custom parameters if desired
    from skyrmion_simulator import MicromagneticParams
    
    params = MicromagneticParams()
    params.grid_size = 128  # Use smaller grid for faster visualization
    
    run_simulation_with_visualization(params=params, num_steps=2000, update_interval=20)
