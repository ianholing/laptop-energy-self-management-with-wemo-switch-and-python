# Laptop Energy Self-management With WeMo Switch

This is an implementation specially done for my environment, but it will work also if you define your primary DNS as your router in order to autodiscover your WeMo using the hostname. Check this using "ping wemo" command.

If you want to add it as a service remeber to change "DESTINATION_DIR" in wemo-power-manager.service and launch this:

* **sudo cp wemo-power-manager.service /etc/systemd/system/wemo-power-manager.service**
* **sudo systemctl enable wemo-power-manager.service**
* **sudo systemctl daemon-reload**
* **sudo systemctl restart wemo-power-manager.service**

You can also check logs like this:
* **systemctl status wemo-power-manager.service** OR **journalctl -u wemo-power-manager.service**
