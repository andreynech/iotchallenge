#!/bin/bash

rm -rf unpacked/*
rm -rf sorted/*

./unpack.py

mkdir -p sorted/unpacked

for f in unpacked/*
do
	sort $f > sorted/$f
done

mv sorted/unpacked/* sorted
rm -rf sorted/unpacked

cd sorted

touch currents.dat
touch alerts.dat

for f in *_alert
do
    echo " " >> ${f:0:36}
    cat $f >> ${f:0:36}

    cat $f >> alerts.dat
    echo " " >> alerts.dat

    cat ${f:0:36} >> currents.dat
    echo " " >> currents.dat
    
    rm $f
done

cd ..
