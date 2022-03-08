#!/usr/bin/env python3

import sys
from sys import stdout
from boto.s3.key import Key
import yaml
import re
import mutagen.id3
from mutagen.id3 import ID3, TIT2, TALB, TCOM, TCON, TDRC, TPE1, TPE2, TRCK, APIC, TPUB
from datetime import date
import os
import boto3
import botocore
import sys
import threading


# From http://boto3.readthedocs.io/en/stable/guide/s3.html
class ProgressPercentage(object):
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)"
                % (self._filename, self._seen_so_far, self._size, percentage)
            )
            sys.stdout.flush()


def get_configuration(file):
    f = open(file)
    data = yaml.safe_load(f)
    return data


def join_and(li):
    if len(li) <= 2:
        return " and ".join(li)
    else:
        return ", ".join(li[:-1]) + (", and " + li[-1])


def parse_file_name(name):
    filename = name.split("/")
    parts = filename[-1].split(".")
    string = parts[0]
    number = re.sub("[^0-9]", "", string)
    short = re.sub("[0-9]", "", string)
    return {"name": short, "number": number}


def get_filename_from_path(filename):
    # assume the filename is a path
    # this ensures that it is actually a name
    parts = filename.split("/")
    return parts[-1]


def find_show_from_dictionary(name, shows):
    for key, show in shows.items():
        if name == show["short"]:
            return key
    return "xx"


# Hey look, in line file upload progress!
def percent_cb(complete, total):
    percent = round((float(complete) / float(total)) * 100)
    progress = int(percent / 5)
    str_progress = "-" * progress
    str_spaces = " " * (20 - progress)
    stdout.write("\r%d%%   |%s%s|" % (percent, str_progress, str_spaces))
    stdout.flush()


def get_title(data, show):
    title = "%s #%d: %s" % (show["formal"], int(data["number"]), data["title"])
    return title


# http://stackoverflow.com/a/33843019/3928053
def key_exists(s3, bucket, key):
    try:
        s3.head_object(Bucket=bucket, Key=key)
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        else:
            raise e
    else:
        return True


def write_tags(audio, config, data, show):

    if "blank_members" in data["args"] and data["args"].blank_members:
        print("\tNotice: --blank-members specified; only using named members")
        members = data["members"]
    else:
        members = show["members"] + data["members"]

    genre = "Podcast"

    title = get_title(data, show)
    album = show["formal"]
    composer = config["composer"]

    year = str(date.today().year)

    track_artist = join_and(members)
    album_artist = config["artist"]
    track_number = str(data["number"])
    album_art = config["art_path"] + show["album_art"]

    if not os.path.exists(album_art):
        print("File path %s does not locate a valid album art file." % album_art)
        print("\t=== Error ===")
        sys.exit(-1)

    print("ID3 Metadata:")
    print("\tTitle: %s" % title)
    print("\tGenre: %s" % genre)
    print("\tNumber: %s" % track_number)
    print("\tMembers: %s" % track_artist)

    tit2 = TIT2(encoding=3, text=title)
    talb = TALB(encoding=3, text=album)
    tcom = TCOM(encoding=3, text=composer)
    tcon = TCON(encoding=3, text=genre)
    tdrc = TDRC(encoding=3, text=year)
    tpe1 = TPE1(encoding=3, text=track_artist)
    tpe2 = TPE2(encoding=3, text=album_artist)
    trck = TRCK(encoding=3, text=track_number)
    tpub = TPUB(encoding=3, text=album_artist)

    image = open(album_art, "rb").read()
    apic = APIC(3, "image/jpg", 3, "Front cover", image)

    print("Writing tags...")

    frames = [tit2, talb, tcom, tcon, tdrc, tpe1, tpe2, tpub, trck, apic]

    for frame in frames:
        audio.add(frame)


def set_metadata(config, data, show):

    # load the existing tags or create a new tag container
    try:
        audio = ID3(data["filename"])
    except mutagen.id3.ID3NoHeaderError:
        audio = ID3()
        print("No existing ID3 tags found...")
        print("Creating frames...")

    # save the tags
    write_tags(audio, config, data, show)

    # save the tags
    print("Attempting to save tags...")
    audio.save(data["filename"])


def upload_file(file, s3, aws_config, meta_config, args):
    print("Verifying local file %s" % file.name)

    if not file.name.lower().endswith(".mp3"):
        print("The file (%s) does not have the MP3 extension")
        print("\t=== Error ===")
        return

    if os.path.getsize(file.name) < 0:
        print("The file (%s) has no file size" % file.name)
        print("\t=== Error ===")
        return

    fn = parse_file_name(file.name)
    key = "%s%s/%s" % (
        aws_config["aws_path"],
        fn["name"],
        get_filename_from_path(file.name),
    )

    print("Verifying remote file %s" % key)

    if key_exists(s3=s3, bucket=aws_config["aws_bucket"], key=key):
        print("The remote file (%s) already exists" % key)
        print("Please use the Amazon S3 web explorer to handle conflict")
        print("\t=== Error ===")
        return

    print("Uploading %s (local) to %s (remote)" % (file.name, key))

    s3.upload_file(
        file.name, aws_config["aws_bucket"], key, Callback=ProgressPercentage(file.name)
    )
    print()

    print("Adding 'public-read' ACL to remote file (%s)" % key)

    s3.put_object_acl(Bucket=aws_config["aws_bucket"], Key=key, ACL="public-read")

    # This seems hacky, boto3 doesn't seem to have a good way to do this yet
    url = "{aws}/{key}".format(aws=s3.meta.endpoint_url, key=key)
    http_url = url.replace("https://", "http://" + aws_config["aws_bucket"] + ".")

    print("Access file: %s" % http_url)
