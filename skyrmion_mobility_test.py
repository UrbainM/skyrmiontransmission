"""
SKYRMION MOBILITY DIAGNOSTIC

Measure if skyrmions are drifting/moving in space or staying static.

Key metrics:
- Center of mass position (x_com, y_com) each step
- Drift velocity (pixels per step)
- Trajectory analysis (ballistic vs random walk)
"""

import numpy as np
from skyrmion_simulator import SkyrmionSimulator, MicromagneticParams
import json


def find_skyrmion_centers(m, threshold=-0.3):
    """
    Find skyrmion center of mass
    
    Returns:
        (x_com, y_com) or None if no skyrmions detected
    """
    m_z = m[:, :, 2]
    skyrmion_mask = m_z < threshold
    
    if np.sum(skyrmion_mask) < 10:  # Too few pixels to localize
        return None
    
    y_indices, x_indices = np.where(skyrmion_mask)
    x_com = np.mean(x_indices)
    y_com = np.mean(y_indices)
    
    return x_com, y_com


def run_mobility_test(num_steps=2000, save_interval=20, grid_size=128):
    """
    Measure skyrmion mobility by tracking center of mass
    """
    params = MicromagneticParams()
    params.grid_size = grid_size
    
    sim = SkyrmionSimulator(params)
    
    trajectory = {
        'step': [],
        'x_com': [],
        'y_com': [],
        'velocity': [],  # Displacement per step
        'skyrmion_density': [],
    }
    
    print(f"\n{'='*90}")
    print(f"SKYRMION MOBILITY TEST")
    print(f"{'='*90}")
    print(f"Grid: {grid_size}×{grid_size}")
    print(f"Measurements every {save_interval} steps")
    print(f"Total steps: {num_steps}")
    print(f"{'='*90}\n")
    
    print(f"{'Step':>6} | {'X_com':>8} | {'Y_com':>8} | {'Velocity':>10} | {'Density':>8} | Status")
    print(f"{'-'*90}")
    
    prev_position = None
    
    try:
        for step in range(num_steps):
            sim.step(use_euler=True)
            
            if step % save_interval == 0:
                m = sim.m.copy()
                
                # Find skyrmion center
                center = find_skyrmion_centers(m)
                
                # Calculate skyrmion density
                m_z = m[:, :, 2]
                density = np.sum(m_z < -0.3) / (grid_size ** 2)
                
                if center is None:
                    # No skyrmions
                    x_com, y_com = grid_size/2, grid_size/2
                    velocity = np.nan
                    status = "NO SKYRMIONS"
                else:
                    x_com, y_com = center
                    
                    # Calculate velocity (pixels per step)
                    if prev_position is not None:
                        dx = x_com - prev_position[0]
                        dy = y_com - prev_position[1]
                        # Account for periodic boundary conditions
                        if abs(dx) > grid_size/2:
                            dx = grid_size - abs(dx)
                        if abs(dy) > grid_size/2:
                            dy = grid_size - abs(dy)
                        velocity = np.sqrt(dx**2 + dy**2) / save_interval
                    else:
                        velocity = 0.0
                    
                    prev_position = (x_com, y_com)
                    
                    if velocity < 0.001:
                        status = "STATIC"
                    elif velocity < 0.01:
                        status = "DRIFTING"
                    else:
                        status = "MOVING"
                
                trajectory['step'].append(step)
                trajectory['x_com'].append(x_com)
                trajectory['y_com'].append(y_com)
                trajectory['velocity'].append(velocity if not np.isnan(velocity) else 0.0)
                trajectory['skyrmion_density'].append(density)
                
                print(f"{step:>6} | {x_com:>8.1f} | {y_com:>8.1f} | {velocity:>10.5f} | "
                      f"{density:>8.4f} | {status}")
    
    except KeyboardInterrupt:
        print(f"\n\nInterrupted at step {step}")
    
    print(f"{'-'*90}\n")
    
    return trajectory


