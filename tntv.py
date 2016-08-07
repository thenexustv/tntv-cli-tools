#!/usr/bin/env python3

from tntv_library import *
import argparse
import traceback
import boto
import boto.s3


def main_meta(args):

    print("\t |=== Meta ===|\n")

    meta_config_path = 'config-meta.yaml'
    if args.meta_config is not None:
        meta_config_path = args.meta_config

    meta_config = get_configuration(meta_config_path)

    if not os.path.exists(meta_config['art_path']):
        print("Album Art path (%s) does not exist" % meta_config['art_path'])
        print("\t=== Error ====")
        sys.exit(-1)
    
    fn = parse_file_name(args.file.name)
    data = {'filename': args.file.name,
            'name': fn['name'],
            'number': fn['number'],
            'title': args.title,
            'members': args.members,
            'args': args
            }

    if args.members is None or len(args.members) <= 0:
        data['members'] = []

    if args.show is not None and args.show in meta_config['shows']:
        data['name'] = args.show

    if args.number is not None and args.number > 0:
        data['number'] = args.number

    data['key'] = find_show_from_dictionary(data['name'], meta_config['shows'])
    show = meta_config['shows'][data['key']]

    print("Setting meta-data for %s ..." % get_title(data, show))

    set_metadata(meta_config, data, show)

    print("\tID3 meta-data saved for %s (file: %s)" % (get_title(data, show), data['filename']))


def main_upload(args):

    print("\t |=== Upload ===|\n")

    meta_config_path = 'config-meta.yaml'
    aws_config_path = 'config-aws.yaml'

    if args.aws_config is not None:
        aws_config_path = args.aws_config
    if args.meta_config is not None:
        meta_config_path = args.meta_config

    aws_config = get_configuration(aws_config_path)
    meta_config = get_configuration(meta_config_path)

    print("Connecting to Amazon S3 (%s)" % aws_config['aws_bucket'])

    connection = boto.connect_s3(aws_config["aws_key"], aws_config["aws_secret"])
    bucket = connection.get_bucket(aws_config['aws_bucket'])

    print("Connected to Amazon S3 (%s)" % aws_config['aws_bucket'])

    count = 0
    files = args.file
    for f in files:
        try:
            upload_file(f, bucket, aws_config=aws_config, meta_config=meta_config, args=args)
            count += 1
            print("\n\tUpload %d of %d completed!\n" % (count, len(files)))
        except:
            print("\n Upload %d of %d failed!\n" % (count, len(files)))


def main_backup(args):

    print("\t |=== Backup ===|\n")

    meta_config_path = 'config-meta.yaml'
    aws_config_path = 'config-aws.yaml'
    backup_config_path = 'config-backup.yaml'

    if args.aws_config is not None:
        aws_config_path = args.aws_config
    if args.meta_config is not None:
        meta_config_path = args.meta_config

    aws_config = get_configuration(aws_config_path)
    meta_config = get_configuration(meta_config_path)
    backup_config = get_configuration(backup_config_path)

    print("Connecting to Amazon S3 (%s)" % aws_config['aws_bucket'])

    connection = boto.connect_s3(aws_config["aws_key"], aws_config["aws_secret"])
    bucket = connection.get_bucket(aws_config['aws_bucket'])

    print("Connected to Amazon S3 (%s)" % aws_config['aws_bucket'])

    data_store = backup_config['data_store']

    runtime = {
        'downloaded': 0,
        'skipped': 0,
        'folders': 0
    }

    try:
        with open(data_store, 'r') as f:
            data = yaml.load(f)
    except IOError:
        print("Data-store (%s) not available, creating new file" % data_store)
        data = {'files': {}, 'refresh': 0}    

    for key in bucket.list(prefix=backup_config['remote_path']):
        # if ZSTOP > ZSTOP_X: break;
        # else: ZSTOP += 1
        try:
            
            if key.name.endswith('/') and key.size == 0:
                print(("Handling remote folder: %s" % key.name))
                runtime['folders'] += 1
                continue

            if key.name in data['files']:
                runtime['skipped'] += 1
                continue

            print("Handling remote file: %s" % key.name)

            destination = "%s/%s" % (backup_config['local_path'], key.name)
            parts = destination.split('/')
            folder = "/".join(parts[:-1])

            try:
                os.makedirs(folder)
            except OSError:
                if os.path.exists(folder):
                    pass
                else:
                    print("Could not create folder structure")
                    raise

            key.get_contents_to_filename(destination, cb=percent_cb, num_cb=100)
            stdout.write("\n")

            checksum = key.etag[1:-1]
            if len(checksum) > 32:
                checksum = checksum[:-2]

            data['files'][key.name] = {'size': key.size, 'checksum': checksum}
            runtime['downloaded'] += 1

        except:
            print("%s failed" % key.name)
            print(traceback.format_exc())

    data['refresh'] += 1

    print("Updating data-store (%s) ..." % data_store)

    with open(data_store, 'w') as f:
        f.write(yaml.safe_dump(data, default_flow_style=False))

    print("\n\tDownloaded %d | Folders %d | Skipped %d | Refreshed %d\n" % (runtime['downloaded'], runtime['folders'],
                                                                            runtime['skipped'], data['refresh']))


def main():

    parser = argparse.ArgumentParser(prog='tntv')
    subparsers = parser.add_subparsers(title='Commands')

    parser_meta = subparsers.add_parser('meta', description='Sets episode meta-data',
                                        help='Set meta-data, adding album art and ID3 tags to an MP3')
    parser_meta.add_argument('file', type=argparse.FileType('r'), help='The episode file to set meta-data on')
    parser_meta.add_argument('title', help='The show title of the episode')
    parser_meta.add_argument('-p', '--parent', type=argparse.FileType('r'),
                             help='The parent episode used to determine The Fringe episode titles')
    parser_meta.add_argument('-m', '--members', nargs='*', help='Additional members to include in the episode authors')
    parser_meta.add_argument('-b', '--blank-members', action='store_true', default=False,
                             help='Only uses the supplied --members list')
    parser_meta.add_argument('-s', '--show', help='Manually set the show type, using the short name of the series')
    parser_meta.add_argument('-n', '--number', type=int, help='Manually set the episode number')
    parser_meta.add_argument('--meta-config', type=argparse.FileType('r'),
                             help='Manually load the meta-data configuration file')
    parser_meta.set_defaults(func=main_meta)

    parser_upload = subparsers.add_parser('upload', description='Upload an MP3 file to Amazon S3',
                                          help='Upload files to Amazon S3 hosting')
    parser_upload.add_argument('file', type=argparse.FileType('r'), nargs='+', help='MP3 files to upload')
    parser_upload.add_argument('--aws-config', type=argparse.FileType('r'), dest='aws_config',
                               help='Manually set the AWS configuration file')
    parser_upload.add_argument('--meta-config', type=argparse.FileType('r'), dest='meta_config',
                               help='Manually set the meta-data configuration file')
    parser_upload.set_defaults(func=main_upload)

    parser_backup = subparsers.add_parser('backup', description='Handle automated backup of remote S3 files',
                                          help='Backup files from S3')
    parser_backup.add_argument('--aws-config', type=argparse.FileType('r'), dest='aws_config',
                               help='Manually set the AWS configuration file')
    parser_backup.add_argument('--meta-config', type=argparse.FileType('r'), dest='meta_config',
                               help='Manually set the meta-data configuration file')
    parser_backup.set_defaults(func=main_backup)

    args = parser.parse_args()
    args.func(args)

main()
