#!/bin/bash
#Read grafana json and then extract metrics from each graph by calling them directly from graphite.

PRE="http://grafana.cloud.unimelb.edu.au/render/?target="
FORMAT=csv
OUTDIR=/var/backups/devops/energy_stats
OUTFILE=uom_energy_stats
CONTAINER=energy_stats
GRAFANA_JSON=json
ACCESS_URL="https://swift.rc.nectar.org.au:8888/v1/AUTH_42/${CONTAINER}"
mkdir -p ${OUTDIR}

rm $OUTDIR/*

while read -r line; do

    arg1=$(echo $line | cut -f2 -d '"')
    arg2=$(echo $line | cut -f4 -d '"')
    if [ "$arg1" == "title" ]; then
      count=0
      name=$(echo $arg2 | tr ' ' '_')
    fi
    if [ "$arg1" == "target" ]; then
     count=$(($count + 1))
     metric=$(echo $arg2 | sed 's/, /,/g')
     metric=$(echo $metric | sed 's/ /%20/g')

     from='10/09/2018'; until="today"
     file="${name}_${count}_$(date +%Y_%m_%d).csv"
     curl -s "${PRE}${metric}&from=${from}&until=${until}&format=${FORMAT}" > ${OUTDIR}/${file};

     from='-1d'; until="today"
     file="${name}_${count}_$(date +%Y_%m_%d)_1day.csv"
     curl -s "${PRE}${metric}&from=${from}&until=${until}&format=${FORMAT}" > ${OUTDIR}/${file};

   fi

done < <(cat $GRAFANA_JSON)
tarfile=${OUTFILE}_$(date +%Y_%m_%d).tar.gz
tar -czf ${tarfile} $OUTDIR

./swift-upload $CONTAINER ./${tarfile}
echo ${ACCESS_URL}/${tarfile}

