"""
Advanced Skyrmion Simulation Examples

Demonstrates various use cases:
1. Basic skyrmion creation and evolution
2. Data encoding with different manifold patterns
3. Parameter sensitivity analysis
4. Skyrmion dynamics and annihilation
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from skyrmion_simulator import (
    SkyrmionSimulator, MicromagneticParams, create_sample_manifold
)
from skyrmion_analysis import (
    SkyrmionAnalyzer, DataEncodingDecoder, 
    plot_skyrmion_detection, plot_energy_landscape
)


def example_1_basic_skyrmion_creation():
    """
    Example 1: Create and visualize basic skyrmion formation.
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Skyrmion Creation")
    print("="*70)
    
    # Parameters optimized for skyrmion formation
    params = MicromagneticParams(
        grid_size=128,
        dt=1e-12,
        num_steps=20000,
        save_interval=200,
        A=15e-12,
        D=4e-3,
        K_z=0.8e6,
        B_z=-0.01,
        alpha=0.3,
    )
    
    # Uniform data field (no modulation) for baseline skyrmions
    data_field = np.zeros((params.grid_size, params.grid_size))
    
    print("Initializing simulator for basic skyrmion formation...")
    simulator = SkyrmionSimulator(params, data_field=data_field)
    
    print("Running simulation...")
    simulator.run(verbose=True)
    
    # Analyze results
    m_z = simulator.get_m_z()
    analyzer = SkyrmionAnalyzer()
    skyrmion_info = analyzer.detect_skyrmions(m_z, threshold=0.4)
    
    print(f"\nResults:")
    print(f"  Detected skyrmions: {skyrmion_info['count']}")
    if skyrmion_info['count'] > 0:
        print(f"  Mean skyrmion size: {skyrmion_info['mean_size']:.2f} cells")
        print(f"  Size std dev: {skyrmion_info['std_size']:.2f} cells")
    
    # Visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    axes[0].imshow(m_z, cmap='RdBu_r', vmin=-1, vmax=1)
    axes[0].set_title('Final m_z Configuration')
    axes[0].set_xlabel('x')
    axes[0].set_ylabel('y')
    
    energy_hist = simulator.get_energy_history()
    axes[1].plot(np.arange(len(energy_hist)) * params.save_interval, energy_hist, 'b-')
    axes[1].set_xlabel('Simulation Step')
    axes[1].set_ylabel('Total Energy (J)')
    axes[1].set_title('Energy Evolution')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('outputs/example_1_basic_skyrmions.png', dpi=150, bbox_inches='tight')
    print("\nSaved to outputs/example_1_basic_skyrmions.png")


