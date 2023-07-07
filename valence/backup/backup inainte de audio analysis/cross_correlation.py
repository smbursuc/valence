import numpy as np
from scipy.signal import correlate

# Generate two example sequences of rhythmic features
sequence1 = np.array([0, 1, 2, 3, 4, 5])  # Example sequence 1
sequence2 = np.array([2, 3, 4, 5, 6, 7])  # Example sequence 2

# Compute cross-correlation between the two sequences
cross_corr = correlate(sequence1, sequence2, mode='valid')

# Find the index of the maximum cross-correlation value
max_corr_idx = np.argmax(cross_corr)

# Calculate the time shift or alignment between the two sequences
time_shift = max_corr_idx - (len(sequence1) - 1)

# Print the result
print("Cross-correlation: ", cross_corr)
print("Time shift: ", time_shift)
