#!/bin/bash 

# All timeouts in minutes
TIMEOUT_CHANNEL_REFRESH=60
TIMEOUT_CHANNEL_SYNC=120

exec >/var/log/populate_channels.log 2>&1 </dev/null

echo "`date` populate channels started"

error_handler()
{
  echo "`date` populate channels aborted"
  exit 1
}

trap error_handler ERR

if [ "$1" = "-h" -o "$1" = "--help" -o -z "$1" ]; then
  echo "Usage: $0 channel[,...]"
fi

IFS=','
for channel in $@ ; do
  case $channel in
  sles12)
    CHANNEL_LIST="$CHANNEL_LIST sles12-pool-x86_64 sles12-updates-x86_64 sle-manager-tools12-pool-x86_64 sle-manager-tools12-updates-x86_64"
    ;;
  sles12sp1)
    CHANNEL_LIST="$CHANNEL_LIST sles12-sp1-pool-x86_64 sles12-sp1-updates-x86_64 sle-manager-tools12-pool-x86_64-sp1 sle-manager-tools12-updates-x86_64-sp1"
  sles12sp2)
    CHANNEL_LIST="$CHANNEL_LIST sles12-sp2-pool-x86_64 sles12-sp2-updates-x86_64 sle-manager-tools12-pool-x86_64-sp2 sle-manager-tools12-updates-x86_64-sp2"
    ;;
  sles11sp4)
    CHANNEL_LIST="$CHANNEL_LIST sles11-sp4-pool-x86_64 sles11-sp4-updates-x86_64 sles11-sp4-suse-manager-tools-x86_64 sle-manager-tools11-updates-x86_64-sp4"
    ;;

  *)
    CHANNEL_LIST="$CHANNEL_LIST $channel"
    ;;
  esac
done
unset IFS
echo "Selected channels: $CHANNEL_LIST"
echo -n "Waiting for channels to appear "
tick=0
while [ -z "$(mgr-sync list channels -c | grep -v 'No channels found')" ] ; do
  if [ $tick = 60 ]; then
    echo " timeout waiting for channel refresh"
    exit 1
  fi
  echo -n .
  tick=$((tick+1))
  sleep 60
done
echo

for channel in $CHANNEL_LIST ; do
  mgr-sync add channel $channel
  if [ "$channel" != "${channel/pool}" ]; then
    # wait a bit after adding pool channels for update channels to appear
    sleep 10
  fi
done

echo -n "Waiting for all channels to be synced "
sleep 60

tick=0
DONE=0
while [ "$DONE" = "0" ]; do
  if [ $tick = $TIMEOUT_CHANNEL_SYNC ] ; then
    echo "Timeout waiting for channel sync"
    false
  fi
  for i in `ls /var/log/rhn/reposync` ; do
    if ! tail -n 1 "/var/log/rhn/reposync/$i" | grep -q -E '^Total time' ; then
      # this channel is still syncing
      echo -n '.'
      sleep 60
      tick=$((tick+1))
      continue 2 
    fi
  done
  # if we reach this point, all log files had the final total time message
  DONE=1
done

while [ $tick -lt $TIMEOUT_CHANNEL_SYNC -a "$DONE" = "0" ]; do
  for i in /var/log/rhn/reposync/* ; do
    if ! tail -n 1 $i | grep -q -E '^Total time' ; then
      echo -n '.'
      sleep 60
      tick=$((tick+1))
      continue
    fi
    DONE=1
  done
done
echo    


echo "Creating bootstrap repositories"
PRODS="$(mgr-create-bootstrap-repo -l)"
for prod in $PRODS ; do
  mgr-create-bootstrap-repo -c $prod
done

echo "`date` populate channels finished"
exit 0
