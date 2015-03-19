# first time: sudo ln -s $(pwd)/bin/mne /usr/bin/
export STUDY_PATH=/media/harddrive/2013_meg_ambiguity/python/data/ambiguity

subjects=$(ls $STUDY_PATH/mri)
n=$(ls $STUDY_PATH/mri -1 | wc -l)
# parallel -j$n "sh scripts/run_anatomy_tutorial.sh STUDY_PATH {}" ::: $subjects
for subject in $subjects;do
  sh scripts/run_anatomy_tutorial.sh $STUDY_PATH $subject
done

# parallel -j$n "sh scripts/run_meg_tutorial.sh STUDY_PATH {}" ::: $subjects


for subject in $subjects; do
  # change default surface for viewer
  export subject_dir=$STUDY_PATH/subjects/$subject/bem
  if [ ! -e $subject_dir/$subject-head_original.fif ]; then
    mv $subject_dir/$subject-head.fif $subject_dir/$subject-head_original.fif
    ln -sf $subject_dir/$subject-head-medium.fif $subject_dir/$subject-head.fif
  fi;
done

for subject in $subjects; do
  # then, for each subject:
  export SUBJECTS_DIR=/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/subjects
  export SUBJECT=$subject
  echo $subject
  mne_analyze
  # file > load digitizer, load any raw sss file
  # load surfaces: subject, inflated
  # adjust > coordinate alignment: then click on nasion, LAP, RAP and adjust directly on image
  # > align using fiducials
  # > icp align (20)
  # > omit if outlier
  # > save default sss-trans.fif
done
