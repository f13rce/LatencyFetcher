##########################
# Latency fetcher	 #
##########################

# Imports
import datetime
import time
import os
import json

# Globals
now = datetime.datetime.now()
dateStr = "{}-{}-{}-{}h{}m{}s".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
resultsFile = "results-{}.csv".format(dateStr)

countries = ["US", "NL", "CN", "JP", "AU"] # Needs to have this at the end
pingCountPerWebsite = 10
userAgent = "Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0"

# Classes
class IPInfo:
	ip = ""
	country = ""
	region = ""
	city = ""

# Funcs
def GetTime():
	# Returns time in ms
	return int(round(time.time() * 1000))

def GetPingTimes(aWebsiteURL, aFilter):
	times = []

	try:
		# Perform ping
		print("Pinging {}...".format(aWebsiteURL))
		pings = os.popen("ping4 {} -c {}".format(aWebsiteURL, pingCountPerWebsite)).read()
		pings = pings.split("\n")
		print("Done!")

		# Fetch IP info
		ip = pings[0].split("(")[1].split(")")[0]
		print("\tFetching IP information from the server of {} ({})...".format(aWebsiteURL, ip))
		info = GetIPInformation(ip)

		# Process ping info if it's compliant to our filter
		print("\tChecking if {} ({}) matches the filter ({})...".format(ip, info.country, aFilter))
		if info.country == aFilter:
			print("\tIP {} ({}) matches the filter ({}). Proceeding.".format(ip, info.country, aFilter))
			i = 0
			while i < pingCountPerWebsite:
				# Add +1 to pings[i] because the first line is the message where we're pinging to
				if "time=" in pings[i+1]:
					# Get number between: time=1.18 ms
					ms = pings[i+1].split("time=")[1].split(" ")[0]
					ms = float(ms)
					times.append(ms)
				i += 1
		else:
			print("Website {} is originated in a different country ({}). Will skip this one.".format(aWebsiteURL, info.country))
	except KeyboardInterrupt:
		print("\tDetected keyboard interrupt - will stop.")
	except IndexError:
		print("\tSeems like {} ({}) has disabled ICMP, or is unreachable. Ignoring this site...".format(aWebsiteURL, ip))
		pass
	except Exception as e:
		print("\tSomething went wrong when processing {}. Error: '{}'. Will skip this one.".format(aWebsiteURL, repr(e)))
		pass

	return times

def GetIPInformation(aIP):
	print("\t\tFetching IP info from ipinfo.io...")
	url = 'https://ipinfo.io/{}/json'.format(aIP)
	response = os.popen("curl {}".format(url))
	print("\t\tParsing result to JSON...")
	data = json.load(response)

	print("\t\tStoring data into class...")
	ii = IPInfo()
	ii.ip = data["ip"]
	ii.country = data["country"]
	ii.region = data["region"]
	ii.city = data["city"]

	print("\t\tDone! IP: {} | Country: {} | Region: {} | City: {}".format(ii.ip, ii.country, ii.region, ii.city))
	return ii

def GetWebsiteList(aCountry):
	url = "https://www.alexa.com/topsites/countries/{}".format(aCountry)

	print("Fetching list of {} countries ({})...".format(aCountry, url))
	#page = os.popen("curl --user-agent '{}' {}".format(userAgent, url))
	os.system("wget {}".format(url))

	page = ""
	with open("{}".format(aCountry), "r") as f:
		page = f.read()

	print("\tParsing result...")
	page = str(page)
	page = page.replace(">", "<").split("<")
	searchStr = 'class="tr site-listing"'

	urls = []
	for i in range(len(page)):
		if searchStr in page[i]:
			# Fetch URL
			url = page[i+11]
			urls.append(url)

	print("Done! Fetched {} URLs.".format(len(urls)))
	return urls

def ParseResults(aCountry, aPings, aWebsites):
	total = 0
	high = 0
	low = 9999999

	for ping in aPings:
		total += ping

		if ping < low:
			low = ping
		if ping > high:
			high = ping

	mean = total / len(aPings)

	aPings.sort() # Get proper median
	median = aPings[round(len(aPings) / 2)]

	with open(resultsFile, "a") as f:
		f.write("{}, {}, {}, {}, {}, {}, {}, {}\n".format(aCountry, (mean + median) / 2, mean, median, high, low, len(aPings), repr(aWebsites)))

# Create results file
with open(resultsFile, "w") as f:
	f.truncate()
	f.write("Country, Mean(Mean + Median / 2), Mean, Median, High, Low, Sample size, Websites\n")

c = 0
for country in countries:
	# Logging
	c += 1
	print("==================================")
	print("= Fetching country {} / {} ({})... =".format(c, len(countries), country))
	print("==================================")

	# Fetch list of websites based off Alexa's ranking
	pings = []
	websites = []
	urls = GetWebsiteList(country)

	# Get results per site
	uc = 0
	for url in urls:
		uc += 1

		# Print progress
		str = "* Getting ping data from {} ({}/{})... *".format(url, uc, len(urls))
		starStr = ""
		for i in range(len(str)):
			starStr += "*"

		print(starStr)
		print(str)
		print(starStr)

		res = GetPingTimes(url, country)
		if res:
			for ping in res:
				pings.append(ping)
			websites.append(url)

	# Parse results
	if pings:
		ParseResults(country, pings, websites)
	else:
		print("============== WARNING: Somehow, we have no results for {}! ==============".format(country))

	# Clean up :)
	os.system("rm {}".format(country))
