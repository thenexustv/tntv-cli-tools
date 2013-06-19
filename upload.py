
from sys import stdout
import boto
import boto.s3
from boto.s3.key import Key
import yaml
import argparse
import re

quiet_output = False

def output_hook(string):
	if not quiet_output:
		print string

def get_data(file):
	f = open(file)
	data = yaml.load(f)
	return data;

def get_arguments():
	parser = argparse.ArgumentParser(description="Upload an MP3 file to S3")
	parser.add_argument('file', type=file, help="The MP3 episode file to upload")
	parser.add_argument('--quiet', dest='quiet', action='store_true', help="Display no output")
	parser.add_argument('-p', '--path', help="Override the destination of the MP3 on the S3 server")
	parser.add_argument('--aws-data', dest="aws_data", help="Override the configuration file for AWS creditials")
	parser.add_argument('--meta-data', dest="meta_data", help="Override the configuration file for Meta settings")

	return parser.parse_args()

# Hey look, in line file upload progress!
def percent_cb(complete, total):
	if quiet_output:
		return # this will skip print this entirely
	stdout.write( "\r%d%%" % round( ( float(complete) / float(total) ) * 100 ) )
	stdout.flush()

# really should make a little helper functions library
# TODO: ^
def parse_file_name(name):
	filename = name.split('/')
	parts = filename[-1].split('.')
	string = parts[0]
	number = re.sub('[^0-9]', '', string)
	short = re.sub('[0-9]', '', string)
	return {'name': short, 'number': number}

def get_filename(filename):
	# assume the filename is a path
	# this ensures that it is actually a name
	parts = filename.split('/')
	return parts[-1]

def main():

	aws_data_path = 'config-aws.yaml'
	meta_data_path = 'config-meta.yaml'
	args = get_arguments()
	if args.aws_data is not None:
		aws_data_path = args.aws_data
	if args.meta_data is not None:
		meta_data_path = args.meta_data

	aws_data = get_data(aws_data_path)
	meta_data = get_data(meta_data_path)

	output_hook("Connecting to S3...")

	connection = boto.connect_s3(aws_data["aws_key"], aws_data["aws_secret"])
	bucket = connection.get_bucket(aws_data['aws_bucket'])

	output_hook("Checking file...")

	local_filename = args.file.name

	if not local_filename.lower().endswith('.mp3'):
		print "There is no MP3 extension on supplied file!\n\n"
		return

	fn = parse_file_name(local_filename)
	remote_filename = aws_data['aws_path'] + fn['name'] + "/" + get_filename(local_filename)
	
	output_hook("Remote destination is " + remote_filename)

	output_hook("Checking remote destination...")


	k = Key(bucket)
	k.key = remote_filename

	# Do not ever let files get _overwritten_
	# This is a core principle; it will always be worth doing it by hand
	# If there is any suspicion that a file already exists.
	if k.exists():
		print "The file already exists: ", remote_filename
		print "Please use the web explorer to handle this conflict case!"
		return
	else:
		print "Ready to upload..."

	output_hook("Uploading file " + local_filename + " to ~s3/" + remote_filename)
	k.set_contents_from_filename(local_filename, cb = percent_cb, num_cb = 100, replace = False)
	# this makes input move to the next line
	if not quiet_output:
		stdout.write("\n")
	
	output_hook("Marking file " + remote_filename + " as public")
	k.make_public()

	print "Done!"


# ---
main()