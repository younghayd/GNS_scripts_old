"""

This script reads in the Excel spreadsheet from Sebastian Naeher containing ramped pyrolysis data
from the GC-MS spectra. The GC-MS outputs a spectra of relative abundance against the retention time of the
GC-MS. Sebastian manually assigns each peak a corresponding compound name and then integrates the peak. Thus,
each peak has a retention time and an integration value. This is obtained for the sample over the full temperature
range, and also over individual temperature ranges. The script will read this data in and group each sample into
a sample category. By summing up the integrations of each category and then finding the relative abundance of each
sample group, the script will plot up the relative abundances for each of the sample types and then save these plot.

"""
# Import packages



# Read in data



# Acquire data parameters (number of temperature splits, list of temperature ranges, etc)



# Reorganise data
    # Select only the identification column and all of the area columns, and rename the area columns (r_full, r_1,
# r_2, etc)
    #


#