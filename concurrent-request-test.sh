#!/bin/bash
# script sends 15 parallel DNS queries to the DNS server at 172.168.1.2 
# for the domain google.com, using port 53
for i in {1..15}; do
  dig @172.168.1.2 -p 53 google.com +short &
done
wait
echo "All queries completed."
