#!/bin/zsh

for file in $(find . -maxdepth 1 -name  '*\.json');
do
    
    target=$(echo $file | cut -f 2 -d '/')
    #| cut -f 1 -d '.' )
    #echo $target
    tpath=$(find . -name $target)
    #echo "$tpath.json"
    #touch "$tpath.json"
    cp $file "./nwdb.info/db/recipe/json"

#    mv $file $(find . -name $(echo $file | cut -f -1 -d)) 

done
