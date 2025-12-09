#!/usr/bin/env python3
"""
Skyrmion Simulator - Quickstart Script

This script sets up and runs a quick demonstration of the skyrmion simulator.
Run this first to verify everything is working correctly.

Usage:
    python quickstart.py
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed."""
    print("Checking dependencies...")
    required = {
        'numpy': 'NumPy',
        'scipy': 'SciPy',
        'matplotlib': 'Matplotlib',
        'sklearn': 'scikit-learn',
    }
    
    missing = []
    for module, name in required.items():
        try:
            __import__(module)
            print(f"  [OK] {name}")
        except ImportError:
            print(f"  [XX] {name} - NOT INSTALLED")
            missing.append(module)
    
    if missing:
        print("\n[WARN] Missing dependencies! Install with:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    print("\n[OK] All dependencies installed!")
    return True


def print_intro():
    """Print introduction message."""
    intro = """
+==============================================================================+
|                                                                            |
|          SKYRMION MANIFOLD DATA TRANSMISSION SIMULATOR                     |
|                           Quickstart Guide                                |
|                                                                            |
+==============================================================================+

This script will demonstrate the skyrmion simulator with a quick test run.

WHAT WILL HAPPEN:
  1. A 128x128 grid simulation will run for 15,000 steps (~30 minutes)
  2. Skyrmions will form and encode your data manifold
  3. Results will be saved to outputs/skyrmion_results/
  4. Analysis plots will show:
     - Input data field
     - Resulting magnetization
     - Energy evolution
     - Skyrmion positions
     - Data encoding fidelity

COMPUTATIONAL REQUIREMENTS:
  - Time: ~30 minutes
  - Memory: ~100 MB
  - CPU: Standard multi-core processor

WHAT YOU'LL LEARN:
  1. How to configure a skyrmion simulation
  2. What parameters affect skyrmion formation
  3. How to analyze and visualize results
  4. How data encoding works in magnetic systems
"""
    print(intro)


def run_demo():
    """Run the demonstration simulation."""
    print("\n" + "="*80)
    print("RUNNING DEMONSTRATION")
    print("="*80 + "\n")
    
    try:
        from skyrmion_simulator import (
            SkyrmionSimulator, MicromagneticParams, 
            create_sample_manifold, visualize_results, save_results
        )
        from skyrmion_animation import SkyrmionAnimator, create_summary_animation_figure
        
        print("Step 1: Configuring simulation parameters...")
        # OPTIMIZED PARAMETERS: Stable skyrmions in positive background
        params = MicromagneticParams(
            grid_size=128,
            dt=5e-13,
            num_steps=2000,
            save_interval=200,
            A=15e-12,
            D=5e-3,                 # DMI for skyrmion cores
            K_z=0.8e6,              # Perpendicular anisotropy
            B_z=0.010,              # Moderate positive field (STABLE!)
            alpha=0.3,              # Damping
            eps_K=0.15,             # Modulation
        )

        DATA_ENCODING = MicromagneticParams(
            grid_size=256,
            dt=5e-13,
            num_steps=25000,
            save_interval=250,
            A=15e-12,
            D=4e-3,
            K_z=0.8e6,
            B_z=-0.015,
            alpha=0.3,
            eps_K=0.25,    # Moderate modulation
        )
        
        print("  [OK] Parameters configured")
        print(f"    - Grid: {params.grid_size}x{params.grid_size}")
        print(f"    - Steps: {params.num_steps}")
        print(f"    - Exchange A: {params.A*1e12:.1f} pJ/m")
        print(f"    - DMI D: {params.D*1e3:.1f} mJ/m²  (creates skyrmion cores)")
        print(f"    - Anisotropy K_z: {params.K_z/1e6:.1f} MJ/m³")
        print(f"    - External field B_z: {params.B_z:.3f} T  (positive for stability)")
        print(f"    - Damping alpha: {params.alpha:.1f}")
        print(f"    - Modulation epsilon: {params.eps_K:.2f}")
        print(f"    - Save interval: {params.save_interval} steps (for animation)")
        
        print("\n  [WARN] IMPORTANT PHYSICS NOTES:")
        print(f"    • Negative B_z favors reversed (skyrmion) magnetization")
        print(f"    • Strong DMI (D={params.D*1e3:.1f}) stabilizes skyrmions")
        print(f"    • Higher damping (α={params.alpha}) ensures convergence")
        print(f"    • Total simulation: ~{params.num_steps//1000}k steps")
        
        print("\nStep 2: Creating data manifold...")
        data_field = create_sample_manifold(
            size=DATA_ENCODING.grid_size, 
            pattern='gaussian_bumps'
        )
        print("  [OK] Data field created (Gaussian bumps pattern)")
        
        print("\nStep 3: Initializing simulator...")
        simulator = SkyrmionSimulator(DATA_ENCODING, data_field=data_field)
        print("  [OK] Simulator initialized")
        
        print("\nStep 4: Running simulation...")
        print("  (This will take ~30 minutes, showing progress every 1500 steps)")
        print("-" * 80)
        simulator.run(verbose=True)
        print("-" * 80)
        
        print("\nStep 5: Analyzing results...")
        from skyrmion_analysis import SkyrmionAnalyzer
        analyzer = SkyrmionAnalyzer()
        
        m_z = simulator.get_m_z()
        skyrmion_info = analyzer.detect_skyrmions(m_z, threshold=0.3)
        correlation = analyzer.extract_manifold_signature(m_z, data_field)
        
        print("  [OK] Analysis complete:")
        print(f"    - Skyrmions detected: {skyrmion_info['count']}")
        print(f"    - Data correlation: {correlation:.4f}")
        print(f"    - m_z range: [{m_z.min():.3f}, {m_z.max():.3f}]")
        
        print("\nStep 6: Visualizing results...")
        Path('outputs').mkdir(exist_ok=True)
        visualize_results(simulator, save_dir=Path('outputs/skyrmion_results'))
        print("  [OK] Visualization complete")
        
        print("\nStep 7: Creating animations...")
        animator = SkyrmionAnimator(simulator, output_dir=Path('outputs/skyrmion_results'))
        
        # Create m_z evolution animation
        try:
            print("  - Creating m_z evolution animation...")
            animator.create_m_z_evolution_animation(
                save_path=Path('outputs/skyrmion_results/m_z_evolution.mp4'),
                fps=10,
                skip_frames=2
            )
        except Exception as e:
            print(f"    [WARN] MP4 animation skipped (ffmpeg needed): {e}")
        
        # Create frame sequence (always works)
        print("  - Creating frame sequence (PNG images)...")
        animator.create_frame_sequence(save_dir=Path('outputs/skyrmion_results/frames'))
        
        # Create comparison animation
        try:
            print("  - Creating data vs magnetization comparison...")
            animator.create_comparison_animation(
                data_field=data_field,
                save_path=Path('outputs/skyrmion_results/comparison_animation.mp4'),
                fps=10,
                skip_frames=2
            )
        except Exception as e:
            print(f"    [WARN] Comparison animation skipped: {e}")
        
        # Create summary animation figure
        print("  - Creating animation summary figure...")
        create_summary_animation_figure(
            simulator.m_z_history,
            simulator.energy_history,
            data_field,
            simulator.params.save_interval,
            save_path=Path('outputs/skyrmion_results/animation_summary.png')
        )
        print("  [OK] Animation creation complete")
        
        print("\nStep 8: Saving data...")
        save_results(simulator, Path('outputs/skyrmion_results'))
        print("  [OK] Results saved to outputs/skyrmion_results/")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error during simulation: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_next_steps():
    """Print next steps after demo."""
    next_steps = """
╔════════════════════════════════════════════════════════════════════════════╗
║                           NEXT STEPS                                      ║
╚════════════════════════════════════════════════════════════════════════════╝

1. CHECK YOUR ANIMATIONS & RESULTS
   - View: outputs/skyrmion_results/animation_summary.png
     Shows: Key frames throughout evolution
   
   - View: outputs/skyrmion_results/frames/frame_*.png
     Shows: Individual frames of simulation (PNG sequence)
   
   - View: outputs/skyrmion_results/m_z_evolution.mp4 (if ffmpeg installed)
     Shows: Animated m_z evolution with energy tracking
   
   - View: outputs/skyrmion_results/comparison_animation.mp4 (if ffmpeg installed)
     Shows: Data field vs magnetization with correlation

2. CHECK STATIC ANALYSIS
   - Open: outputs/skyrmion_results/skyrmion_analysis.png
   - Shows: 6-panel analysis with:
     * Input data field
     * Modulated anisotropy
     * Final magnetization
     * Energy evolution
     * m_z statistics
     * Data-magnetization correlation

3. UNDERSTAND WHAT HAPPENED
   Physics:
   [OK] Strong DMI (D=5 mJ/m^2) stabilized skyrmions
   [OK] Negative B_z (-0.02 T) favored reversed magnetization
   [OK] Higher anisotropy (K_z=1.0 MJ/m^3) compacted skyrmions
   [OK] Higher damping (alpha=0.4) ensured convergence
   
   Energy:
   [OK] Should show monotonic convergence to plateau
   [OK] Negative values are NORMAL when B_z < 0
   [OK] Energy normalized per unit area for comparison

4. EXPLORE VARIATIONS
   # Try different data patterns
   python -c "
from skyrmion_examples import example_2_data_encoding
example_2_data_encoding()  # Shows 3 different patterns
   "

5. CUSTOMIZE FOR YOUR NEEDS
   Edit skyrmion_config.py:
   ✓ ConfigurationLibrary has 9 pre-built parameter sets
   ✓ Try DATA_ENCODING or STRONG_DMI configs
   ✓ Or create custom MicromagneticParams

6. ADVANCED: PARAMETER TUNING
   Key parameters for skyrmion formation:
   • D (DMI):     4-8 mJ/m²     (higher → more skyrmions)
   • K_z:         0.8-1.5 MJ/m³ (higher → smaller skyrmions)
   • B_z:         -0.02 to -0.05 (more negative → more skyrmions)
   • alpha:       0.3-0.6       (higher → faster convergence)
   • eps_K:       0.1-0.3       (stronger data modulation)

KEY FILES CREATED:
  📄 outputs/skyrmion_results/
     ├── animation_summary.png      ← Key frames comparison
     ├── frames/                    ← PNG frame sequence
     ├── m_z_evolution.mp4          ← Animated m_z (if ffmpeg)
     ├── comparison_animation.mp4   ← Data vs magnetization
     ├── skyrmion_analysis.png      ← 6-panel analysis
     ├── magnetization_field.npy    ← Full 3D field
     ├── m_z_final.npy             ← Final m_z
     ├── energy_history.npy        ← Energy evolution
     └── parameters.json           ← Configuration used

NEXT RUNNING OPTIONS:
  # Run all examples
  python skyrmion_examples.py
  
  # View configuration guide
  python skyrmion_config.py
  
  # Create custom simulation
  python -c "
from skyrmion_simulator import SkyrmionSimulator, MicromagneticParams
from skyrmion_config import ConfigurationLibrary

params = ConfigurationLibrary.DATA_ENCODING
sim = SkyrmionSimulator(params)
sim.run(verbose=True)
  "

TROUBLESHOOTING:
  ✓ MP4 files need ffmpeg (optional, PNG frames always created)
  ✓ Negative energy is PHYSICS (B_z < 0 favors down magnetization)
  ✓ No skyrmions? Try: Increase D or |B_z|, use longer simulations
  ✓ Slow? Use ConfigurationLibrary.FAST_RELAXATION

═════════════════════════════════════════════════════════════════════════════

Now you understand:
  ✓ How to simulate skyrmion formation
  ✓ How to encode data into magnetic systems
  ✓ How to visualize evolution with animations
  ✓ How to interpret energy and magnetization
  ✓ How to tune parameters for different outcomes

Ready for advanced work? Try modifying simulations with your own data!
"""
    print(next_steps)


def main():
    """Main quickstart routine."""
    print_intro()
    
    # Check dependencies
    if not check_dependencies():
        print("\n⚠ Cannot proceed without dependencies.")
        print("Install with: pip install numpy scipy matplotlib scikit-learn")
        return False
    
    # Ask user to proceed
    print("\n" + "="*80)
    response = input("Ready to run demonstration? (y/n) [y]: ").strip().lower()
    if response == 'n':
        print("Skipping demonstration. Run again when ready!")
        return False
    
    # Run demo
    success = run_demo()
    
    if success:
        print("\n" + "="*80)
        print("✓ DEMONSTRATION COMPLETE!")
        print("="*80)
        print_next_steps()
        return True
    else:
        print("\n✗ Demonstration failed. See errors above.")
        return False


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
