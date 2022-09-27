/usr/local/bin/kubectl delete node "nxt2032"
/usr/local/bin/kubectl cordon node "nxt2031"
/usr/local/bin/kubectl drain --force --ignore-daemonsets --delete-local-data --grace-period=10 "nxt2031"
