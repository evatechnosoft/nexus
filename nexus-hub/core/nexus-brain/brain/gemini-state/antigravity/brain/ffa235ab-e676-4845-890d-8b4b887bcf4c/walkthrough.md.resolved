# Xiaomi Integration Walkthrough

The Xiaomi Miot Auto integration has been successfully installed and Home Assistant has been restarted. You can now complete the setup through the web interface.

## Actions Taken

- [x] **HACS Verification**: Confirmed HACS is installed in `/DATA/AppData/homeassistant/config/custom_components`.
- [x] **Xiaomi Miot Auto Installation**: Installed the `xiaomi_miot` custom component via the official install script.
- [x] **Home Assistant Restart**: Restarted the `homeassistant-homeassistant-1-homeassistant-homeassistant-1-1` container to load the new component.

## Next Steps for You (Manual)

To complete the account-based connection, please follow these steps in your Home Assistant UI:

1. Open **Home Assistant** (e.g., `ha.evaitec.com`).
2. Go to **Settings** -> **Devices & Services**.
3. Click **Add Integration** (bottom right).
4. Search for **Xiaomi Miot Auto** (NOT Xiaomi Miio).
5. Select **Log in with Mi Account**.
6. Enter your Xiaomi credentials. For the server, you should select **Singapore (sg)** as indicated in your discovery log.
7. Your devices (**Bella** and **Mi Temp**) will be discovered and added automatically.

> [!TIP]
> Since we already have the **BLE KEY** for the "Mi Temp" sensor (`1f8912aeb5bc8f53bf27576033fb8949`), the integration will be able to decrypt the data automatically.

## Device Reference (Backup)

For your records, here are the details we used during the process:
- **Bella (Vacuum)**: TOKEN `457a59536976797343786e4c5a373779` | IP `192.168.1.181`
- **Mi Temp (Sensor)**: BLE KEY `1f8912aeb5bc8f53bf27576033fb8949` | MAC `A4:C1:38:17:90:BD`
