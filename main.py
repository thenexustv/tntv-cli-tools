
from mutagen.mp3 import MP3
from mutagen.id3 import *
from mutagen.id3 import TIT2, TALB, TCOM, TCON, TDRC, TPE1, TPE2, TRCK, APIC
from datetime import date
import yaml
import argparse
import re

def join_and(li):
	if len(li) <= 2:
		return ' and '.join(li)
	else:
		return ', '.join(li[:-1]) + (' and ' + li[-1])

def parse_file_name(name):
	parts = name.split('.')
	string = parts[0]
	number = re.sub('[^0-9]', '', string)
	short = re.sub('[0-9]', '', string)
	return {'name': short, 'number': number}

def find_show(name, shows):
	for key, show in shows.iteritems():
		if name == show['short']:
			return key
	return 'xx'

def get_arguments():
	parser = argparse.ArgumentParser(description='Sets episode metadata')
	parser.add_argument('file', type=file)
	parser.add_argument('title')
	parser.add_argument('-m', '--members', nargs='*')

	return parser.parse_args()

def set_metadata(file, show, title, members=[]):
	audio = ID3(file)
	fn = parse_file_name(file)
	members = show['members'] + members

	formal_title = show['formal'] + ' #' + fn['number'] + ": " + title 
	album = show['formal']
	composer = 'Ryan Rampersad' # make some kind of option for this?
	genre = 'podcast'
	year = str(date.today().year)
	track_artist = join_and(members)
	album_artist = 'The Nexus TV'
	track_number = fn['number']

	tit2 = TIT2(encoding=3, text=formal_title)
	talb = TALB(encoding=3, text=album)
	tcom = TCOM(encoding=3, text=composer)
	tcon = TCON(encoding=3, text=genre)
	tdrc = TDRC(encoding=3, text=year)
	tpe1 = TPE1(encoding=3, text=track_artist)
	tpe2 = TPE2(encoding=3, text=album_artist)
	trck = TRCK(encoding=3, text=track_number)

	elements = [tit2, talb, tcom, tcon, tdrc, tpe1, tpe2, trck]
	for element in elements:
		audio.add(element)
	audio.save()

	print "Done!"
	# print audio.pprint()

def get_data(file):
	f = open(file)
	data = yaml.load(f)
	return data;

def main():
	args = get_arguments()

	filename = args.file.name
	fn = parse_file_name(filename)
	title = args.title

	# massage the members array; pass in an empty list otherwise
	members = args.members
	if args.members is None or len(args.members) <= 0:
		members = []

	data = get_data('shows.yaml')

	show_key = find_show(fn['name'], data['shows'])
	show = data['shows'][show_key]

	set_metadata(args.file.name, show, title, members=members)


# ---
main()