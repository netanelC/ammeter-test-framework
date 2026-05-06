import os
import matplotlib.pyplot as plt # type: ignore
from typing import List, Optional, Dict
from datetime import datetime

def generate_simple_plot(ammeter_type: str, measurements: List[float], output_dir: str = "results", stats: Optional[Dict[str, float]] = None) -> str:
    """
    Generates a simple, clean, and user-friendly line plot of the current measurements over time.
    Acts like a dashboard panel by including optional statistical reference lines.
    """
    if not measurements:
        return ""

    os.makedirs(output_dir, exist_ok=True)
    
    plt.figure(figsize=(10, 5))
    
    # Simple line plot with markers for clean visualization
    plt.plot(measurements, marker='o', linestyle='-', color='#007acc', linewidth=2, markersize=6, label="Current (A)")
    
    # Dashboard-Style Visualization: Add reference lines if stats are provided
    if stats:
        if 'mean' in stats:
            plt.axhline(y=stats['mean'], color='green', linestyle='--', linewidth=2, label=f"Mean: {stats['mean']:.4f} A")
        if 'max' in stats:
            plt.axhline(y=stats['max'], color='red', linestyle=':', linewidth=2, label=f"Max: {stats['max']:.4f} A")
        
        # Add legend to explain the reference lines
        plt.legend(loc='best', fontsize=10)
    
    plt.title(f"Current Measurements over Time: {ammeter_type.upper()}", fontsize=14, pad=15)
    plt.xlabel("Sample Index", fontsize=12)
    plt.ylabel("Current (A)", fontsize=12)
    
    # User-friendly grid for better readability
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{ammeter_type}_{timestamp}_plot.png"
    filepath = os.path.join(output_dir, filename)
    
    plt.savefig(filepath)
    plt.close()
    
    return filepath