def example_2_data_encoding():
    """
    Example 2: Encode different manifold patterns into skyrmion configurations.
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Data Encoding with Different Manifolds")
    print("="*70)
    
    patterns = ['gaussian_bumps', 'sinusoid', 'checkerboard']
    
    params = MicromagneticParams(
        grid_size=128,
        dt=1e-12,
        num_steps=15000,
        save_interval=250,
        eps_K=0.25,
    )
    
    fig, axes = plt.subplots(3, 3, figsize=(15, 14))
    
    for row, pattern in enumerate(patterns):
        print(f"\nProcessing pattern: {pattern}")
        
        # Create data manifold
        data_field = create_sample_manifold(params.grid_size, pattern=pattern)
        
        # Simulate
        simulator = SkyrmionSimulator(params, data_field=data_field)
        print(f"  Running simulation...")
        simulator.run(verbose=False)
        
        m_z = simulator.get_m_z()
        
        # Analyze encoding fidelity
        analyzer = SkyrmionAnalyzer()
        correlation = analyzer.extract_manifold_signature(m_z, data_field)
        
        print(f"  Data-Magnetization correlation: {correlation:.4f}")
        
        # Decode data
        decoder = DataEncodingDecoder()
        capacity = decoder.compute_channel_capacity(m_z)
        print(f"  Estimated channel capacity: {capacity:.1f} bits")
        
        # Visualization
        axes[row, 0].imshow(data_field, cmap='RdBu_r')
        axes[row, 0].set_title(f'{pattern.title()}\nData Field')
        axes[row, 0].set_xticks([])
        axes[row, 0].set_yticks([])
        
        axes[row, 1].imshow(m_z, cmap='RdBu_r', vmin=-1, vmax=1)
        axes[row, 1].set_title(f'Resulting m_z\nCorr: {correlation:.3f}')
        axes[row, 1].set_xticks([])
        axes[row, 1].set_yticks([])
        
        energy_hist = simulator.get_energy_history()
        axes[row, 2].plot(np.arange(len(energy_hist)) * params.save_interval, energy_hist)
        axes[row, 2].set_title(f'Energy Evolution\nCapacity: {capacity:.0f} bits')
        axes[row, 2].grid(True, alpha=0.3)
        axes[row, 2].set_xticks([])
    
    plt.tight_layout()
    plt.savefig('outputs/example_2_data_encoding.png', dpi=150, bbox_inches='tight')
    print("\nSaved to outputs/example_2_data_encoding.png")


def example_3_parameter_sensitivity():
    """
    Example 3: Analyze sensitivity to key parameters.
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Parameter Sensitivity Analysis")
    print("="*70)
    
    base_params = MicromagneticParams(
        grid_size=64,
        dt=1e-12,
        num_steps=10000,
        save_interval=200,
    )
    
    # Test different DMI strengths
    dmi_values = [2e-3, 4e-3, 6e-3, 8e-3]
    dmi_results = []
    
    print("\nTesting DMI sensitivity...")
    data_field = create_sample_manifold(base_params.grid_size, pattern='gaussian_bumps')
    
    for D in dmi_values:
        print(f"  D = {D:.2e} J/m²")
        params = MicromagneticParams(
            grid_size=base_params.grid_size,
            dt=base_params.dt,
            num_steps=base_params.num_steps,
            D=D,
        )
        
        simulator = SkyrmionSimulator(params, data_field=data_field)
        simulator.run(verbose=False)
        
        m_z = simulator.get_m_z()
        analyzer = SkyrmionAnalyzer()
        skyrmion_info = analyzer.detect_skyrmions(m_z, threshold=0.4)
        
        dmi_results.append({
            'D': D,
            'n_skyrmions': skyrmion_info['count'],
            'm_z_mean': m_z.mean(),
            'm_z_std': m_z.std(),
            'energy': simulator.energy_history[-1] if simulator.energy_history else 0
        })
        print(f"    Skyrmions: {skyrmion_info['count']}, m_z mean: {m_z.mean():.3f}")
    
    # Test different anisotropy modulations
    eps_values = [0.0, 0.1, 0.2, 0.3, 0.4]
    eps_results = []
    
    print("\nTesting anisotropy modulation sensitivity...")
    for eps in eps_values:
        print(f"  ε = {eps:.2f}")
        params = MicromagneticParams(
            grid_size=base_params.grid_size,
            dt=base_params.dt,
            num_steps=base_params.num_steps,
            eps_K=eps,
        )
        
        simulator = SkyrmionSimulator(params, data_field=data_field)
        simulator.run(verbose=False)
        
        m_z = simulator.get_m_z()
        analyzer = SkyrmionAnalyzer()
        correlation = analyzer.extract_manifold_signature(m_z, data_field)
        
        eps_results.append({
            'eps': eps,
            'correlation': correlation,
            'm_z_std': m_z.std(),
        })
        print(f"    Correlation: {correlation:.4f}")
    
    # Plots
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # DMI sensitivity
    ax = axes[0]
    D_vals = [r['D'] * 1e3 for r in dmi_results]  # Convert to mJ/m²
    n_sky = [r['n_skyrmions'] for r in dmi_results]
    ax.plot(D_vals, n_sky, 'o-', linewidth=2, markersize=8)
    ax.set_xlabel('DMI Constant D (mJ/m²)')
    ax.set_ylabel('Number of Skyrmions')
    ax.set_title('DMI Sensitivity')
    ax.grid(True, alpha=0.3)
    
    # Anisotropy modulation sensitivity
    ax = axes[1]
    eps_vals = [r['eps'] for r in eps_results]
    corr = [r['correlation'] for r in eps_results]
    ax.plot(eps_vals, corr, 's-', linewidth=2, markersize=8, color='green')
    ax.set_xlabel('Anisotropy Modulation ε')
    ax.set_ylabel('Data-Magnetization Correlation')
    ax.set_title('Anisotropy Modulation Sensitivity')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('outputs/example_3_sensitivity.png', dpi=150, bbox_inches='tight')
    print("\nSaved to outputs/example_3_sensitivity.png")


