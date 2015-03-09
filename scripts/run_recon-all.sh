#!/usr/bin/env bash

subjects=$(ls $MRI_DIR)

# make sure all is clean
for subject in $subjects; do
    error_log=$SUBJECTS_DIR/$subject/scripts/IsRunning.lh+rh;
    if [ -e $error_log ]; then
        echo  removing $error_log;
        rm $error_log;
    fi;
done

# XXX put the -j{digit} flag to set n jobs
parallel -j19 'export SUBJECT={}; echo processing: $SUBJECT; recon-all -all -s $SUBJECT -i $MRI_DIR/$SUBJECT/anatomy/highres001.nii.gz > $MRI_DIR/$SUBJECT/my-recon-all.txt' -- $subjects
