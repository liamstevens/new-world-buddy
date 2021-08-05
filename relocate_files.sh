#!/bin/zsh

for file in $(find . -name '*\.json');
do
    echo $file
    target=$(echo $file | cut -f 2 -d '/' | cut -f 1 -d '.' )
    echo $target
    tpath=$(find . -name $target)
    mv $file "$tpath.json"

#    mv $file $(find . -name $(echo $file | cut -f -1 -d)) 

done
