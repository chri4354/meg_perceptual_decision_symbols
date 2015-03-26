# first time: may need to do sudo ln -s $(pwd)/bin/mne /usr/bin/
export STUDY_PATH=/media/harddrive/2013_meg_ambiguity/python/data/ambiguity

subjects=$(ls $STUDY_PATH/mri)
n=$(ls $STUDY_PATH/mri -1 | wc -l)
# parallel -j$n "sh scripts/run_anatomy_tutorial.sh STUDY_PATH {}" ::: $subjects # did not work?
for subject in $subjects;do
  sh scripts/mne_anatomy_tutorial.sh $STUDY_PATH $subject
done

# parallel -j$n "sh scripts/run_meg_tutorial.sh STUDY_PATH {}" ::: $subjects  # did not work?
for subject in $subjects;do
  sh scripts/mne_meg_tutorial.sh $STUDY_PATH $subject
done


for subject in $subjects; do
  # change default surface for viewer
  export subject_dir=$STUDY_PATH/subjects/$subject/bem
  if [ -e $subject_dir/$subject-head_original.fif ]; then
    rm $subject_dir/$subject-head_original.fif
  fi;
  if [ ! -e $subject_dir/$subject-head_original.fif ]; then
    mv $subject_dir/$subject-head.fif $subject_dir/$subject-head_original.fif
    ln -sf $subject_dir/$subject-head-medium.fif $subject_dir/$subject-head.fif
  fi;
done

export SUBJECTS_DIR=/media/harddrive/2013_meg_ambiguity/python/data/ambiguity/subjects
for subject in $subjects; do
  # then, for each subject:
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
# check
export STUDY_PATH=/media/harddrive/2013_meg_ambiguity/python/data/ambiguity
subjects=$(ls $STUDY_PATH/mri)
for subject in $subjects; do
  echo $subject
  ls $STUDY_PATH/MEG/$subject/*trans*
done

# SUBJECT 07: manual fix: head surface is not closed X used original sb-head.fif instead of medium resolution
# SUBJECT 13: manual fix: head surface is not closed X used original sb-head.fif instead of medium resolution
# SUBJECT 05: freesurfer crashed
# SUBJECT 10: freesurfer crashed
# SUBJECT 01: MISSING
# SUBJECT 12: MISSING
# SUBJECT 15: MISSING
# SUBJECT 16: MISSING
# SUBJECT 17: MISSING
