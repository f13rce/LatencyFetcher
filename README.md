# LatencyFetcher
Grab latency of continents their web servers based on its top visited sites

# Usage

Open the fetchlatency.py file and edit the ``countries`` array to include countries you want to test. Countries are listed a country abbreviations with a length of 2, e.g.: NL, US, CA, CN, AU.

Then run the file: ``python3 fetchlatency.py``

# Requirements

A Linux distro, since every ``os.system`` and ``os.popen`` command is Linux-specific (``curl``, ``rm``, etc).

# Results

Output will give you a results-$DATE.csv file listing all the countries with their median, mean, min, max ping, sample size and websites it was able to test (that originate from the same country).
