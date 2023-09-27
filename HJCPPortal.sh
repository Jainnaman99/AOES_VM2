echo -n username:

read username

echo -n password:

read -s password

curl -Lk "https://10.44.254.206:6082/php/uid.php?vsys=1&url=https://hjcpportal.persistent.com:6082/php/uid.php?vsys=1&rule=0&url"%"2f" -H "Host: 10.44.254.206:6082"  -H "Referer: https://10.44.254.206:6082/php/uid.php?vsys=1&url=https://hjcpportal.persistent.com:6082/php/uid.php?vsys=1&rule=0&url"%"2f" -H "Connection: keep-alive" --data "inputStr=&escapeUser=$username&user=$username&passwd=$password&ok=Login"
