#!/bin/bash

# --- Configuration: CHANGE THESE ---
APP_FOLDER_NAME="PiMPD_show"    # The folder in your home directory
PYTHON_SCRIPT="mpdshow.py"            # The script to execute
SERVICE_NAME="PiMPD_show"      # What the service will be called
CLEAR_FB_SCRIPT="clear_fb.py"
# -----------------------------------

INSTALL_DIR="/opt/$APP_FOLDER_NAME"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME.service"
HOME_DIR=$(eval echo ~$SUDO_USER)

# Check for root privileges
if [[ $EUID -ne 0 ]]; then
   echo "Error: This script must be run with sudo."
   exit 1
fi

usage() {
    echo "Usage: $0 {--install|--uninstall}"
    exit 1
}

Install() {
    echo "--- Installing Service ---"

    # 1. Copy from Home to /opt
    if [ -d "$HOME_DIR/$APP_FOLDER_NAME" ]; then
        echo "Copying $APP_FOLDER_NAME to $INSTALL_DIR..."
        cp -r "$HOME_DIR/$APP_FOLDER_NAME" /opt/
        # Ensure the user who called sudo still owns the files in /opt
        chown -R $SUDO_USER:$SUDO_USER "$INSTALL_DIR"
    else
        echo "Error: Directory $HOME_DIR/$APP_FOLDER_NAME not found."
        exit 1
    fi

    # 2. Create the Systemd service file
    echo "Creating systemd service at $SERVICE_PATH..."
    PYTHON_BIN=$(which python3)

    cat <<EOF > "$SERVICE_PATH"
[Unit]
Description=Python Service for $APP_FOLDER_NAME
After=network.target
After=mpd.service
Requires=mpd.service

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$PYTHON_BIN $INSTALL_DIR/$PYTHON_SCRIPT
Restart=always
ExecStop=$PYTHON_BIN $INSTALL_DIR/$CLEAR_FB_SCRIPT

[Install]
WantedBy=multi-user.target
EOF

    # 3. Start and enable
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    systemctl start "$SERVICE_NAME"

    echo "Installation finished. Service '$SERVICE_NAME' is now running."
}

uninstall() {
    echo "--- Uninstalling Service ---"

    # 1. Stop and Disable
    echo "Stopping $SERVICE_NAME..."
    systemctl stop "$SERVICE_NAME"
    systemctl disable "$SERVICE_NAME"

    # 2. Remove files
    echo "Removing $SERVICE_PATH and $INSTALL_DIR..."
    rm -f "$SERVICE_PATH"
    rm -rf "$INSTALL_DIR"

    # 3. Cleanup
    systemctl daemon-reload
    systemctl reset-failed

    echo "Uninstallation complete."
}

start() {
    echo "▶️  Starting $SERVICE_NAME..."
    sudo systemctl start $SERVICE_NAME
}

stop() {
    echo "🛑 Stopping $SERVICE_NAME..."
    sudo systemctl stop $SERVICE_NAME
}

restart() {
    echo "🔄 Restarting $SERVICE_NAME..."
    sudo systemctl restart $SERVICE_NAME
}

status() {
    echo "📊 Checking status for $SERVICE_NAME..."
    sudo systemctl status $SERVICE_NAME
}

case "$1" in
    install)   install ;;
    uninstall) uninstall ;;
    start)     start ;;
    stop)      stop ;;
    restart)   restart ;;
    status)    status ;;
    *)
        echo "Usage: $0 {install|uninstall|start|stop|restart|status}"
        exit 1
        ;;
esac

