#!/bin/bash

exit_cleanup()
{
  test -n "$SRVS" &&  rm -f "$SRVS" 
}


print_rgnsrv_block()
{
  awk -v pattern="type=\"regionserver-$1\"" '
$0 ~ pattern \
{ 
  if (print_comma) print ","
  split($4, rgn, "=")
  split($2, addr, "=")
  printf "      %s : { \"Address\" : %s }", rgn[2], addr[2]
  print_comma=1
}' $SRVS
  echo
}

print_smt_block()
{
  awk -v pattern="type=\"smt-$1\"" '
$0 ~ pattern \
{ 
  split($4, rgn, "=")
  if (last_region != rgn[2]) {
    if (close_region) {
      printf "\n      },\n"
    }
    else {
      close_region=1
    }
    suffix=1
    printf "      %s : {\n", rgn[2]
  }
  else {
    suffix++
    if (print_comma) print ","
  }
  split($2, addr, "=")
  printf "          \"Address%s\" : %s", suffix, addr[2]
  print_comma=1
  last_region = rgn[2]
}' $SRVS
  printf "\n      }\n"
}

test -f "$1" || { echo "Usage: $0 template_file" >&2 ; exit 1 ; }

SRVS=$(mktemp /tmp/pintdata.XXXXXX)
trap exit_cleanup EXIT

pint amazon servers |grep name |sort -k4 >> $SRVS

IFS=
while read -r line ; do
  if [[ "$line" =~ ' '*\"Mappings\"' '*: ]]; then
    echo "$line"
    echo '    "SMTSLES" : {'
    print_smt_block sles
    echo "    },"
    echo '    "SMTSAP" : {'
    print_smt_block sap
    echo "    },"
    echo '    "RgnsrvSLES" : {'
    print_rgnsrv_block sles
    echo "    },"
    echo '    "RgnsrvSAP" : {'
    print_rgnsrv_block sap
    echo "    }"
    # seek to end of Mappings block
    LEVEL=1
    while [[ $LEVEL -gt 0 ]]; do
      read -r line
      # this is not very robust as it also counts brackets in strings
      OPENING_BRACKETS="${line//[^\{]/}"
      CLOSING_BRACKETS="${line//[^\}]/}"
      OPENING_BRACKETS_COUNT=${#OPENING_BRACKETS}
      CLOSING_BRACKETS_COUNT=${#CLOSING_BRACKETS}
      LEVEL=$((LEVEL+OPENING_BRACKETS_COUNT-CLOSING_BRACKETS_COUNT))
    done
  fi
  echo "$line"
done < $1
