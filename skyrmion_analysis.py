"""
Skyrmion Analysis and Utilities Module

Advanced tools for skyrmion detection, characterization, and data encoding/decoding.
"""

import numpy as np
from scipy import ndimage
from scipy.signal import find_peaks
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from pathlib import Path


class SkyrmionAnalyzer:
    """
    Tools for detecting, characterizing, and analyzing skyrmion configurations.
    """
    
    @staticmethod
    def detect_skyrmions(m_z: np.ndarray, threshold: float = 0.3) -> dict:
        """
        Detect skyrmions using topological charge analysis.
        A skyrmion is characterized by reversed (opposite sign) m_z cores.
        
        Args:
            m_z: Out-of-plane magnetization array (N, N)
            threshold: Threshold for separating core (|m_z| < threshold) from background
        
        Returns:
            Dictionary with skyrmion statistics
        """
        # Find core regions (low |m_z| values)
        core_mask = np.abs(m_z) < threshold
        
        # Label connected components
        labeled, n_skyrmions = ndimage.label(core_mask)
        
        # Get properties of each skyrmion
        properties = ndimage.find_objects(labeled)
        centers = ndimage.center_of_mass(core_mask, labeled, range(1, n_skyrmions + 1))
        
        skyrmion_info = {
            'count': n_skyrmions,
            'centers': np.array(centers) if centers else np.array([]),
            'core_areas': [],
            'sizes': [],
        }
        
        for i, slc in enumerate(properties):
            if slc is not None:
                core_region = core_mask[slc]
                area = np.sum(core_region)
                skyrmion_info['core_areas'].append(area)
                skyrmion_info['sizes'].append(np.sqrt(area))
        
        if skyrmion_info['core_areas']:
            skyrmion_info['mean_size'] = np.mean(skyrmion_info['sizes'])
            skyrmion_info['std_size'] = np.std(skyrmion_info['sizes'])
        
        return skyrmion_info
    
    @staticmethod
    def compute_topological_charge(m_x: np.ndarray, m_y: np.ndarray, 
                                   m_z: np.ndarray, N_window: int = None) -> np.ndarray:
        """
        Compute local topological charge density.
        Q = (1/4π) * m · (∂m/∂x × ∂m/∂y)
        
        Args:
            m_x, m_y, m_z: Magnetization components (N, N)
            N_window: Window size for local averaging (None for no averaging)
        
        Returns:
            Topological charge density array (N, N)
        """
        m = np.stack([m_x, m_y, m_z], axis=-1)
        
        # Compute gradients
        dm_dx = np.gradient(m, axis=1)  # ∂m/∂x
        dm_dy = np.gradient(m, axis=0)  # ∂m/∂y
        
        # Compute m · (∂m/∂x × ∂m/∂y)
        cross_prod = np.cross(dm_dx, dm_dy)  # shape (N, N, 3)
        q_density = np.sum(m * cross_prod, axis=2) / (4 * np.pi)
        
        if N_window is not None:
            from scipy.ndimage import uniform_filter
            q_density = uniform_filter(q_density, size=N_window)
        
        return q_density
    
    @staticmethod
    def extract_manifold_signature(m_z: np.ndarray, data_field: np.ndarray) -> float:
        """
        Compute correlation between magnetization and input data field.
        High correlation indicates successful encoding.
        
        Args:
            m_z: Final out-of-plane magnetization (N, N)
            data_field: Input data field (N, N)
        
        Returns:
            Pearson correlation coefficient
        """
        flat_m = m_z.flatten()
        flat_d = data_field.flatten()
        correlation = np.corrcoef(flat_m, flat_d)[0, 1]
        return correlation
    
    @staticmethod
    def compute_spin_texture_entropy(m: np.ndarray) -> float:
        """
        Compute Shannon entropy of spin texture orientation.
        Lower entropy = more ordered (skyrmion-like) structure.
        
        Args:
            m: Magnetization field (N, N, 3)
        
        Returns:
            Entropy value (dimensionless)
        """
        # Quantize magnetization directions to nearest bin
        theta = np.arctan2(np.sqrt(m[:, :, 0]**2 + m[:, :, 1]**2), m[:, :, 2])
        phi = np.arctan2(m[:, :, 1], m[:, :, 0])
        
        # Create 2D histogram
        n_bins = 16
        hist_theta, _ = np.histogram(theta, bins=n_bins, range=(-np.pi, np.pi))
        hist_phi, _ = np.histogram(phi, bins=n_bins, range=(-np.pi, np.pi))
        
        # Normalize
        p_theta = hist_theta / np.sum(hist_theta)
        p_phi = hist_phi / np.sum(hist_phi)
        
        # Compute entropy (Shannon)
        entropy = -np.sum(p_theta[p_theta > 0] * np.log2(p_theta[p_theta > 0])) - \
                  np.sum(p_phi[p_phi > 0] * np.log2(p_phi[p_phi > 0]))
        
        return entropy


