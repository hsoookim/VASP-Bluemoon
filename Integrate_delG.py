import sys
import numpy as np
import matplotlib.pyplot as plt


def calculate_block_error(file_path, block_size=1000):
    """
    Read a force time-series and return (mean, standard error)
    using block averaging.
    """
    data = np.loadtxt(file_path)
    n_total = len(data)
    n_blocks = n_total // block_size

    if n_blocks < 2:
        # Simulation too short to block; use a simple estimate instead.
        return np.mean(data), np.std(data) / np.sqrt(n_total)

    truncated = data[:n_blocks * block_size]
    blocks = truncated.reshape((n_blocks, block_size))
    block_means = np.mean(blocks, axis=1)

    mean_force = np.mean(block_means)
    block_sem = np.std(block_means, ddof=1) / np.sqrt(n_blocks)
    return mean_force, block_sem


def read_data(metadata_file, block_size=1000):
    """
    Read the metadata file. Each line is one of:

        [dir]  [coord]  [path_to_file.dat]
        [dir]  [coord]  [mean_force]  [error]
    """
    image, r, delG, errors = [], [], [], []

    with open(metadata_file) as f:
        for line in f:
            row = line.split()
            if not row:
                continue  # skip empty lines

            dir_name = row[0]
            coord = float(row[1])

            if row[2].endswith('.dat'):
                # Compute mean force + error from the time-series file.
                mean_force, error = calculate_block_error(row[2], block_size)
            else:
                # Values are given directly in the metadata file.
                mean_force = float(row[2])
                error = float(row[3])

            image.append(dir_name)
            r.append(coord)
            delG.append(mean_force)
            errors.append(error)

    return image, np.array(r), np.array(delG), np.array(errors)


def plot_mean_force(r, delG, errors):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.errorbar(r, delG, yerr=errors, fmt='o', fillstyle='none', color='black')
    ax.axhline(0, color='black', linestyle='--')
    ax.set_xlabel("Coordinate")
    ax.set_ylabel(r"Mean Force (eV/$\AA$)")
    ax.set_title("Mean Force vs Coordinate")
    fig.tight_layout()
    fig.savefig('mean_force.png', dpi=200)
    return fig, ax


def plot_free_energy(r, G, G_errors):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(r, G, marker='o', markersize=4, linestyle='-', color='black')
    ax.fill_between(r, G - G_errors, G + G_errors, color='gray', alpha=0.3)
    ax.set_xlabel("Reaction Coordinate")
    ax.set_ylabel("G (eV)")
    ax.set_title("Free Energy vs Coordinate")
    fig.tight_layout()
    fig.savefig('free_energy.png', dpi=200)
    return fig, ax


def integrate_and_plot(file_path):
    image, r, delG, errors = read_data(file_path, block_size=1000)

    # Trapezoidal integration of the mean force -> free energy,
    # propagating the variance at each step.
    G = [0.0]
    variance = [0.0]

    for i in range(1, len(r)):
        dr = r[i] - r[i - 1]

        step_G = 0.5 * (delG[i] + delG[i - 1]) * dr
        G.append(G[-1] + step_G)

        step_var = (0.5 * dr) ** 2 * (errors[i] ** 2 + errors[i - 1] ** 2)
        variance.append(variance[-1] + step_var)

    G = np.array(G)
    G_errors = np.sqrt(variance)

    # Shift so the minimum free energy is zero (reference point).
    G = G - G.min()

    print("\n--- Integrated free energy ---")
    for ri, Gi, ei in zip(r, G, G_errors):
        print(f"r = {ri:.4f}, G = {Gi:.6f} +/- {ei:.6f} eV")

    plot_mean_force(r, delG, errors)
    plot_free_energy(r, G, G_errors)
    print("\nSaved: mean_force.png, free_energy.png")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python integrate.py <data_file>")
        sys.exit(1)

    integrate_and_plot(sys.argv[1])
