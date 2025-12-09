"""
Skyrmion Animation Module

Create animated visualizations of skyrmion evolution during simulation.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import Normalize
from pathlib import Path
from typing import List, Optional, Tuple


class SkyrmionAnimator:
    """
    Create animations of skyrmion configurations evolving over time.
    """
    
    def __init__(self, simulator, output_dir: Optional[Path] = None):
        """
        Initialize animator.
        
        Args:
            simulator: SkyrmionSimulator instance with m_z_history
            output_dir: Directory to save animation files
        """
        self.simulator = simulator
        self.output_dir = Path(output_dir) if output_dir else Path('outputs')
        self.output_dir.mkdir(exist_ok=True)
        
        self.m_z_history = simulator.m_z_history
        self.energy_history = simulator.energy_history
        self.params = simulator.params
    
    def create_m_z_evolution_animation(self, 
                                       save_path: Optional[Path] = None,
                                       fps: int = 10,
                                       skip_frames: int = 1) -> Optional[animation.FuncAnimation]:
        """
        Create animation of m_z evolution over time.
        
        Args:
            save_path: Path to save MP4 file (optional)
            fps: Frames per second
            skip_frames: Show every Nth frame to speed up
        
        Returns:
            FuncAnimation object
        """
        if not self.m_z_history:
            print("No m_z history available for animation")
            return None
        
        # Prepare frames
        frames = self.m_z_history[::skip_frames]
        n_frames = len(frames)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Initialize images
        im1 = ax1.imshow(frames[0], cmap='RdBu_r', vmin=-1, vmax=1)
        ax1.set_title('Out-of-Plane Magnetization m_z(x,y)')
        ax1.set_xlabel('x')
        ax1.set_ylabel('y')
        cbar1 = plt.colorbar(im1, ax=ax1, label='m_z')
        
        # Energy plot
        steps = np.arange(len(self.energy_history)) * self.params.save_interval
        ax2.plot(steps, self.energy_history, 'b-', linewidth=1, alpha=0.5)
        line, = ax2.plot([], [], 'ro-', linewidth=2, markersize=8, label='Current')
        ax2.set_xlabel('Simulation Step')
        ax2.set_ylabel('Energy (J/area)')
        ax2.set_title('Energy Evolution')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # Set axis limits for energy plot
        ax2.set_xlim(0, steps[-1])
        ax2.set_ylim(np.array(self.energy_history).min() * 1.1, 
                     np.array(self.energy_history).max() * 0.9)
        
        # Text for frame info
        text = fig.text(0.5, 0.02, '', ha='center', fontsize=12, weight='bold')
        
        def animate(frame_idx):
            """Update animation frame."""
            m_z = frames[frame_idx]
            im1.set_array(m_z)
            
            # Update energy point
            step_idx = frame_idx * skip_frames
            if step_idx < len(self.energy_history):
                step = step_idx * self.params.save_interval
                energy = self.energy_history[step_idx]
                line.set_data([step], [energy])
            
            # Update text
            step_number = frame_idx * skip_frames * self.params.save_interval
            m_z_mean = np.mean(m_z)
            m_z_std = np.std(m_z)
            text.set_text(
                f'Step: {step_number:,} | '
                f'm_z mean: {m_z_mean:.3f} ± {m_z_std:.3f}'
            )
            
            return im1, line, text
        
        anim = animation.FuncAnimation(
            fig, animate, frames=n_frames, interval=1000//fps,
            blit=True, repeat=True
        )
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(exist_ok=True, parents=True)
            try:
                anim.save(save_path, writer='ffmpeg', fps=fps)
                print(f"✓ Animation saved to {save_path}")
            except Exception as e:
                print(f"⚠ Could not save MP4 (ffmpeg needed): {e}")
                print("  Saving PNG instead...")
                self._save_as_gif(anim, save_path.with_suffix('.gif'))
        
        return anim
    
    def create_comparison_animation(self, 
                                    data_field: np.ndarray,
                                    save_path: Optional[Path] = None,
                                    fps: int = 10,
                                    skip_frames: int = 1) -> Optional[animation.FuncAnimation]:
        """
        Create animation showing data field vs evolving m_z.
        
        Args:
            data_field: Input data manifold (N, N)
            save_path: Path to save MP4 file (optional)
            fps: Frames per second
            skip_frames: Show every Nth frame
        
        Returns:
            FuncAnimation object
        """
        if not self.m_z_history:
            print("No m_z history available")
            return None
        
        frames = self.m_z_history[::skip_frames]
        n_frames = len(frames)
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        # Data field (fixed)
        im1 = axes[0, 0].imshow(data_field, cmap='RdBu_r')
        axes[0, 0].set_title('Input Data Field D(x,y)')
        axes[0, 0].set_xlabel('x')
        axes[0, 0].set_ylabel('y')
        plt.colorbar(im1, ax=axes[0, 0])
        
        # m_z evolution
        im2 = axes[0, 1].imshow(frames[0], cmap='RdBu_r', vmin=-1, vmax=1)
        axes[0, 1].set_title('Magnetization m_z(x,y)')
        axes[0, 1].set_xlabel('x')
        axes[0, 1].set_ylabel('y')
        cbar2 = plt.colorbar(im2, ax=axes[0, 1], label='m_z')
        
        # Correlation
        corr_array = []
        for frame in frames:
            corr = np.corrcoef(data_field.flatten(), frame.flatten())[0, 1]
            corr_array.append(corr)
        
        axes[1, 0].plot(np.arange(len(corr_array)) * skip_frames, corr_array, 'g-', linewidth=2)
        line_corr, = axes[1, 0].plot([], [], 'ro', markersize=8)
        axes[1, 0].set_xlabel('Frame Index')
        axes[1, 0].set_ylabel('Correlation')
        axes[1, 0].set_title('Data-Magnetization Correlation')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].set_ylim(-1, 1)
        
        # Energy evolution
        steps = np.arange(len(self.energy_history)) * self.params.save_interval
        axes[1, 1].plot(steps, self.energy_history, 'b-', linewidth=1, alpha=0.5)
        line_energy, = axes[1, 1].plot([], [], 'ro-', linewidth=2, markersize=8)
        axes[1, 1].set_xlabel('Simulation Step')
        axes[1, 1].set_ylabel('Energy (J/area)')
        axes[1, 1].set_title('Energy Evolution')
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].set_xlim(0, steps[-1])
        axes[1, 1].set_ylim(
            np.array(self.energy_history).min() * 1.1,
            np.array(self.energy_history).max() * 0.9
        )
        
        text = fig.text(0.5, 0.02, '', ha='center', fontsize=11, weight='bold')
        
        def animate(frame_idx):
            m_z = frames[frame_idx]
            im2.set_array(m_z)
            
            # Correlation point
            if frame_idx < len(corr_array):
                line_corr.set_data([frame_idx * skip_frames], [corr_array[frame_idx]])
            
            # Energy point
            step_idx = frame_idx * skip_frames
            if step_idx < len(self.energy_history):
                step = step_idx * self.params.save_interval
                energy = self.energy_history[step_idx]
                line_energy.set_data([step], [energy])
            
            # Update text
            step_number = frame_idx * skip_frames * self.params.save_interval
            text.set_text(
                f'Step: {step_number:,} | '
                f'Correlation: {corr_array[frame_idx]:.3f} | '
                f'm_z range: [{np.min(m_z):.2f}, {np.max(m_z):.2f}]'
            )
            
            return im2, line_corr, line_energy, text
        
        anim = animation.FuncAnimation(
            fig, animate, frames=n_frames, interval=1000//fps,
            blit=True, repeat=True
        )
        
        plt.tight_layout(rect=(0, 0.03, 1, 1))
        
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(exist_ok=True, parents=True)
            try:
                anim.save(save_path, writer='ffmpeg', fps=fps)
                print(f"✓ Comparison animation saved to {save_path}")
            except Exception as e:
                print(f"⚠ Could not save MP4: {e}")
        
        return anim
    
    def create_frame_sequence(self, 
                             save_dir: Optional[Path] = None,
                             frame_indices: Optional[List[int]] = None) -> List[Path]:
        """
        Save individual frames as PNG images.
        
        Args:
            save_dir: Directory to save frames
            frame_indices: Specific frame indices to save (default: every 10th frame)
        
        Returns:
            List of saved file paths
        """
        if save_dir is None:
            save_dir = self.output_dir / 'frame_sequence'
        else:
            save_dir = Path(save_dir)
        
        save_dir.mkdir(exist_ok=True, parents=True)
        
        if frame_indices is None:
            frame_indices = list(range(0, len(self.m_z_history), max(1, len(self.m_z_history) // 10)))
        
        saved_files = []
        
        for frame_idx in frame_indices:
            if frame_idx >= len(self.m_z_history):
                continue
            
            m_z = self.m_z_history[frame_idx]
            
            fig, ax = plt.subplots(figsize=(8, 8))
            im = ax.imshow(m_z, cmap='RdBu_r', vmin=-1, vmax=1)
            ax.set_title(f'm_z at Step {frame_idx * self.params.save_interval:,}')
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            plt.colorbar(im, ax=ax, label='m_z')
            
            save_path = save_dir / f'frame_{frame_idx:04d}.png'
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
            plt.close(fig)
            
            saved_files.append(save_path)
        
        print(f"✓ Saved {len(saved_files)} frames to {save_dir}")
        return saved_files
    
    def _save_as_gif(self, anim, save_path: Path):
        """Fallback to save as GIF if ffmpeg not available."""
        try:
            anim.save(save_path, writer='pillow', fps=5)
            print(f"✓ Animation saved as GIF: {save_path}")
        except Exception as e:
            print(f"⚠ Could not save GIF: {e}")


def create_summary_animation_figure(m_z_history: List[np.ndarray],
                                    energy_history: List[float],
                                    data_field: np.ndarray,
                                    save_interval: int,
                                    save_path: Optional[Path] = None) -> Path:
    """
    Create a static figure with key animation frames.
    
    Args:
        m_z_history: List of m_z arrays over time
        energy_history: List of energy values
        data_field: Input data manifold
        save_interval: Steps between saved frames
        save_path: Optional path to save figure
    
    Returns:
        Path to saved figure
    """
    if not m_z_history:
        print("No history available")
        return None
    
    # Select key frames: initial, 25%, 50%, 75%, final
    n_frames = len(m_z_history)
    frame_indices = [
        0,
        n_frames // 4,
        n_frames // 2,
        3 * n_frames // 4,
        n_frames - 1
    ]
    
    fig, axes = plt.subplots(2, 6, figsize=(16, 8))
    
    # Top row: data field (repeated) and m_z frames
    for col, idx in enumerate(frame_indices):
        if col == 0:
            im = axes[0, col].imshow(data_field, cmap='RdBu_r')
            axes[0, col].set_title('Input Data')
        else:
            m_z = m_z_history[idx]
            im = axes[0, col].imshow(m_z, cmap='RdBu_r', vmin=-1, vmax=1)
            step = idx * save_interval
            axes[0, col].set_title(f'Step {step:,}')
        
        axes[0, col].set_xlabel('x')
        axes[0, col].set_ylabel('y')
        plt.colorbar(im, ax=axes[0, col])
    
    # Bottom row: statistics
    for col, idx in enumerate(frame_indices):
        if col == 0:
            # Energy evolution
            steps = np.arange(len(energy_history)) * save_interval
            axes[1, col].plot(steps, energy_history, 'b-', linewidth=2)
            axes[1, col].axvline(frame_indices[1] * save_interval, color='r', linestyle='--', alpha=0.5)
            axes[1, col].axvline(frame_indices[2] * save_interval, color='g', linestyle='--', alpha=0.5)
            axes[1, col].axvline(frame_indices[3] * save_interval, color='m', linestyle='--', alpha=0.5)
            axes[1, col].set_xlabel('Step')
            axes[1, col].set_ylabel('Energy (J/area)')
            axes[1, col].set_title('Energy Evolution')
            axes[1, col].grid(True, alpha=0.3)
        else:
            m_z = m_z_history[idx]
            
            # Statistics for this frame
            stats_text = (
                f'Step: {idx * save_interval:,}\n'
                f'm_z min: {np.min(m_z):.3f}\n'
                f'm_z max: {np.max(m_z):.3f}\n'
                f'm_z mean: {np.mean(m_z):.3f}\n'
                f'm_z std: {np.std(m_z):.3f}\n'
                f'E: {energy_history[idx]:.2e}'
            )
            
            axes[1, col].text(0.5, 0.5, stats_text, ha='center', va='center',
                            fontsize=10, family='monospace',
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            axes[1, col].axis('off')
    
    plt.tight_layout()
    
    if save_path is None:
        save_path = Path('outputs') / 'animation_summary.png'
    else:
        save_path = Path(save_path)
    
    save_path.parent.mkdir(exist_ok=True, parents=True)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"✓ Animation summary saved to {save_path}")
    
    return save_path


if __name__ == '__main__':
    print("Skyrmion Animation Module")
    print("This module creates animations of skyrmion evolution.")
    print("\nUsage:")
    print("  from skyrmion_animation import SkyrmionAnimator")
    print("  animator = SkyrmionAnimator(simulator)")
    print("  animator.create_m_z_evolution_animation(save_path='output.mp4')")
