
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import skewnorm, norm  # Import norm
from scipy.special import erfc

# Load the CSV file
try:
    df = pd.read_csv(r"data\pmt_spectroscopy\vp2ps_20250320-181313_co60_12h_20cm.csv")  # Replace with your actual file path
except FileNotFoundError:
    print("Error: co60.csv not found.")
    exit()

df.columns = ["index", "t", "V"]
df["mV"] = df["V"] * 1000
bin_width = 4
lower_bound = 80
upper_bound = 1000
bins = np.arange(lower_bound - bin_width / 2, upper_bound + bin_width / 2, bin_width)
filtered_df = df[(df["mV"] >= lower_bound) & (df["mV"] <= upper_bound)]

# Get histogram data
counts, bin_edges = np.histogram(filtered_df["mV"], bins=bins)
bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2


# --- Fitting Functions ---

def skewed_gaussian(x, A, mu, sigma, skew):
    """Skewed Gaussian with tail"""
    skewed_gauss = A * skewnorm.pdf(x, skew, loc=mu, scale=sigma)
    return skewed_gauss
    

def total_fit_function(x, A1, mu1, sigma1, skew1):#, A2, mu2, sigma2, A3, mu3, sigma3, A4, mu4, sigma4):
    """Combines a skewed Gaussian with tail and three regular Gaussians."""
    return skewed_gaussian(x, A1, mu1, sigma1, skew1) 
            # 0*norm.pdf(x, loc=mu2, scale=sigma2) * A2 +  # Use norm.pdf
            # 0*norm.pdf(x, loc=mu3, scale=sigma3) * A3 +
            # 0*norm.pdf(x, loc=mu4, scale=sigma4) * A4)



# --- Initial Guesses and Bounds ---
# guesses and bounds as tuples in format (min, guess, max)

A1 = (1000, 1500, 3000)
mu1 = (200, 230, 3000)
sigma1 = (5, 8, 1000)
skew1 = (0, 6, 200)

params = [
    A1, mu1, sigma1, skew1,
]

for p in params:
    if p[1] < p[0] or p[1] > p[2]:
        print("Initial guess out of bounds. Check your initial guesses.")
        print(p)
        exit()


initial_guesses = [p[1] for p in params]

# Bounds
#               A1,  mu1, sigma1,  skew1,    A2,  mu2, sigma2,   A3,  mu3, sigma3,     A4,  mu4, sigma4
lower_bounds = [p[0] for p in params]
upper_bounds = [p[2] for p in params]

bounds = (lower_bounds, upper_bounds)



# --- Perform the Fit ---
try:
    popt, pcov = curve_fit(total_fit_function, bin_centers, counts, p0=initial_guesses, bounds=bounds, maxfev=10000)

    perr = np.sqrt(np.diag(pcov))

    # --- Plotting ---
    plt.figure(figsize=(10, 6))
    plt.hist(filtered_df["mV"], bins=bins, edgecolor='black', label="Data")

    x_fit = np.linspace(lower_bound, upper_bound, 1000)
    y_fit = total_fit_function(x_fit, *popt)
    plt.plot(x_fit, y_fit, 'r-', label="Total Fit", linewidth=2)

    y_fit_peak1 = skewed_gaussian(x_fit, *popt[:4])  # First 6 parameters
    # y_fit_peak2 = norm.pdf(x_fit, loc=popt[5], scale=popt[6]) * popt[4]  # Use norm.pdf and scale by amplitude
    # y_fit_peak3 = norm.pdf(x_fit, loc=popt[8], scale=popt[9]) * popt[7]
    # y_fit_peak4 = norm.pdf(x_fit, loc=popt[11], scale=popt[12]) * popt[10]


    plt.plot(x_fit, y_fit_peak1, 'g--', label="Peak 1 (Background)", linewidth=1.5)
    # plt.plot(x_fit, y_fit_peak2, 'b--', label="Peak 2 (Annihilation)", linewidth=1.5)
    # plt.plot(x_fit, y_fit_peak3, 'm--', label="Peak 3 (Co-60 Peak 1)", linewidth=1.5)
    # plt.plot(x_fit, y_fit_peak4, 'c--', label="Peak 4 (Co-60 Peak 2)", linewidth=1.5)

    plt.xlabel("Voltage (mV)")
    plt.ylabel("Frequency")
    plt.title("Histogram of Co-60 Voltage Data with Fit")
    plt.xlim(lower_bound, upper_bound)
    plt.legend()
    plt.grid(True)
    plt.yscale("linear")

    print("Fit Results:")
    param_names = ["A1", "mu1", "sigma1", "skew1", "A2", "mu2", "sigma2", "A3", "mu3", "sigma3", "A4", "mu4", "sigma4"]
    for i, param_name in enumerate(param_names[:4]):
        print(f"{param_name}: {popt[i]:.3f} ± {perr[i]:.3f}")

    plt.show()

except RuntimeError as e:
    print(f"Fit failed: {e}")
    plt.figure(figsize=(10, 6))
    plt.hist(filtered_df["mV"], bins=bins, edgecolor='black', label="Data")
    plt.xlabel("Voltage (mV)")
    plt.ylabel("Frequency")
    plt.title("Histogram of Co-60 Voltage Data (Fit Failed)")
    plt.xlim(lower_bound, upper_bound)
    plt.legend()
    plt.grid(True)
    plt.show()