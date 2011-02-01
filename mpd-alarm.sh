#!/bin/bash
##########################
SLEEP_TIME=3             # Seconds to wait for next step (one step is +1% on the volume)
PLAYLIST="Favorites"     # The name of the playlist to load
MPC="/usr/bin/mpc -q"    # Path to mpc
AMIXER="/usr/bin/amixer" # Path to amixer
SLEEP="/usr/bin/sleep"   # Path to sleep
##########################

$MPC stop
$MPC clear 
$MPC load $PLAYLIST
$MPC random on

################ PulseAudio HACK START ###############
# Must run on the same machine as mpd in order to work
$AMIXER set Master mute
$MPC play
sleep 1 # Wait for mpd to connect to the pulse daemon
$MPC volume 0
$AMIXER set Master unmute
################ PulseAudio HACK END #################

for i in {0..100..1}
do
    $SLEEP $SLEEP_TIME
    $MPC volume $i
done