def example_4_high_resolution_encoding():
    """
    Example 4: High-resolution data encoding demonstration.
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: High-Resolution Data Encoding")
    print("="*70)
    
    params = MicromagneticParams(
        grid_size=256,
        dt=5e-13,
        num_steps=30000,
        save_interval=500,
        eps_K=0.2,
    )
    
    # Create complex manifold pattern
    print("Creating complex manifold...")
    data_field = create_sample_manifold(params.grid_size, pattern='gaussian_bumps')
    
    print("Running high-resolution simulation...")
    simulator = SkyrmionSimulator(params, data_field=data_field)
    simulator.run(verbose=True)
    
    m_z = simulator.get_m_z()
    
    # Comprehensive analysis
    analyzer = SkyrmionAnalyzer()
    skyrmion_info = analyzer.detect_skyrmions(m_z, threshold=0.35)
    correlation = analyzer.extract_manifold_signature(m_z, data_field)
    entropy = analyzer.compute_spin_texture_entropy(simulator.get_magnetization())
    
    decoder = DataEncodingDecoder()
    capacity = decoder.compute_channel_capacity(m_z)
    
    print(f"\nDetailed Analysis:")
    print(f"  Skyrmions detected: {skyrmion_info['count']}")
    print(f"  Data-magnetization correlation: {correlation:.4f}")
    print(f"  Spin texture entropy: {entropy:.2f}")
    print(f"  Estimated channel capacity: {capacity:.1f} bits")
    
    # Advanced visualization
    fig = plt.figure(figsize=(16, 12))
    
    # Data field
    ax1 = plt.subplot(2, 3, 1)
    im1 = ax1.imshow(data_field, cmap='RdBu_r')
    ax1.set_title('Input Data Field')
    plt.colorbar(im1, ax=ax1)
    
    # Final m_z
    ax2 = plt.subplot(2, 3, 2)
    im2 = ax2.imshow(m_z, cmap='RdBu_r', vmin=-1, vmax=1)
    ax2.set_title('Final m_z Configuration')
    plt.colorbar(im2, ax=ax2)
    
    # Energy evolution
    ax3 = plt.subplot(2, 3, 3)
    energy_hist = simulator.get_energy_history()
    steps = np.arange(len(energy_hist)) * params.save_interval
    ax3.plot(steps, energy_hist, linewidth=1)
    ax3.set_xlabel('Step')
    ax3.set_ylabel('Energy (J)')
    ax3.set_title('Energy Evolution')
    ax3.grid(True, alpha=0.3)
    
    # m_z histogram
    ax4 = plt.subplot(2, 3, 4)
    ax4.hist(m_z.flatten(), bins=50, edgecolor='black', alpha=0.7)
    ax4.set_xlabel('m_z value')
    ax4.set_ylabel('Frequency')
    ax4.set_title('m_z Distribution')
    ax4.grid(True, alpha=0.3)
    
    # Correlation scatter
    ax5 = plt.subplot(2, 3, 5)
    ax5.scatter(data_field.flatten(), m_z.flatten(), alpha=0.2, s=2)
    ax5.set_xlabel('Data Field')
    ax5.set_ylabel('m_z')
    ax5.set_title(f'Encoding Correlation: {correlation:.3f}')
    ax5.grid(True, alpha=0.3)
    
    # Skyrmion detection overlay
    ax6 = plt.subplot(2, 3, 6)
    im6 = ax6.imshow(m_z, cmap='RdBu_r', vmin=-1, vmax=1)
    if skyrmion_info['centers'].size > 0:
        centers = skyrmion_info['centers']
        ax6.scatter(centers[:, 1], centers[:, 0], c='lime', s=50, 
                   edgecolors='white', linewidths=1.5)
    ax6.set_title(f'Detected Skyrmions: {skyrmion_info["count"]}')
    
    plt.tight_layout()
    plt.savefig('outputs/example_4_high_res.png', dpi=150, bbox_inches='tight')
    print("\nSaved to outputs/example_4_high_res.png")


if __name__ == '__main__':
    # Create output directory
    Path('outputs').mkdir(exist_ok=True)
    
    print("\n" + "="*70)
    print("SKYRMION SIMULATION EXAMPLES")
    print("="*70)
    
    # Run examples
    try:
        example_1_basic_skyrmion_creation()
        plt.close('all')
    except Exception as e:
        print(f"Error in Example 1: {e}")
    
    try:
        example_2_data_encoding()
        plt.close('all')
    except Exception as e:
        print(f"Error in Example 2: {e}")
    
    try:
        example_3_parameter_sensitivity()
        plt.close('all')
    except Exception as e:
        print(f"Error in Example 3: {e}")
    
    try:
        example_4_high_resolution_encoding()
        plt.close('all')
    except Exception as e:
        print(f"Error in Example 4: {e}")
    
    print("\n" + "="*70)
    print("All examples completed!")
    print("Results saved to outputs/ directory")
    print("="*70)
