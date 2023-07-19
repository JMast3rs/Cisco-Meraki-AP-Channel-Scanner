import requests, time

# Set your API key and Meraki network ID
api_key = ''
network_id = ''

def get_devices_network(api_key, network_id):

    url = f"https://api.meraki.com/api/v1/networks/{network_id}/devices"

    response = requests.request("GET", url, headers={"X-Cisco-Meraki-API-Key": api_key, "Content-Type": "'application/json"})

    if response.status_code == 200:
        return response.json()

    elif response.status_code == 429:
        time.sleep(int(response.headers["Retry-After"]))
        return get_devices_network(api_key, network_id)

    else:
        print(f"ERROR: get_devices_network {response.status_code} {response.text}")
        return []


def get_ap_channel_setting(api_key, device_serial):

    url = f"https://api.meraki.com/api/v1/devices/{device_serial}/wireless/status"

    response = requests.request("GET", url, headers={"X-Cisco-Meraki-API-Key": api_key, "Content-Type": "'application/json"})

    if response.status_code == 200:
        return response.json()

    elif response.status_code == 429:
        time.sleep(int(response.headers["Retry-After"]))
        return get_devices_network(api_key, network_id)

    else:
        print(f"ERROR: get_ap_channel_setting {response.status_code} {response.text}")
        return {"basicServiceSets": []}


def get_ap_radio_setting(api_key, device_serial):

    url = f"https://api.meraki.com/api/v1/devices/{device_serial}/wireless/radio/settings"

    response = requests.request("GET", url, headers={"X-Cisco-Meraki-API-Key": api_key, "Content-Type": "'application/json"})

    if response.status_code == 200:
        return response.json()

    elif response.status_code == 429:
        time.sleep(int(response.headers["Retry-After"]))
        return get_devices_network(api_key, network_id)

    else:
        print(f"ERROR: get_ap_radio_setting {response.status_code} {response.text}")
        return {"fiveGhzSettings": {"channel": 0}}

def reboot_device(api_key, device_serial):

    url = f"https://api.meraki.com/api/v1/devices/{device_serial}/reboot"

    response = requests.request("POST", url, headers={"X-Cisco-Meraki-API-Key": api_key, "Content-Type": "'application/json"})

    if response.status_code == 202:
        return response.json()

    elif response.status_code == 429:
        time.sleep(int(response.headers["Retry-After"]))
        return reboot_device(api_key, network_id)

    else:
        print(f"ERROR: reboot_device {response.status_code} {response.text}")
        return {"success": False}

def check_channel(api_key, device_serial):

    channel_status_response = get_ap_channel_setting(api_key, device_serial)

    channel_setting_response = get_ap_radio_setting(api_key, device_serial)

    channel_status = 0
    for ssid in channel_status_response["basicServiceSets"]:
        
        if ssid["enabled"] == True and ssid["channel"] != None:
            channel_status = ssid["channel"]

    channel_setting = channel_setting_response["fiveGhzSettings"]["channel"]

    if channel_setting != channel_status:
        return {"match": False, "set": channel_setting, "status": channel_status}
    else:
        return {"match": True, "set": channel_setting, "status": channel_status}

def reboot_ap_list(api_key, device_list, all_devices_list):

    rebooted_successful = []
    rebooted_failed = []

    for device in all_devices_list:

        if device['name'] in device_list:
            reboot_response = reboot_device(api_key, device["serial"])

            if reboot_response["success"]:
                rebooted_successful.append(device['name'])
                print(f"{device['name']} rebooted successful!")
            else:
                rebooted_failed.append(device['name'])
                print(f"{device['name']} rebooted failed!")

            time.sleep(5)
    
    return rebooted_successful, rebooted_failed

def main():

    all_devices_list = get_devices_network(api_key, network_id)

    matched = []
    mismatched = []

    for device in all_devices_list:
        if device["model"] == "MR46": #Filter just on MR46
            channel_state = check_channel(api_key, device["serial"])

            if channel_state["match"]:
                matched.append(device['name'])
            else:
                mismatched.append(device['name'])
    
    print(f"Total Match: {len(matched)}, Total Mismatch: {len(mismatched)}")
    print(mismatched)

    if len(mismatched) > 0:
        reboot_yes = str(input("Would you like to reboot these APs? (yes or no): "))

        if reboot_yes.lower() == "yes":
            rebooted_successful, rebooted_failed = reboot_ap_list(api_key, mismatched, all_devices_list)
            print(f"Rebooted Successfully: {str(len(rebooted_successful)/len(mismatched)*100)}%")

main()
