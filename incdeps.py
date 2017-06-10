#!/usr/bin/env python
# encoding: utf-8
# Copyright (C) 2016 John Törnblom
"""
A simple command line tool for dumping a Graphviz description (dot) that
describes include dependencies. Heavily inspired by cindex-includes.py
disitributed with the clang source code.
"""
import ctypes.util
import logging
import sys
import os

from clang.cindex import Index, Config


for libname in ['clang', 'clang-4.0', 'clang-3.9', 'clang-3.8', 'clang-3.7']:
    filename = ctypes.util.find_library(libname)
    if filename:
        Config.set_library_file(filename)
        break


logger = logging.getLogger('incdeps')


def emit_node(out, uid, label):
    out.write('  "%s" [label="%s"];\n' % (uid, label))


def emit_cluster(out, children, cluster_path='', parent_path=''):
    prefix = '  ' * (cluster_path.count(os.path.sep) - 1)
    
    nodes = list()
    clusters = dict()
    for path, item in children.items():
        if isinstance(item, str):
            nodes.append(path)
        else:
            clusters[path] = item

    if nodes or len(clusters) > 1:
        label = cluster_path.replace(parent_path, '', 1)
        parent_path = cluster_path + os.path.sep
        out.write(prefix + 'subgraph "cluster %s" {\n' % cluster_path)
        out.write(prefix + '  label="%s";\n' % label)
        out.write(prefix + '  style=filled;\n')
        out.write(prefix + '  color=black;\n')
        out.write(prefix + '  fillcolor="#CCCCCC30";\n')

    for node in nodes:
        out.write(prefix)
        emit_node(out, node, os.path.basename(node))
        
    for path, item in clusters.items():
        emit_cluster(out, item, path, parent_path)

    if nodes or len(clusters) > 1:
        out.write(prefix)
        out.write("}\n")
    

def emit_edge(out, source_uid, target_uid):
    out.write('  "%s" -> "%s";\n' % (source_uid, target_uid))


def emit_graph(out, tu, once=False):
    out.write('digraph {\n')
    out.write('  rankdir=LR;\n')
    out.write('  node [shape=box, style=rounded];\n')
    
    cluster_root = dict()
    nodes = set()
    
    def add_to_cluster(filename):
        dirname = os.path.dirname(filename)
        cluster = cluster_root
        path = ''
        for name in dirname.split(os.path.sep):
            if path != os.path.sep:
                path += os.path.sep

            path += name
            if path not in cluster:
                cluster[path] = dict()

            cluster = cluster[path]

        cluster[filename] = filename

    add_to_cluster(os.path.abspath(tu.spelling))
    for i in tu.get_includes():
        source = os.path.abspath(i.source.name)
        target = os.path.abspath(i.include.name)
        if target not in nodes:
            add_to_cluster(source)
            add_to_cluster(target)
            emit_edge(out, source, target)

        if once:
            nodes.add(target)
        
    emit_cluster(out, cluster_root)

    out.write("}\n")


def main():
    if len(sys.argv) < 2:
        sys.stderr.write('missing arguments (see -h for help)\n')
        sys.exit(1)
        
    if '-h' in sys.argv:
        sys.stderr.write('%s\n\n' % __doc__.strip())
        sys.stderr.write('usage example: %s /usr/include/stdio.h | dot -Txlib\n' %  sys.argv[0])
        sys.exit(1)
        
    logging.basicConfig(level=logging.INFO)
    index = Index.create()
    tu = index.parse(None, sys.argv[1:])
    rc = 0
    
    if tu:
        emit_graph(sys.stdout, tu)
        log_map = {
            0: logger.debug,
            1: logger.info,
            2: logger.warning,
            3: logger.error,
            4: logger.fatal
        }
        rc = 0
        for d in tu.diagnostics:
            rc = max(d.severity, rc)
            log = log_map[d.severity]
            log('in file %s, line %d:%s' % (d.location.file.name,
                                            d.location.line,
                                            d.spelling))
    else:
        rc = 1
        
    sys.exit(rc)


if __name__ == '__main__':
    main()
