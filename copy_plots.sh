#!/bin/bash

SOURCE_PATH="/home/tobiaszfic/school/m_sc/mgr/thesis-analysis/analysis/plots"
DESTINATION_PATH="/home/tobiaszfic/school/m_sc/mgr/thesis/img/plots"
echo "Copying plots from $SOURCE_PATH to $DESTINATION_PATH"
# copy the contents of the source directory to the destination directory

cp -r $SOURCE_PATH/* $DESTINATION_PATH

echo "Copied plots from $SOURCE_PATH to $DESTINATION_PATH"