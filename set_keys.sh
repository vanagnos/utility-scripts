

cd ~/.ssh

jumpserverIp='10.10.10.10'
jumpserverUsername='root'
targetHostIp='10.10.10.11'
targetHostUsername='root'
read -s -p "enter intermediate jump server password for ssh: " jumpserverPassword
echo
read -s -p "enter target host password: " targetHostpassword




/usr/bin/expect <(cat << EOF

if [ $targetHostUsername == "root"]; then
    targetprompt=']#'
else
    targetprompt=']$'
fi

if [ $jumpserverUsername == "root"]; then
    jumpserverprompt=']#'
else
    jumpserverprompt=']$'
fi

spawn ssh-keygen -q -t rsa -N '' -f ~/.ssh/my_key <<< n

/usr/bin/expect <(cat << EOF
spawn ssh $jumpserverUsername@$jumpserverIp "echo \"`cat ~/.ssh/deployment_key.pub`\" >> ~/.ssh/authorized_keys"
expect "password:"
send "$jumpserverPassword\r"
expect $targetprompt
EOF
)

/usr/bin/expect <(cat << EOF
spawn ssh $jumpserverUsername@$jumpserverIp
expect $jumpserverprompt
send "ssh-keygen -q -t rsa -N '' -f ~/.ssh/my_key <<< n\r"
expect $jumpserverprompt
send "ssh-copy-id -f -i my_key $targetHostUsername@$targetHostIp\r"
expect "password:"
send "$targetHostpassword\r"
expect $jumpserverprompt
EOF
)
