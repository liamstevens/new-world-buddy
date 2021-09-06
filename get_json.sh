#!/bin/zsh
#$URLs=find nwdb.info
for url in $(find nwdb.info/db/recipe ! -name '*\?*' ! -name '*\.*');
do
    
    echo $url
    wget "$url.json" > "$url.json"
done
