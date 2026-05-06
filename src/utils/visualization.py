import matplotlib.pyplot as plt # type: ignore
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

def generate_simple_plot(ammeter_type: str, measurements: List[float], output_dir: str = "results", stats: Optional[Dict[str, float]] = None) -> str:
    """
    Generates a simple, clean, and user-friendly line plot of the current measurements over time.
    Uses Matplotlib's Object-Oriented API for thread-safe plotting.
    """
    if not measurements:
        return ""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Simple line plot with markers
    ax.plot(measurements, marker='o', linestyle='-', color='#007acc', linewidth=2, markersize=6, label="Current (A)")
    
    # Dashboard-Style Visualization: Add reference lines if stats are provided
    if stats:
        if 'mean' in stats:
            ax.axhline(y=stats['mean'], color='green', linestyle='--', linewidth=2, label=f"Mean: {stats['mean']:.4f} A")
        if 'max' in stats:
            ax.axhline(y=stats['max'], color='red', linestyle=':', linewidth=2, label=f"Max: {stats['max']:.4f} A")
        
        ax.legend(loc='best', fontsize=10)
    
    ax.set_title(f"Current Measurements over Time: {ammeter_type.upper()}", fontsize=14, pad=15)
    ax.set_xlabel("Sample Index", fontsize=12)
    ax.set_ylabel("Current (A)", fontsize=12)
    
    # User-friendly grid for better readability
    ax.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{ammeter_type}_{timestamp}_plot.png"
    filepath = output_path / filename
    
    fig.savefig(filepath)
    plt.close(fig)
    
    return str(filepath)
