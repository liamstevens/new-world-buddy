#!/bin/zsh
#$URLs=find nwdb.info
for url in $(find nwdb.info ! -name '*\?*' ! -name '*\.*');
do
    
    echo $url
    wget "$url.json"
done