def analyze_mobility(trajectory):
    """Analyze mobility results"""
    if not trajectory['step']:
        print("No trajectory data collected!")
        return
    
    steps = np.array(trajectory['step'])
    velocities = np.array(trajectory['velocity'])
    densities = np.array(trajectory['skyrmion_density'])
    x_positions = np.array(trajectory['x_com'])
    y_positions = np.array(trajectory['y_com'])
    
    print(f"\n{'='*90}")
    print(f"MOBILITY ANALYSIS")
    print(f"{'='*90}\n")
    
    # Filter out non-zero velocities (after formation phase)
    formation_idx = np.where(densities > 0.2)[0]
    if len(formation_idx) > 0:
        stable_idx = formation_idx[0]  # Start of stable region
        velocities_stable = velocities[stable_idx:]
    else:
        velocities_stable = velocities
    
    v_mean = np.mean(velocities_stable)
    v_std = np.std(velocities_stable)
    v_max = np.max(velocities_stable)
    
    print(f"Velocity Statistics (stable phase):")
    print(f"  Mean: {v_mean:.6f} pixels/step")
    print(f"  Std:  {v_std:.6f} pixels/step")
    print(f"  Max:  {v_max:.6f} pixels/step\n")
    
    # Total displacement
    if len(x_positions) > 1:
        total_dx = x_positions[-1] - x_positions[0]
        total_dy = y_positions[-1] - y_positions[0]
        total_distance = np.sqrt(total_dx**2 + total_dy**2)
        steps_elapsed = steps[-1] - steps[0]
        avg_velocity = total_distance / (steps_elapsed / 1)  # pixels per measurement interval
        
        print(f"Total Displacement:")
        print(f"  Δx: {total_dx:+.1f} pixels")
        print(f"  Δy: {total_dy:+.1f} pixels")
        print(f"  Total distance: {total_distance:.1f} pixels")
        print(f"  Steps elapsed: {steps_elapsed}")
        print(f"  Avg velocity: {avg_velocity:.6f} pixels/step\n")
    
    # Skyrmion density
    print(f"Skyrmion Density:")
    print(f"  Mean: {np.mean(densities):.4f}")
    print(f"  Std:  {np.std(densities):.4f}")
    print(f"  Min:  {np.min(densities):.4f}")
    print(f"  Max:  {np.max(densities):.4f}\n")
    
    # Classification
    print(f"{'='*90}")
    if v_mean < 0.001:
        print(f"CLASSIFICATION: STATIC SKYRMIONS")
        print(f"  Velocity: {v_mean:.6f} pixels/step (essentially zero)")
        print(f"\nRECOMMENDATION:")
        print(f"  Skyrmions are not moving naturally.")
        print(f"  Add external driving mechanism:")
        print(f"    - AC magnetic field: B_z(t) = B_0 + B_1*cos(ωt)")
        print(f"    - Spin-polarized current: j(y) = j_0*sin(πy/L)")
        print(f"    - Temperature gradient: ∇T")
    elif v_mean < 0.01:
        print(f"CLASSIFICATION: WEAKLY MOBILE SKYRMIONS")
        print(f"  Velocity: {v_mean:.6f} pixels/step")
        print(f"  Drift distance over 2000 steps: {v_mean * 2000:.0f} pixels")
        print(f"\nRECOMMENDATION:")
        print(f"  Skyrmions have weak natural drift.")
        print(f"  Enhance with modest driving mechanism.")
    else:
        print(f"CLASSIFICATION: STRONGLY MOBILE SKYRMIONS")
        print(f"  Velocity: {v_mean:.6f} pixels/step")
        print(f"  Drift distance over 2000 steps: {v_mean * 2000:.0f} pixels")
        print(f"\nRECOMMENDATION:")
        print(f"  Skyrmions have strong natural motion!")
        print(f"  Ready for information encoding with potential landscape.")
    
    print(f"{'='*90}\n")
    
    return v_mean


def save_trajectory(trajectory, filename='skyrmion_trajectory.json'):
    """Save trajectory for plotting"""
    trajectory_serializable = {}
    for key, value in trajectory.items():
        trajectory_serializable[key] = [float(v) for v in value]
    
    with open(filename, 'w') as f:
        json.dump(trajectory_serializable, f, indent=2)
    
    print(f"Trajectory saved to: {filename}\n")


if __name__ == "__main__":
    print("Starting skyrmion mobility test...")
    print("(This measures if skyrmions are moving or static)\n")
    
    trajectory = run_mobility_test(num_steps=2000, save_interval=20, grid_size=128)
    
    v_mean = analyze_mobility(trajectory)
    
    save_trajectory(trajectory)
    
    print("\nNext steps based on mobility result:")
    print("1. If STATIC: Design and implement driving mechanism")
    print("2. If MOBILE: Design information encoding scheme")
    print("3. Test long-distance transport with encoded data")
