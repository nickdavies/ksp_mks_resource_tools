#!/usr/bin/env python

import sys
import os
import re

re_begin_d2 = re.compile(r'\s*(\S+)\s*{\s*$')
re_begin_d = re.compile(r'\s*{\s*$')
re_end_d = re.compile(r'\s*}\s*$')
re_keyval = re.compile(r'\s*(\S+)\s*=\s*(.*)\s*$')
re_float = re.compile(r'(-?\d*\.\d*)$')
re_spaces = re.compile(r'((-?\d*\.\d*|-?\d+) )+(-?\d*\.\d*|-?\d+)$')

def typify(s):
    s = s.strip()
    if s == '':
        return ''
    if re_spaces.match(s):
        return tuple([typify(x) for x in s.split(' ')])
    if ',' in s:
        split = tuple([typify(x) for x in s.split(',')])
        for i in split:
            if not isinstance(i, basestring):
                return split
        return s
    m_f = re_float.match(s)
    if m_f and len(s) > 1:
        return float(s)
    if s.isdigit() or (s[0] == '-' and s[1:].isdigit()):
        return int(s)
    return s

def get_inner(d, path):
    d2 = d
    for p in path:
        if p not in d2:
            d2[p] = {}
        d2 = d2[p]
        if isinstance(d2, list):
            d2 = d2[-1]
    return d2

def insert(d, path, key, val):
    inner = get_inner(d, path)
    tval = typify(val)
    if key in inner:
        if not isinstance(inner[key], list):
            inner[key] = [inner[key], tval]
        else:
            inner[key] += [tval]
    else:
        inner[key] = tval

def clean(line):
    line = line.strip()
    if line.startswith('\xef\xbb\xbf'):
        line = line[3:]
    if not line:
        return None
    if line.startswith('//'):
        return None
    return line

def new_dict(d, path, key):
    inner = get_inner(d, path)
    if key in inner:
        if not isinstance(inner[key], list):
            inner[key] = [inner[key], {}]
        else:
            inner[key] += [{}]
    path += [key]

def parse_cfg(text):
    d = {}
    path = []
    last_id = None
    for dirty_line in text.splitlines():
        line = clean(dirty_line)
        if line is None:
            continue
        m_begin_d = re_begin_d.match(line)
        m_begin_d2 = re_begin_d2.match(line)
        m_end_d = re_end_d.match(line)
        m_keyval = re_keyval.match(line)
        if m_keyval:
            key, val = m_keyval.groups()
            insert(d, path, key, val)
        elif m_begin_d2:
            key = m_begin_d2.group(1)
            new_dict(d, path, key)
            last_id = None
        elif m_begin_d:
            if not last_id:
                raise ValueError(text)
            new_dict(d, path, last_id)
            last_id = None
        elif m_end_d:
            path.pop()
        elif last_id:
            raise RuntimeError('Didnt know what to do with last_id %s' % last_id)
        else:
            last_id = line
    return d

def parse_cfg_dirs(target_paths, stop_on_error=True):
    if isinstance(target_paths, str):
        target_paths = [target_paths]

    paths = []
    dirs = []
    for path in target_paths:
        if os.path.isdir(path):
            dirs += [path]
        else:
            paths += [path]

    for dir in dirs:
        for root, _, files in os.walk(dir):
            for path in files:
                if path.lower().endswith('.cfg'):
                    paths += [os.path.join(root, path)]
    d = {}
    for path in paths:
        with open(path) as f:
            text = f.read()
        try:
            d[path] = parse_cfg(text)
        except Exception as err:
            print >>sys.stderr, path
            print >>sys.stderr, str(err)
            d[path] = 'Exception: %s' % str(err)
            if stop_on_error:
                raise
            else:
                continue

    return d


if __name__ == '__main__':
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument('--out', '-o', default=None, help='Path to dump json')
    parser.add_argument('paths', nargs='+', help='Configs or dirs to parse.')
    args = parser.parse_args()

    d = parse_cfg_paths(args.paths)

    if args.out:
        with open(args.out, 'w') as f:
            json.dump(d, f, indent=4)
    else:
        print(json.dumps(d, indent=4))
