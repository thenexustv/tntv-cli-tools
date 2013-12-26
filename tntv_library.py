import argparse
import sys
from sys import stdout
import boto
import boto.s3
from boto.s3.key import Key
import yaml
import re
import mutagen.id3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TALB, TCOM, TCON, TDRC, TPE1, TPE2, TRCK, APIC, TPUB
from datetime import date
import os

def get_configuration(file):
	f = open(file)
	data = yaml.load(f)
	return data

def join_and(li):
	if len(li) <= 2:
		return ' and '.join(li)
	else:
		return ', '.join(li[:-1]) + (' and ' + li[-1])

def parse_file_name(name):
	filename = name.split('/')
	parts = filename[-1].split('.')
	string = parts[0]
	number = re.sub('[^0-9]', '', string)
	short = re.sub('[0-9]', '', string)
	return {'name': short, 'number': number}

def get_filename_from_path(filename):
	# assume the filename is a path
	# this ensures that it is actually a name
	parts = filename.split('/')
	return parts[-1]

def find_show_from_dictionary(name, shows):
	for key, show in shows.iteritems():
		if name == show['short']:
			return key
	return 'xx'

# Hey look, in line file upload progress!
def percent_cb(complete, total):
	percent = round( ( float(complete) / float(total) ) * 100 )
	progress = int(percent / 5)
	str_progress = "-" * progress
	str_spaces = " " * (20 - progress)
	stdout.write( "\r%d%%   |%s%s|" % (percent, str_progress, str_spaces) )
	stdout.flush()

def get_title(data, show):
	title = "%s #%d: %s" % (show['formal'], int(data['number']), data['title'])
	return title

def write_tags(audio, config, data, show):

	members = show['members'] + data['members']

	genre = 'Podcast'

	title = get_title(data, show)
	album = show['formal']
	composer = config['composer']
	
	year = str(date.today().year)

	track_artist = join_and(members)
	album_artist = config['artist']
	track_number = str(data['number'])
	album_art = config['art_path'] + show['album_art']

	if not os.path.exists(album_art):
		print "File path %s does not locate a valid album art file." % (album_art)
		print "\t=== Error ==="
		sys.exit(-1)

	print "Meta-data:"
	print "\tTitle: %s" % (title)
	print "\tGenre: %s" % (genre)
	print "\tNumber: %s" % (track_number)
	print "\tMembers: %s" % (track_artist)

	tit2 = TIT2(encoding=3, text=title)
	talb = TALB(encoding=3, text=album)
	tcom = TCOM(encoding=3, text=composer)
	tcon = TCON(encoding=3, text=genre)
	tdrc = TDRC(encoding=3, text=year)
	tpe1 = TPE1(encoding=3, text=track_artist)
	tpe2 = TPE2(encoding=3, text=album_artist)
	trck = TRCK(encoding=3, text=track_number)
	tpub = TPUB(encoding=3, text=album_artist)

	image = open(album_art, 'rb').read()
	apic = APIC(3, 'image/jpg', 3, 'Front cover', image)

	print "Writing tags..."

	elements = [tit2, talb, tcom, tcon, tdrc, tpe1, tpe2, tpub, trck, apic]

	for element in elements:
		audio.add(element)


def set_metadata(config, data, show):

	# load the existing tags or create a new tag container
	try:
		audio = ID3( data['filename'] )
	except mutagen.id3.ID3NoHeaderError:
		audio = ID3()
		output_hook("No existing ID3 tags found...")
		output_hook("Creating frames...")

	# save the tags
	write_tags(audio, config, data, show)

	# save the tags
	print "Attempting to save tags..."
	audio.save( data['filename'] )

def upload_file(file, bucket, aws_config, meta_config, args):
	print "Verifying local file %s" % (file.name)

	if not file.name.lower().endswith('.mp3'):
		print "The file (%s) does not have the MP3 extension"
		print "\t=== Error ==="
		return

	if os.path.getsize(file.name) < 0:
		print "The file (%s) has no file size" % (file.name)
		print "\t=== Error ==="
		return

	fn = parse_file_name(file.name)
	remote_file = "%s%s/%s" % (aws_config['aws_path'], fn['name'], get_filename_from_path(file.name))

	# refers to upload path
	# if args.path is not None:
	# 	remote_file = args.path

	print "Verifying remote file %s" % (remote_file)

	k = Key(bucket)
	k.key = remote_file

	if k.exists():
		print "The remote file (%s) already exists" % (remote_file)
		print "Please use the Amazon S3 web explorer to handle conflict"
		print "\t=== Error ==="
		return
	
	print "Ready to upload %s (local) to %s (remote)" % (file.name, remote_file)
	
	k.set_contents_from_filename(file.name, cb = percent_cb, num_cb = 100, replace = False)
	
	# this makes input move to the next line
	stdout.write("\n")

	print "Marking remote file (%s) as Public" % (remote_file)
	k.make_public()

	print "Completed\n\n"

