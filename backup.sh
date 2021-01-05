#!/bin/bash
#================================================================
# HEADER
#================================================================
#% SYNOPSIS
#+    ./${SCRIPT_NAME} -vnflcm [IP] -tar [BACKUP FILE NAME] DEST
#%
#% DESCRIPTION
#%    Creates a tar from the contents of:
#%        "/home/cloud-user"
#%        "/ericsson/3pp/jboss/standalone/log/server.log"
#%        "/var/opt/ericsson/workflows/work"
#%    on the specified VNF-LCM and SCP it locally to the specified destination.
#%
#% MANDATORY ARGUMENTS
#%    -vnflcm                   VNF-LCM IP
#%    -tar                      name for tar to be created
#%    DEST                      Destination
#%
#% OPTIONS
#%     -v                       Verbose mode
#%    --help                    Print this help
#%
#% EXAMPLE
#%    ./${SCRIPT_NAME} -vnflcm 214.2.14.20 -tar mybackup.tar.gz .
#%
#================================================================
# END_OF_HEADER
#================================================================

SCRIPT_HEADSIZE=$(head -200 ${0} |grep -n "^# END_OF_HEADER" | cut -f1 -d:)
SCRIPT_NAME="$(basename ${0})"
usagefull() { head -${SCRIPT_HEADSIZE:-99} ${0} | grep -e "^#[%+-]" | sed -e "s/^#[%+-]//g" -e "s/\${SCRIPT_NAME}/${SCRIPT_NAME}/g" ; }

eo_ip=150.132.156.67
eo_user=root
eo_password=ecm123
vnflcm_user=cloud-user
vnflcm_password=Er1css0n!
timeout=300
verbose=0






if [ vnflcm_user = 'root' ]; then
    prompt=']#'
else
    prompt=']$'
fi

while [ "$#" -gt 0 ]; do
    if [ -d "$1" ]; then #|| [ -z "$destination" ]; then
        destination="$1"
    shift
    fi

    case "$1" in
        --help) usagefull; exit 0;;
        -v) verbose=1; shift;;
        -vnflcm) vnflcm_ip="$2"; shift;;
        -tar) backupfile_name="$2"; shift;;
        *)
    echo '"$1" not recognized'
        shift
        ;;
    esac
    shift
done


if [ -z $vnflcm_ip ]; then
    echo "$SCRIPT_NAME: missing '-vnflcm' argument"
    echo "Try './$SCRIPT_NAME --help' for more information."
    exit 1
fi

if [ -z $backupfile_name ]; then
    echo "$SCRIPT_NAME: missing '-tar' argument"
    echo "Try './$SCRIPT_NAME --help' for more information."
    exit 1
fi

if [ -z $destination ]; then
    echo "$SCRIPT_NAME: missing destination"
    echo "Try './$SCRIPT_NAME --help' for more information."
    exit 1
fi

if [[ $backupfile_name != *".tar.gz" ]]; then
    backupfile_name="${backupfile_name}.tar.gz"
fi


zip_command="tar -czf $backupfile_name /home/cloud-user/ /ericsson/3pp/jboss/standalone/log/server.log /var/opt/ericsson/workflows/work/"


echo 'Creating tar on VNF-LCM...'
# create tar on VNF-LCM host
/usr/bin/expect <(cat << EOF
log_user $verbose
set timeout $timeout
spawn ssh  -J $eo_user@$eo_ip $vnflcm_user@$vnflcm_ip $zip_command
expect "password:"
send "$eo_password\r"
expect "password:"
send "$vnflcm_password\r"
expect "$prompt"

EOF
)

echo 'SCP tar locally...'
#scp tar from VNF-LCM to local destination
/usr/bin/expect <(cat << EOF
log_user $verbose
set timeout $timeout
spawn scp  -o "StrictHostKeyChecking no" -o "ProxyCommand ssh $eo_user@$eo_ip -W %h:%p" $vnflcm_user@$vnflcm_ip:$backupfile_name $destination
expect "password:"
send "$eo_password\r"
expect "password:"
send "$vnflcm_password\r"
expect "$prompt"
EOF
)

#cleanup created tar from vnflcm
/usr/bin/expect <(cat << EOF
log_user $verbose
set timeout $timeout
spawn ssh -o "StrictHostKeyChecking no" -J $eo_user@$eo_ip $vnflcm_user@$vnflcm_ip rm -f $backupfile_name
expect "password:"
send "$eo_password\r"
expect "password:"
send "$vnflcm_password\r"
expect "$prompt"
EOF
)
