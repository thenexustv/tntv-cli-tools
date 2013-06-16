
import argparse
import re

class Meta(object):
	def __init__(self, formal="", short="", members=["Nexus Team"]):
		self.formal = formal
		self.short = short;
		self.members = members

def parse_file_name(name):
	parts = name.split(".")
	string = parts[0]
	number = re.sub('[^0-9]', '', string)
	short = re.sub('[0-9]', '', string)
	return {"name": short, "number": number}

def find_show(name, shows):
	for show in shows:
		# print name , " == " , show.short
		if name == show.short:
			return show
	return shows[-1]

def main():
	
	parser = argparse.ArgumentParser(description="Sets episode metadata")
	parser.add_argument('file', type=file)
	parser.add_argument('title')
	parser.add_argument("-m", "--members", nargs="*")

	args = parser.parse_args()

	filename = args.file.name
	fn = parse_file_name(filename)
	
	atn = Meta("At The Nexus", "atn", ["Ryan Rampersad", "Matthew Petschl"])
	eb = Meta("Eight Bit", "eb", ["Ian Buck", "Ian Decker"])
	cs = Meta("Control Structure", "cs", ["Andrew Bailey", "Christopher Thompson"])
	ns = Meta("Nexus Special", "ns")
	tu = Meta("The Universe", "tu", ["Sam Ebertz", "Ryan Rampersad"])
	tf = Meta("The Fringe", "tf")
	xx = Meta("Unknown", "xx", ["Literally No One"])

	shows = [atn, eb, cs, ns, tu, tf]

	print find_show(fn["name"], shows)

# ---
main()