#!/bin/bash

# Jens Dede, 2014
# jd@comnets.uni-bremen.de
#
# Execute a cooja (--> contiki) simulation file several times

if [ $# -ne 1 ]; then
    echo "Call with simulation as parameter: $0 test.csc"
    exit
else
    if [ -f $1 ]; then
        echo "Using saved simulation \"$1\"..."
    else
        echo "File \"$1\" does not exists!"
        exit
    fi
fi

simulation=$1
# Number of simulation runs
runs=10
# For filename
simDate=$(date +%y-%m-%d_%H-%M)

# Figure out the contiki base path. Assume, we are inside the contiki directory
unset contikiPath
contikiPath=$(pwd)
while [ $contikiPath != "/" ]; do
    if [ -d "$contikiPath/core/" ]; then
        break;
    fi
    contikiPath=$(dirname $contikiPath)
done

CONTIKI=$contikiPath
echo "Using the following contiki path: \"$CONTIKI\""

echo "Building cooja..."
curDir=$(pwd)
cd $CONTIKI/tools/cooja
ant jar
cd $curDir

echo "Done building cooja..."

for runNumber in $(seq 1 $runs); do
    # New random seed for each simulation run
    CURRENT_SEED=$RANDOM$RANDOM$RANDOM$RANDOM
    echo "Current seed: $CURRENT_SEED"
    echo "Run number $runNumber from $runs"
    echo "Staring simulation..."
    java -jar $CONTIKI/tools/cooja/dist/cooja.jar -nogui=$simulation -random-seed=$CURRENT_SEED
    if [ $? -ne 0 ]; then
        echo "Error in simulation! Breaking loop."
        break
    fi
    savepath="sim/simulation_$simDate/run_$runNumber/"
    mkdir -p $savepath
    # Store everything which could be interesting into output folder
    cp COOJA.* $simulation $savepath
done
