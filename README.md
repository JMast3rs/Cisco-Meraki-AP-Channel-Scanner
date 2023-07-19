# Meraki AP Channel Scanner

This Python script uses the Meraki API to scan for Access Points that are not configured on their assigned channels. Once found, the script will reboot the Access Points to force them to re-scan the channels and join the correct one.

## Requirements

* Python 3.6+
* Meraki Read/Write API credentials
* Meraki Network ID to scan.

## Installation

1. Clone this repository to your local machine.
2. Run the script.

```
python3 main.py
Total Match: 65, Total Mismatch: 4
['AP-23', 'AP-13', 'AP-02', 'AP-01']
Would you like to reboot these APs? (yes or no): yes
Rebooted Successfully: 100.0%
```
