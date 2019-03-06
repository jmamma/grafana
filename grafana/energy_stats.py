#!/usr/bin/python

import json
from datetime import datetime
import subprocess

PRE = "http://grafana.cloud.unimelb.edu.au/render/?target="
FORMAT = "csv"
OUTDIR = "/var/backups/devops/energy_stats"
TARDIR = "/var/backups/devops"
OUTFILE = "uom_energy_stats"
CONTAINER = "energy_stats"
GRAFANA_JSON = "json"
ACCESS_URL = "https://swift.rc.nectar.org.au:8888/v1/AUTH_42/${CONTAINER}"

def cmdline(command):
    print command
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    out = proc.communicate()
    proc.wait()
    return (out, proc.returncode)

def main():
    f = open("json","r")

    x = json.load(f)
    from pprint import pprint

    for panel in x['panels']:
        if 'datasource' in panel:
            if panel['datasource'] == 'Graphite':
                name = panel['title'].lstrip(' ').replace(' ','_').replace('/','_')
                count = 0
                for t in panel['targets']:
                     count += 1
                     metric = t['target'].replace(', ',',').replace(" ","%20")
                     
                     frm = "10/09/2018"
                     until = "today"
                     file = name + "_" + str(count) + "_" + datetime.now().strftime("%Y_%m_%d") + ".csv"
                     command = "curl -s " + '"' + PRE + metric + "&from=" + frm + "&until=" + until + "&format=" + FORMAT + '"' + " > '" + OUTDIR + "/" + file + "'";
                     cmdline(command)

                     frm = "-1d"
                     until = "today"
                     file = name + "_" + str(count) + "_" + datetime.now().strftime("%Y_%m_%d") + "_1day.csv"
                     command = "curl -s " + '"' + PRE + metric + "&from=" + frm + "&until=" + until + "&format=" + FORMAT + '"' + " > '" + OUTDIR + "/" + file + "'";
                     cmdline(command)
    
    tarfile_short = OUTFILE + "_" + datetime.now().strftime("%Y_%m_%d") + ".tar.gz"
    tarfile = TARDIR + "/" + tarfile_short
    
    command = "tar -czf " + tarfile + " " + OUTDIR
    cmdline(command)

    command = "swift --os-tenant-name='nectar_tenant' upload " + CONTAINER + "--object-name " + tarfile_short + " " + tarfile
    cmdline(command)

if __name__ == '__main__':
    main()


