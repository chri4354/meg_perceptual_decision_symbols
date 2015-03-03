#!/usr/bin/env bash

STUDY_PATH=$1
export SUBJECT=$2

cd ${STUDY_PATH}/subjects && export SUBJECTS_DIR=${PWD}

# # Compute BEM model using Flash sequences
# assumes mef05.mgz and mef30.mgz are in the mri/flash folder
# you might want to use something like: find $SUBJECTS_DIR -name "meflash*" -exec rename 's/meflash_/mef' '{}';
# to make this work

# make sure the parameter maps are clean
if [ -d "$SUBJECTS_DIR/$SUBJECT/mri/flash/parameter_maps" ]; then
    rm -rf "$SUBJECTS_DIR/$SUBJECT/mri/flash/parameter_maps";
fi

echo $PWD

#
# mne_flash_bem --noconvert
# # # # #
# # # # # # The BEM surfaces should now be the bem/flash folder
# cd ${SUBJECTS_DIR}/${SUBJECT}/bem
# ln -sf flash/inner_skull.surf .
# ln -sf flash/outer_skin.surf .
# ln -sf flash/outer_skull.surf .
# #
# # # without FLASH images you should use

cd ${SUBJECTS_DIR}/${SUBJECT}/bem
mne_watershed_bem --overwrite

ln -sf watershed/${SUBJECT}_inner_skull_surface ${SUBJECT}-inner_skull.surf
ln -sf watershed/${SUBJECT}_outer_skin_surface ${SUBJECT}-outer_skin.surf
ln -sf watershed/${SUBJECT}_outer_skull_surface ${SUBJECT}-outer_skull.surf

# # MRI (this is not really needed for anything)

# # mne_setup_mri --overwrite
#
# # # Make high resolution head surface
mne make_scalp_surfaces --overwrite -f --subject ${SUBJECT} --subjects-dir $STUDY_PATH
# # if the previous command fails you can use the --force option.
#
# # # # Generate morph maps for morphing between sample and fsaverage
mne_make_morph_maps --from ${SUBJECT} --to fsaverage
mne_make_morph_maps --from ${SUBJECT} --to ${SUBJECT}
mne_make_morph_maps --from fsaverage --to fsaverage
