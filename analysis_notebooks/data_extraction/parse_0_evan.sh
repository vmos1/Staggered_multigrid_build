#!/bin/bash

if [ "$#" -ne 2 ]
then
  echo "Expected two inputs, file and cg/mg"
  exit
fi

case $2 in
  "cg") MG="0" ;;
  "mg") MG="1" ;;
  *) echo "Invalid solve type, exit..."; exit ;;
esac

IOFILE=$1

HEADER=""
VALUES=""

# startup time
HEADER=$HEADER" startup"
VALUES="${VALUES} "`grep "Aggregate time to setup" $IOFILE | cut -d ' ' -f5`

# loading
HEADER=$HEADER" loading"
VALUES="${VALUES} "`grep "Aggregate time to readin" $IOFILE | cut -d ' ' -f5`

if [ "$MG" -eq 1 ]
then

  # mg setup
  HEADER=$HEADER" mg-setup"
  MGSETUP=`grep "MG inverter setup complete" $IOFILE | cut -d' ' -f8`
  VALUES="${VALUES} ${MGSETUP}"

  ## read all lines related to solves ##
  readarray -t a < <(grep "fn_QUDA_MG D" $IOFILE)

  ## Mass 1: lines 0, 3, 6, 9, 12, 15... but setup is munged into 0,
  ##         so we just estimate that
  mass="0.0"
  for l in 3 6 9 12 15 18
  do
    val=$(echo "${a[$l]}" | cut -d' ' -f4)
    mass=$(echo "${mass} ${val}" | awk ' { printf "%.16e\n", $1 + $2; } ')
  done
  mass1=$(echo $mass | awk ' { printf "%.16e\n", ($1*6./5.)/2.; } ')
  HEADER_MASS=$HEADER_MASS" mass-01"
  VALUES_MASS=$VALUES_MASS" ${mass1}"

  ## Mass 2: lines 1, 4, 7, ...
  mass="0.0"
  for l in 1 4 7 10 13 16
  do
    val=$(echo "${a[$l]}" | cut -d' ' -f4)
    mass=$(echo "${mass} ${val}" | awk ' { printf "%.16e\n", $1 + $2; } ')
  done
  mass2=$(echo $mass | awk ' { printf "%.16e\n", $1/2.; } ')
  HEADER_MASS=$HEADER_MASS" mass-02"
  VALUES_MASS=$VALUES_MASS" ${mass2}"

  ## Mass 3: lines 2 5 8 11 14 17
  mass="0.0"
  for l in 2 5 8 11 14 17
  do
    val=$(echo "${a[$l]}" | cut -d' ' -f4)
    mass=$(echo "${mass} ${val}" | awk ' { printf "%.16e\n", $1 + $2; } ')
  done
  mass3=$(echo $mass | awk ' { printf "%.16e\n", $1/2.; } ')
  HEADER_MASS=$HEADER_MASS" mass-03"
  VALUES_MASS=$VALUES_MASS" ${mass3}"
else
  # mg setup is 0
  HEADER=$HEADER" mg-setup"
  VALUES="${VALUES} 0"
fi

## Multishift: read in all lines
readarray -t a < <(grep "multicg_offset_QUDA D" $IOFILE)
mass="0.0"
for line in "${a[@]}"
do
  val=$(echo $line | cut -d' ' -f4)
  mass=$(echo "${mass} ${val}" | awk ' { printf "%.16e\n", $1 + $2; } ')
done
mass_multi=$(echo $mass | awk ' { printf "%.16e\n", $1/2.; } ')

if [ "$MG" -eq 1 ]
then 
  HEADER_MASS=$HEADER_MASS" mass-04-10"
else
  HEADER_MASS=$HEADER_MASS" mass-01-10"
fi
VALUES_MASS=$VALUES_MASS" ${mass_multi}"

## Heavy quark
readarray -t a < <(grep "fn_QUDA D" $IOFILE)
mass="0.0"
for line in "${a[@]}"
do
  val=$(echo $line | cut -d' ' -f4)
  mass=$(echo "${mass} ${val}" | awk ' { printf "%.16e\n", $1 + $2; } ')
done
mass_heavy=$(echo $mass | awk ' { printf "%.16e\n", $1/2.; } ')
HEADER_MASS=$HEADER_MASS" mass-11-20"
VALUES_MASS=$VALUES_MASS" ${mass_heavy}"

echo $HEADER_MASS
echo $VALUES_MASS

PROPTIME=`echo $VALUES_MASS | awk ' { t = 0; for (i = 1; i <= NF; i++) { t += $i; } printf "%.16e\n", 2 * t; } '`
HEADER=$HEADER" solve-time"
VALUES="${VALUES} ${PROPTIME}"

# make/save source
HEADER=$HEADER" make/save-src"
VALUES="${VALUES} "`grep "Aggregate time to create sources" $IOFILE | cut -d' ' -f6`

# contractions
HEADER=$HEADER" contractions"
VALUES="${VALUES} "`grep "Aggregate time to tie meson correlators" $IOFILE | cut -d' ' -f7`

# sum up our reported time
CALCTIME=`echo $VALUES | awk ' { t = 0; for (i = 1; i <= NF; i++) { t += $i; } printf "%.16e\n", t; } '`
HEADER=$HEADER" summed-time"
VALUES="${VALUES} ${CALCTIME}"

# QUDA total time
HEADER=$HEADER" quda-total-time"
VALUES="${VALUES} "`grep "QUDA Total time" $IOFILE | tr -s ' ' | cut -d' ' -f6`

# MILC total time
MILCTOTAL=`grep "Time =" $IOFILE | grep "seconds" | cut -d ' ' -f3`
HEADER=$HEADER" milc-total-time"
VALUES="${VALUES} ${MILCTOTAL}"

# error
ERRORTIME=`echo "$MILCTOTAL $CALCTIME" | awk ' { printf "%.15e\n", $1 - $2; } '`
HEADER=$HEADER" error"
VALUES="${VALUES} ${ERRORTIME}"

echo $HEADER
echo $VALUES

#startup: grep "Aggregate time to setup" output-mg-nc64-nc96-drop.kpp | cut -d' ' -f5
#make/save source: grep "Aggregate time to create sources"
#loading: grep "Aggregate time to readin"
#contractions: grep "Aggregate time to tie meson correlators"

#isolated setup time: grep "MG inverter setup complete"

#total time by MILC: grep "Time =" | grep "seconds"