class DataEncodingDecoder:
    """
    Tools for encoding data into magnetization and decoding it back.
    """
    
    @staticmethod
    def encode_to_magnetization(data_field: np.ndarray, m_z_response: np.ndarray) -> np.ndarray:
        """
        Create encoded message by comparing data field and resulting m_z.
        Encoded bit = 1 if data_field and m_z have same sign, 0 otherwise.
        
        Args:
            data_field: Original data field (N, N) in [-1, 1]
            m_z_response: Resulting magnetization (N, N)
        
        Returns:
            Encoded bit array (N, N, binary)
        """
        encoded = (np.sign(data_field) * np.sign(m_z_response) > 0).astype(np.uint8)
        return encoded
    
    @staticmethod
    def decode_from_magnetization(m_z: np.ndarray, num_levels: int = 256) -> np.ndarray:
        """
        Decode data from magnetization configuration.
        Simple approach: histogram-based quantization of m_z values.
        
        Args:
            m_z: Out-of-plane magnetization (N, N) in [-1, 1]
            num_levels: Number of quantization levels
        
        Returns:
            Decoded data field (N, N) in [0, num_levels-1]
        """
        # Quantize m_z
        decoded = np.digitize(m_z, bins=np.linspace(-1, 1, num_levels + 1)) - 1
        decoded = np.clip(decoded, 0, num_levels - 1)
        return decoded.astype(np.uint8)
    
    @staticmethod
    def compute_channel_capacity(m_z: np.ndarray, num_pixels: int = None) -> float:
        """
        Estimate information capacity based on m_z variance.
        Higher variance = higher capacity.
        
        Args:
            m_z: Out-of-plane magnetization (N, N)
            num_pixels: Number of pixels (defaults to array size)
        
        Returns:
            Estimated bits of information
        """
        if num_pixels is None:
            num_pixels = m_z.shape[0] * m_z.shape[1]
        
        # Information content ≈ bits per pixel × num_pixels
        # Using variance as proxy for distinguishability
        variance = np.var(m_z)
        bits_per_pixel = np.log2(1 + variance)
        
        return bits_per_pixel * num_pixels


def plot_skyrmion_detection(m_z: np.ndarray, skyrmion_info: dict, 
                            output_path: Path = None):
    """
    Visualize detected skyrmions on the magnetization map.
    
    Args:
        m_z: Out-of-plane magnetization array (N, N)
        skyrmion_info: Dictionary from SkyrmionAnalyzer.detect_skyrmions()
        output_path: Optional path to save figure
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    
    im = ax.imshow(m_z, cmap='RdBu_r', vmin=-1, vmax=1)
    ax.set_title(f"Skyrmion Detection (count: {skyrmion_info['count']})")
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    
    # Plot skyrmion centers
    if skyrmion_info['centers'].size > 0:
        centers = skyrmion_info['centers']
        ax.scatter(centers[:, 1], centers[:, 0], c='green', s=100, 
                   marker='o', edgecolors='white', linewidth=2, label='Centers')
        
        # Draw circles around skyrmions
        for i, (size, center) in enumerate(zip(skyrmion_info.get('sizes', []), centers)):
            circle = Circle((center[1], center[0]), radius=size, 
                          fill=False, edgecolor='lime', linewidth=1.5, linestyle='--')
            ax.add_patch(circle)
    
    ax.legend()
    plt.colorbar(im, ax=ax, label='m_z')
    plt.tight_layout()
    
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(exist_ok=True, parents=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved skyrmion detection plot to {output_path}")
    
    plt.show()


def plot_energy_landscape(simulator, output_path: Path = None):
    """
    Create detailed energy landscape analysis plots.
    
    Args:
        simulator: SkyrmionSimulator instance
        output_path: Optional path to save figure
    """
    energy_hist = simulator.get_energy_history()
    if not energy_hist:
        print("No energy history available")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    steps = np.arange(len(energy_hist)) * simulator.params.save_interval
    
    # Full energy evolution
    ax = axes[0, 0]
    ax.plot(steps, energy_hist, 'b-', linewidth=1)
    ax.set_xlabel('Simulation Step')
    ax.set_ylabel('Total Energy (J)')
    ax.set_title('Energy Evolution')
    ax.grid(True, alpha=0.3)
    
    # Energy convergence (log scale)
    ax = axes[0, 1]
    energy_diff = np.abs(np.diff(energy_hist))
    ax.semilogy(steps[1:], energy_diff, 'r-', linewidth=1)
    ax.set_xlabel('Simulation Step')
    ax.set_ylabel('|ΔE| (J)')
    ax.set_title('Energy Change (log scale)')
    ax.grid(True, alpha=0.3)
    
    # Energy histogram
    ax = axes[1, 0]
    ax.hist(energy_hist, bins=30, edgecolor='black', alpha=0.7)
    ax.set_xlabel('Energy (J)')
    ax.set_ylabel('Frequency')
    ax.set_title('Energy Distribution')
    ax.grid(True, alpha=0.3)
    
    # Convergence metric
    ax = axes[1, 1]
    window = min(50, len(energy_hist) // 10)
    if window > 1:
        rolling_avg = np.convolve(np.array(energy_hist), np.ones(window)/window, mode='valid')
        ax.plot(steps[:len(rolling_avg)], rolling_avg, 'g-', linewidth=1.5, label='Rolling avg')
        ax.plot(steps, energy_hist, 'b-', alpha=0.3, linewidth=0.5, label='Raw')
        ax.legend()
        ax.set_xlabel('Simulation Step')
        ax.set_ylabel('Energy (J)')
        ax.set_title(f'Energy with {window}-step Rolling Average')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(exist_ok=True, parents=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved energy landscape plot to {output_path}")
    
    plt.show()


if __name__ == '__main__':
    print("Skyrmion Analysis and Utilities Module")
    print("This module provides advanced analysis tools for skyrmion simulations.")
