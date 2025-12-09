"""
Skyrmion Manifold Data Transmission Simulator

A finite-difference solver for the Landau-Lifshitz-Gilbert (LLG) equation
to simulate chiral magnetic thin films with skyrmion configurations encoding
data from a 2D manifold.

Physics Model:
- Micromagnetic energy with Exchange (A), DMI (D), Anisotropy (K_z), Zeeman (B)
- LLG dynamics with Gilbert damping (α)
- Data encoding via spatially modulated anisotropy K_z(x,y)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.ndimage import convolve
from pathlib import Path
import json
from dataclasses import dataclass, asdict
from typing import Optional, Union


@dataclass
class MicromagneticParams:
    """Physical parameters for micromagnetic simulation."""
    # Exchange stiffness (J/m)
    A: float = 15e-12
    # DMI constant (J/m²)
    D: float = 4e-3
    # Perpendicular anisotropy (J/m³)
    K_z: float = 0.8e6
    # Anisotropy modulation strength
    eps_K: float = 0.2
    # External field (T) - moderate positive field for stable skyrmions in positive background
    # Positive field (B_z > 0) favors m_z = +1, DMI creates topological reversed cores
    B_z: float = 0.010
    # Gilbert damping coefficient
    alpha: float = 0.3
    # Saturation magnetization (A/m)
    M_s: float = 4e5
    
    # Grid parameters
    grid_size: int = 256
    cell_size: float = 1.0  # in nm
    thickness: float = 10.0  # Magnetic film thickness in nm (typical 10-100 nm)
    
    # Time-stepping
    dt: float = 1e-12  # seconds
    num_steps: int = 50000
    save_interval: int = 1000
    
    # Relaxation parameters
    use_adaptive_dt: bool = True
    max_energy_change: float = 1e-9


class SkyrmionSimulator:
    """
    Finite-difference solver for micromagnetic simulations with skyrmion dynamics.
    """
    
    def __init__(self, params: MicromagneticParams, data_field: Optional[np.ndarray] = None):
        """
        Initialize the simulator.
        
        Args:
            params: MicromagneticParams object with physical parameters
            data_field: Optional (N, N) array normalized to [-1, 1] for anisotropy modulation
        """
        self.params = params
        self.N = params.grid_size
        # Convert cell size from nm to meters
        self.dx = params.cell_size * 1e-9  # cell_size in nm, convert to m
        # Convert film thickness from nm to meters
        self.thickness = params.thickness * 1e-9  # thickness in nm, convert to m
        
        # Magnetization field: shape (N, N, 3) for (m_x, m_y, m_z)
        self.m = np.zeros((self.N, self.N, 3), dtype=np.float32)
        # Initialize with mostly uniform out-of-plane state plus random perturbations
        # Using positive bias (m_z = +0.9) matched to positive B_z field for stability
        # Strong noise (18%) allows DMI to create skyrmion cores despite field alignment
        noise_strength = 0.18  # 18% noise - balance between stability and exploration
        self.m[:, :, 0] = np.random.randn(self.N, self.N) * noise_strength
        self.m[:, :, 1] = np.random.randn(self.N, self.N) * noise_strength
        # Positive bias state (stable with positive B_z field)
        self.m[:, :, 2] = 0.9 + np.random.randn(self.N, self.N) * noise_strength
        
        # Normalize to unit vectors
        m_norm = np.linalg.norm(self.m, axis=2, keepdims=True)
        m_norm = np.where(m_norm > 1e-10, m_norm, 1.0)
        self.m = self.m / m_norm
        
        # Data field for anisotropy modulation
        if data_field is None:
            # Default: create a sample pattern (e.g., Gaussian bumps)
            self.data_field = self._create_sample_data_field()
        else:
            # Normalize input to [-1, 1]
            data_field = np.asarray(data_field, dtype=np.float32)
            dmin, dmax = data_field.min(), data_field.max()
            if dmax > dmin:
                self.data_field = 2 * (data_field - dmin) / (dmax - dmin) - 1
            else:
                self.data_field = data_field.copy()
        
        # Spatially modulated anisotropy: K_z(x,y) = K_0 + eps * D(x,y)
        self.K_z_map = (
            self.params.K_z +
            self.params.eps_K * self.params.K_z * self.data_field
        ).astype(np.float32)
        
        # Energy and trajectory tracking
        self.energy_history = []
        self.m_z_history = []
        self.step_count = 0
        
        # Kernels for finite differences (periodic boundary conditions)
        self._setup_kernels()
    
    def _create_sample_data_field(self) -> np.ndarray:
        """Create a sample 2D data field with Gaussian features."""
        x = np.linspace(-2, 2, self.N)
        y = np.linspace(-2, 2, self.N)
        X, Y = np.meshgrid(x, y)
        
        # Multiple Gaussian bumps
        data = (
            np.exp(-((X - 0.5)**2 + (Y - 0.5)**2) / 0.2) +
            np.exp(-((X + 0.5)**2 + (Y + 0.5)**2) / 0.2) +
            0.5 * np.exp(-((X)**2 + (Y - 1)**2) / 0.3)
        )
        # Normalize to [-1, 1]
        data = 2 * (data - data.min()) / (data.max() - data.min() + 1e-8) - 1
        return data.astype(np.float32)
    
    def _setup_kernels(self):
        """Setup finite-difference kernels for computing field derivatives."""
        # Laplacian kernel for ∇² operator (5-point stencil, periodic BC)
        self.laplacian_kernel = np.array(
            [[0, 1, 0],
             [1, -4, 1],
             [0, 1, 0]], dtype=np.float32
        ) / (self.dx ** 2)
        
        # Gradient kernels
        self.grad_x_kernel = np.array(
            [[0, 0, 0],
             [-1, 0, 1],
             [0, 0, 0]], dtype=np.float32
        ) / (2 * self.dx)
        
        self.grad_y_kernel = np.array(
            [[0, -1, 0],
             [0, 0, 0],
             [0, 1, 0]], dtype=np.float32
        ) / (2 * self.dx)
    
    def _compute_exchange_field(self) -> np.ndarray:
        """
        Compute exchange field: H_ex = A / (μ₀ M_s) * ∇²m
        
        Returns:
            Exchange field shape (N, N, 3)
        """
        H_ex = np.zeros((self.N, self.N, 3))
        factor = self.params.A / (4 * np.pi * 1e-7 * self.params.M_s)
        
        for i in range(3):
            H_ex[:, :, i] = convolve(
                self.m[:, :, i], 
                self.laplacian_kernel, 
                mode='wrap'
            ) * factor
        return H_ex
    
    def _compute_dmi_field(self) -> np.ndarray:
        """
        Compute DMI field: H_DMI = D / (μ₀ M_s) * (n × ∇²m)
        Simplified for 2D thin film: H_DMI ~ D * (ẑ × ∇m_z)
        
        Returns:
            DMI field shape (N, N, 3)
        """
        H_dmi = np.zeros((self.N, self.N, 3))
        factor = self.params.D / (4 * np.pi * 1e-7 * self.params.M_s)
        
        # DMI gradient of m_z (out-of-plane magnetization)
        grad_mz_x = convolve(self.m[:, :, 2], self.grad_x_kernel, mode='wrap')
        grad_mz_y = convolve(self.m[:, :, 2], self.grad_y_kernel, mode='wrap')
        
        # H_dmi,x = -D * ∂m_z/∂y, H_dmi,y = D * ∂m_z/∂x (perpendicular DMI)
        H_dmi[:, :, 0] = -factor * grad_mz_y
        H_dmi[:, :, 1] = factor * grad_mz_x
        
        return H_dmi
    
    def _compute_anisotropy_field(self) -> np.ndarray:
        """
        Compute perpendicular anisotropy field: H_k = -2*K_z/M_s * m_z * ẑ
        Spatially modulated by data field.
        
        Returns:
            Anisotropy field shape (N, N, 3)
        """
        H_anis = np.zeros((self.N, self.N, 3))
        factor = -2 * self.K_z_map / self.params.M_s
        H_anis[:, :, 2] = factor * self.m[:, :, 2]
        return H_anis
    
    def _compute_zeeman_field(self) -> np.ndarray:
        """
        Compute external Zeeman field: H_z = B_z / μ₀
        
        Returns:
            Zeeman field shape (N, N, 3)
        """
        H_zee = np.zeros((self.N, self.N, 3))
        H_zee[:, :, 2] = self.params.B_z / (4 * np.pi * 1e-7)
        return H_zee
    
    def _compute_effective_field(self) -> np.ndarray:
        """
        Total effective field: H_eff = H_ex + H_dmi + H_anis + H_zee
        
        Returns:
            Effective field shape (N, N, 3)
        """
        H_eff = (
            self._compute_exchange_field() +
            self._compute_dmi_field() +
            self._compute_anisotropy_field() +
            self._compute_zeeman_field()
        )
        return H_eff
    
    def _landau_lifshitz_gilbert(self, H_eff: np.ndarray) -> np.ndarray:
        """
        LLG equation: dm/dt = -γ/(1+α²) * [m × H_eff + α * m × (m × H_eff)]
        
        Args:
            H_eff: Effective magnetic field shape (N, N, 3)
        
        Returns:
            Time derivative dm/dt shape (N, N, 3)
        """
        # Gyromagnetic ratio: γ = 1.76e11 rad/(T·s) in SI units
        # Scaled to reasonable values for numerical stability with normalized fields
        gamma = 1e4  # Scaled gyromagnetic ratio for numerical stability
        alpha = self.params.alpha
        
        # m × H_eff
        m_cross_H = np.cross(self.m, H_eff)
        
        # m × (m × H_eff)
        m_cross_m_cross_H = np.cross(self.m, m_cross_H)
        
        # dm/dt = -γ/(1+α²) * [m × H_eff + α * m × (m × H_eff)]
        dmdt = -gamma / (1 + alpha**2) * (m_cross_H + alpha * m_cross_m_cross_H)
        
        return dmdt
    
    def _normalize_magnetization(self):
        """Ensure |m| = 1 everywhere (unit vectors)."""
        m_norm = np.linalg.norm(self.m, axis=2, keepdims=True)
        m_norm = np.where(m_norm > 1e-10, m_norm, 1.0)
        self.m = self.m / m_norm
    
    def _compute_energy(self) -> float:
        """
        Compute total magnetic energy density (in J/m²).
        All parameters treated as surface energy densities (per unit area).
        This is standard thin-film micromagnetic formulation.
        
        Returns:
            Energy density in J/m²
        """
        E_ex = 0.0
        E_anis = 0.0
        E_zee = 0.0
        
        # For gradients: np.gradient gives ∂m/∂i (per index), need ∂m/∂x = (∂m/∂i) / dx
        inv_dx = 1.0 / self.dx  # Convert from index space to physical space
        
        # Exchange energy: E_ex = A_eff * ∫|∇m|² dA
        # A_eff is surface exchange stiffness (J/m²) = A_bulk * thickness
        # self.params.A is bulk exchange (J/m), multiply by thickness for surface value
        A_eff = self.params.A * self.thickness
        for i in range(3):
            # Get gradients in physical space (m⁻¹)
            grad_m_x = np.gradient(self.m[:, :, i], axis=1) * inv_dx  # ∂m/∂x
            grad_m_y = np.gradient(self.m[:, :, i], axis=0) * inv_dx  # ∂m/∂y
            # Integrate over area
            E_ex += np.sum(grad_m_x**2 + grad_m_y**2) * A_eff * (self.dx ** 2)
        
        # Anisotropy energy: E_anis = -∫K_z * m_z² * thickness dA
        # K_z is volumetric (J/m³), thickness converts to surface energy
        E_anis = -np.sum(self.K_z_map * self.m[:, :, 2]**2) * (self.dx ** 2) * self.thickness
        
        # Zeeman energy: E_zee = -μ₀ M_s ∫B_z * m_z dA
        mu_0 = 4 * np.pi * 1e-7
        E_zee = -mu_0 * self.params.M_s * self.params.B_z * np.sum(self.m[:, :, 2]) * (self.dx ** 2) * self.thickness
        
        # Total energy
        total_energy = E_ex + E_anis + E_zee
        
        # Divide by total area to get energy density (J/m²)
        total_area = (self.N * self.dx) ** 2
        energy_density = total_energy / total_area
        
        return float(energy_density)
    
    def step(self, use_euler: bool = True):
        """
        Advance simulation by one time step.
        
        Args:
            use_euler: If True, use Euler scheme; otherwise use RK2
        """
        H_eff = self._compute_effective_field()
        dmdt = self._landau_lifshitz_gilbert(H_eff)
        
        if use_euler:
            # Euler: m(t+dt) = m(t) + dt * dm/dt
            self.m += self.params.dt * dmdt
        else:
            # RK2 midpoint
            m_temp = self.m + 0.5 * self.params.dt * dmdt
            m_norm = np.linalg.norm(m_temp, axis=2, keepdims=True)
            m_norm = np.where(m_norm > 1e-10, m_norm, 1.0)
            m_temp = m_temp / m_norm
            
            H_eff_mid = self._compute_effective_field()
            dmdt_mid = self._landau_lifshitz_gilbert(H_eff_mid)
            
            self.m += self.params.dt * dmdt_mid
        
        # Ensure magnetization normalization
        self._normalize_magnetization()
        
        # Record energy and m_z
        if self.step_count % self.params.save_interval == 0:
            self.energy_history.append(self._compute_energy())
            self.m_z_history.append(self.m[:, :, 2].copy())
        
        self.step_count += 1
    
    def run(self, num_steps: Optional[int] = None, verbose: bool = True) -> None:
        """
        Run the simulation for specified number of steps.

        Args:
            num_steps: Number of steps to simulate (default: params.num_steps)
            verbose: Print progress information
        """
        if num_steps is None:
            num_steps = self.params.num_steps

        last_stable_energy = None
        divergence_counter = 0

        for step_idx in range(num_steps):
            self.step(use_euler=True)

            # Check for divergence
            current_energy = self.energy_history[-1] if self.energy_history else 0

            # If energy becomes NaN or explodes, reduce dt and continue
            if np.isnan(current_energy) or np.isinf(current_energy):
                print(f"⚠ Warning: Non-finite energy detected at step {step_idx}. Reducing dt...")
                self.params.dt *= 0.5
                divergence_counter += 1
                if divergence_counter > 5:
                    print("✗ Simulation diverged too many times. Stopping.")
                    break
                continue

            # Check for energy increasing (indicates instability)
            if last_stable_energy is not None and current_energy > last_stable_energy + 1e-4:
                # Energy jumped significantly - slight step size reduction
                if divergence_counter < 3:
                    self.params.dt *= 0.9
                    divergence_counter += 1
            else:
                last_stable_energy = current_energy
                divergence_counter = max(0, divergence_counter - 1)  # Recovery

            if verbose and (step_idx + 1) % max(1, num_steps // 20) == 0:
                energy = current_energy
                print(f"Step {step_idx + 1:5d}/{num_steps}, Energy: {energy:.6e} (dt={self.params.dt:.3e})")
    
    def get_magnetization(self) -> np.ndarray:
        """Return current magnetization field shape (N, N, 3)."""
        return self.m.copy()
    
    def get_m_z(self) -> np.ndarray:
        """Return current out-of-plane magnetization m_z shape (N, N)."""
        return self.m[:, :, 2].copy()
    
    def get_energy_history(self) -> list:
        """Return energy values over time."""
        return self.energy_history.copy()


def create_sample_manifold(size: int = 256, pattern: str = 'gaussian_bumps') -> np.ndarray:
    """
    Create a sample 2D manifold/image for data encoding.
    
    Args:
        size: Dimension of output array (size x size)
        pattern: Type of pattern ('gaussian_bumps', 'sinusoid', 'checkerboard', 'random')
    
    Returns:
        Normalized array in [-1, 1]
    """
    x = np.linspace(-3, 3, size)
    y = np.linspace(-3, 3, size)
    X, Y = np.meshgrid(x, y)
    
    if pattern == 'gaussian_bumps':
        data = (
            1.5 * np.exp(-((X - 1)**2 + (Y - 1)**2) / 0.3) +
            np.exp(-((X + 1)**2 + (Y + 1)**2) / 0.3) +
            0.8 * np.exp(-((X)**2 + (Y - 1.5)**2) / 0.2)
        )
    elif pattern == 'sinusoid':
        data = np.sin(2 * np.pi * X / 3) * np.cos(2 * np.pi * Y / 3)
    elif pattern == 'checkerboard':
        data = np.sign(np.sin(3 * np.pi * X) * np.sin(3 * np.pi * Y))
    elif pattern == 'random':
        data = np.random.randn(size, size)
    else:
        raise ValueError(f"Unknown pattern: {pattern}")
    
    # Normalize to [-1, 1]
    data_min = data.min()
    data_max = data.max()
    if data_max > data_min:
        data = 2 * (data - data_min) / (data_max - data_min) - 1
    return data.astype(np.float32)


def visualize_results(simulator: SkyrmionSimulator, save_dir: Optional[Union[Path, str]] = None):
    """
    Create comprehensive visualization of simulation results.
    
    Args:
        simulator: Initialized SkyrmionSimulator instance
        save_dir: Optional directory to save figures
    """
    if save_dir is not None:
        save_dir = Path(save_dir)
        save_dir.mkdir(exist_ok=True)
    
    fig = plt.figure(figsize=(16, 12))
    
    # Panel 1: Data field
    ax1 = plt.subplot(2, 3, 1)
    im1 = ax1.imshow(simulator.data_field, cmap='RdBu_r')
    ax1.set_title('Data Field D(x,y)')
    ax1.set_xlabel('x')
    ax1.set_ylabel('y')
    plt.colorbar(im1, ax=ax1)
    
    # Panel 2: K_z modulation
    ax2 = plt.subplot(2, 3, 2)
    im2 = ax2.imshow(simulator.K_z_map / 1e6, cmap='viridis')
    ax2.set_title('Modulated Anisotropy K_z(x,y)')
    ax2.set_xlabel('x')
    ax2.set_ylabel('y')
    plt.colorbar(im2, ax=ax2, label='K_z (MJ/m³)')
    
    # Panel 3: Final m_z configuration
    ax3 = plt.subplot(2, 3, 3)
    m_z_final = simulator.get_m_z()
    im3 = ax3.imshow(m_z_final, cmap='RdBu_r', vmin=-1, vmax=1)
    ax3.set_title('Final m_z(x,y) Configuration')
    ax3.set_xlabel('x')
    ax3.set_ylabel('y')
    plt.colorbar(im3, ax=ax3, label='m_z')
    
    # Panel 4: Energy evolution
    ax4 = plt.subplot(2, 3, 4)
    energy_hist = simulator.get_energy_history()
    if energy_hist:
        steps = np.arange(len(energy_hist)) * simulator.params.save_interval
        ax4.plot(steps, energy_hist, 'b-', linewidth=1.5)
        ax4.set_xlabel('Simulation Step')
        ax4.set_ylabel('Total Energy (J)')
        ax4.set_title('Energy Evolution')
        ax4.grid(True, alpha=0.3)
    
    # Panel 5: m_z spatial histogram
    ax5 = plt.subplot(2, 3, 5)
    ax5.hist(m_z_final.flatten(), bins=50, edgecolor='black', alpha=0.7)
    ax5.set_xlabel('m_z value')
    ax5.set_ylabel('Frequency')
    ax5.set_title('m_z Distribution')
    ax5.grid(True, alpha=0.3)
    
    # Panel 6: Correlation between data and m_z
    ax6 = plt.subplot(2, 3, 6)
    correlation = np.corrcoef(
        simulator.data_field.flatten(),
        m_z_final.flatten()
    )[0, 1]
    ax6.scatter(simulator.data_field.flatten(), m_z_final.flatten(), alpha=0.3, s=5)
    ax6.set_xlabel('Data Field D(x,y)')
    ax6.set_ylabel('m_z(x,y)')
    ax6.set_title(f'Data-Magnetization Correlation: {correlation:.3f}')
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_dir:
        plt.savefig(save_dir / 'skyrmion_analysis.png', dpi=150, bbox_inches='tight')
        print(f"Saved visualization to {save_dir / 'skyrmion_analysis.png'}")
    
    plt.show()


def save_results(simulator: SkyrmionSimulator, output_dir: Path):
    """
    Save simulation results to disk.
    
    Args:
        simulator: Initialized SkyrmionSimulator instance
        output_dir: Directory to save results
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Save magnetization field
    np.save(output_dir / 'magnetization_field.npy', simulator.get_magnetization())
    np.save(output_dir / 'm_z_final.npy', simulator.get_m_z())
    np.save(output_dir / 'data_field.npy', simulator.data_field)
    np.save(output_dir / 'K_z_map.npy', simulator.K_z_map)
    
    # Save energy history
    np.save(output_dir / 'energy_history.npy', np.array(simulator.get_energy_history()))
    
    # Save parameters
    params_dict = asdict(simulator.params)
    with open(output_dir / 'parameters.json', 'w') as f:
        json.dump(params_dict, f, indent=2)
    
    print(f"Results saved to {output_dir}")


