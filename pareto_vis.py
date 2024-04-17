import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pareto

def plot_pareto_distribution(shape, scale, num_samples=10000):
    # Generate random samples from the Pareto distribution
    samples = pareto.rvs(shape, scale=scale, size=num_samples)

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot the histogram of the samples
    ax.hist(samples, bins=50, density=True, alpha=0.7, color='blue')

    # Plot the PDF (Probability Density Function) of the Pareto distribution
    x = np.linspace(pareto.ppf(0.01, shape, scale=scale), pareto.ppf(0.99, shape, scale=scale), 100)
    ax.plot(x, pareto.pdf(x, shape, scale=scale), 'r-', lw=2, alpha=0.6, label='PDF')

    # Add labels and title
    ax.set_xlabel('Value')
    ax.set_ylabel('Density')
    ax.set_title(f'Pareto Distribution (shape={shape}, scale={scale})')

    # Add a legend
    ax.legend(loc='best')

    # Show the plot
    plt.tight_layout()
    plt.show()


# Plot the Pareto distribution
plot_pareto_distribution(8, 3)