#!/usr/bin/env python3
from optparse import OptionParser
import os
import locale
import datetime


locale. setlocale(locale.LC_ALL, '')


def args_parse(args):
    parsed_args =[]
    if not args:
        parsed_args = "."
    elif args == "..":
        parsed_args.append(args)
    else:
        for arg in args:
            if arg.endswith("/") or arg.endswith("\\"):
                arg = arg[:-1]
            parsed_args.append(arg)
    return parsed_args


def file_list_create(options):
    if options.recursive:
        def get_file_list(args):
            if 'win' in os.uname().sysname.lower():
                slash = '\\'
            else:
                slash = '/'
            folder = []
            file_list = []
            for arg in args:
                for i in os.walk(arg):
                    folder.append(i)
                for address, sub_dirs, files in folder:
                    for file in files:
                        file_list.append(address + slash + file)
            return file_list
    else:
        def get_file_list(args):
            if 'win' in os.uname().sysname.lower():
                slash = '\\'
            else:
                slash = '/'
            file_list = []
            for arg in args:
                folders = []
                for i in os.walk(arg):
                    folders.append(i)
                folder = folders[0]
                adress, dirs, files = folder
                for dir in dirs:
                    file_list.append(adress + slash + dir + slash)
                for file in files:
                    file_list.append(adress + slash + file)
            return file_list
    return get_file_list


def file_hidden(files, options):
    if not options.hidden:
        for file_path in files[::]:
            file = file_path.split("/")[-1]
            #if ls is working in windows
            file = file.split("\\")[-1]
            if file.startswith("."):
                files.remove(file_path)
    return files


def modified_option(files, options):
    files_data = {}
    if options.modified:
        for path_to_file in files:
            if 'win' in os.uname().sysname.lower():
                files_data[path_to_file] = os.path.getctime(path_to_file)
            else:
                mtime = os.path.getmtime(path_to_file)
                files_data[path_to_file] = datetime.datetime.fromtimestamp(mtime).strftime("%d %b %Y %H:%M:%S")
    else:
        for path_to_file in files:
            files_data[path_to_file] = ''
    return files_data


def get_size(files_data):
    for file_path in files_data:
        if file_path.endswith("\\") or file_path.endswith("/"):
            continue
        # size in b
        size = os.path.getsize(file_path)
        formatted_size = locale.format("%d", size)
        if size > 9999999999:
            formatted_size = formatted_size[:-2] + "..."
        files_data[file_path] = "{0} {1:>10}".format(files_data[file_path], formatted_size)


def programs_out(files_data, options):
    directory_counter = 0
    files_counter = 0
    keys = get_sorted_dict_keys(files_data, options)
    for key in keys:
        if options.size and options.modified:
            print("{0:32} {1:20}".format(files_data[key], key))
        elif options.modified:
            print("{0:21} {1:20}".format(files_data[key], key))
        elif options.size:
            print("{0:10} {1:20}".format(files_data[key], key))
        else:
            print(key)
        if key.endswith("\\") or key.endswith("/"):
            directory_counter += 1
        else:
            files_counter += 1
    if files_counter == 1:
        file_word = "file"
    else:
        file_word = "files"
    if directory_counter == 1:
        directory_word = "directory"
    else:
        directory_word = "directories"
    print("{} {}, {} {}".format(files_counter, file_word, directory_counter, directory_word))


def get_size_to_path(path):
    if 'win' in os.uname().sysname.lower():
        slash = '\\'
    else:
        slash = '/'
    if path.endswith(slash) or path.endswith("."):
        folder = []
        file_list = []
        for i in os.walk(path):
            folder.append(i)
        for address, sub_dirs, files in folder:
            for file in files:
                file_list.append(address + slash + file)
        size = 0
        for file in file_list:
            size += os.path.getsize(file)
        return size
    return os.path.getsize(path)



def get_file_dir_name(file_path):
    if 'win' in os.uname().sysname.lower():
        slash = '\\'
    else:
        slash = '/'
    if file_path.endswith(slash):
        file_path = file_path[:-1]
    return file_path.split(slash)[-1]

def get_sorted_dict_keys(files_dict, options):
    if options.order == 'name' or options.order == 'n':
        sorted_keys = sorted(files_dict, key=get_file_dir_name)
        return sorted_keys
    elif options.order == 'size' or options.order == 's':
        sorted_keys = sorted(files_dict, key=get_size_to_path)
        return sorted_keys

usage = '''
%prog [options] [path1 [path2 [... pathN]]]

The paths are optional; if not given . is used.

'''
parser = OptionParser(usage=usage)
parser.add_option("-H", "--hidden", action='store_true', help='show hidden files default: off')
parser.add_option("-m", "--modified", action='store_true', help='show last modified date/time [default: off]')
parser.add_option("-o", "--order", default='name')
parser.add_option("-r", "--recursive", action='store_true', help='recurse into subdirectories [default: off]')
parser.add_option("-s", "--size", action='store_true', help='show sizes [default: off]')
options, args = parser.parse_args()

args = args_parse(args)
get_file_list = file_list_create(options)
files = get_file_list(args)
files = file_hidden(files, options)
files_dict = modified_option(files, options)
if options.size:
    get_size(files_dict)

programs_out(files_dict, options)
