#!/bin/zsh

for file in $(find . -name '*\.json');
do
    
    target=$(echo $file | cut -f 2 -d '/')
    #| cut -f 1 -d '.' )
    echo $target
    tpath=$(find . -name $target)
    #echo "$tpath.json"
    cp $file "$tpath.json"

#    mv $file $(find . -name $(echo $file | cut -f -1 -d)) 

done