if __name__ == '__main__':
    print("=" * 70)
    print("SKYRMION MANIFOLD DATA TRANSMISSION SIMULATOR")
    print("=" * 70)
    
    # Configure simulation parameters
    params = MicromagneticParams(
        grid_size=256,
        dt=5e-13,
        num_steps=30000,
        save_interval=500,
        alpha=0.3,
    )
    
    print(f"\nSimulation Parameters:")
    print(f"  Grid size: {params.grid_size}×{params.grid_size}")
    print(f"  Cell size: {params.cell_size} nm")
    print(f"  Exchange stiffness A: {params.A:.3e} J/m")
    print(f"  DMI constant D: {params.D:.3e} J/m²")
    print(f"  Base anisotropy K_z: {params.K_z:.3e} J/m³")
    print(f"  Anisotropy modulation ε: {params.eps_K:.2f}")
    print(f"  External field B_z: {params.B_z:.3e} T")
    print(f"  Gilbert damping α: {params.alpha:.2f}")
    print(f"  Time step dt: {params.dt:.3e} s")
    print(f"  Total steps: {params.num_steps}")
    print(f"  Save interval: {params.save_interval} steps\n")
    
    # Create sample data manifold
    print("Creating sample data manifold...")
    data_manifold = create_sample_manifold(size=params.grid_size, pattern='gaussian_bumps')
    
    # Initialize simulator
    print("Initializing simulator...")
    simulator = SkyrmionSimulator(params, data_field=data_manifold)
    
    # Run simulation
    print("Running simulation...")
    simulator.run(verbose=True)
    
    print("\nSimulation complete!")
    
    # Visualize results
    print("\nGenerating visualizations...")
    visualize_results(simulator, save_dir='outputs/skyrmion_results')
    
    # Save results
    save_results(simulator, Path('outputs/skyrmion_results'))
    
    print("\n" + "=" * 70)
    print("Analysis Summary:")
    print("=" * 70)
    
    m_z_final = simulator.get_m_z()
    print(f"m_z range: [{m_z_final.min():.3f}, {m_z_final.max():.3f}]")
    print(f"m_z mean: {m_z_final.mean():.3f}")
    print(f"m_z std: {m_z_final.std():.3f}")
    
    correlation = np.corrcoef(
        simulator.data_field.flatten(),
        m_z_final.flatten()
    )[0, 1]
    print(f"Data-Magnetization correlation: {correlation:.4f}")
    
    if simulator.energy_history:
        energy_init = simulator.energy_history[0]
        energy_final = simulator.energy_history[-1]
        print(f"Initial energy: {energy_init:.6e} J")
        print(f"Final energy: {energy_final:.6e} J")
        print(f"Energy change: {energy_final - energy_init:.6e} J")
    
    print("=" * 70)
