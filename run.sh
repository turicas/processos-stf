#!/bin/bash

set -e

LIST_OF_PROCESSES="data/output/lista-processos.csv"
#MOVEMENTS="data/output/andamentos.csv"
PROCESSES="data/output/processos.csv"
STF_DB="data/output/processos-stf.sqlite"

rm -rf data/output data/scraper.log
mkdir -p data/output

echo '***** Downloading list of processes...'
time scrapy crawl list-processes -o "$LIST_OF_PROCESSES"

#echo '***** Downloading movements...'
#time scrapy crawl process-movements -o "$MOVEMENTS"

echo '***** Downloading metadata...'
time scrapy crawl process-meta -o "$PROCESSES"

echo '***** Converting to SQLite...'
time rows csv2sqlite "$LIST_OF_PROCESSES" "$PROCESSES" "$STF_DB"

xz -z $LIST_OF_PROCESSES
xz -z $PROCESSES
