#!/bin/bash
apt update

install_dir="/opt/Hiddify-Bot"
repository_url="https://github.com/ReturnFI/Hiddify-Bot.git"

function check_and_install_package {
    if ! dpkg -s $1 >/dev/null 2>&1; then
        apt install -y $1
    else
        echo "$1 is already installed."
    fi
}

packages=(python3 python3-pip git python3-dev python3-venv docker docker-compose)
for package in "${packages[@]}"; do
    check_and_install_package $package
done

sleep 2

if [ -d "$install_dir" ]; then
    rm -rf "$install_dir"
fi
sleep 2

git clone -b Dev "$repository_url" "$install_dir"

cd "$install_dir"

clear
echo "Please provide the following environment variables:"

function get_non_empty_input {
    local prompt=$1
    local input_var
    while true; do
        read -p "$prompt" input_var
        if [ -n "$input_var" ]; then
            echo $input_var
            break
        else
            echo "Input cannot be empty. Please provide a valid value."
        fi
    done
}

ALLOWED_USER_IDS=$(get_non_empty_input "Chat ID: ")
ADMIN_UUID=$(get_non_empty_input "Admin uuid: ")
ADMIN_URLAPI=$(get_non_empty_input "Admin panel url: ")
SUBLINK_URL=$(get_non_empty_input "Panel sublink url: ")
TELEGRAM_TOKEN=$(get_non_empty_input "Bot Token: ")

env_file_path="$install_dir/.env"
echo "ALLOWED_USER_IDS=$ALLOWED_USER_IDS" > "$env_file_path"
echo "ADMIN_UUID=$ADMIN_UUID" >> "$env_file_path"
echo "ADMIN_URLAPI=$ADMIN_URLAPI" >> "$env_file_path"
echo "SUBLINK_URL=$SUBLINK_URL" >> "$env_file_path"
echo "TELEGRAM_TOKEN=$TELEGRAM_TOKEN" >> "$env_file_path"

docker-compose up -d

if [ "$(docker ps -q -f name=hiddifybot)" ]; then
    clear
    echo "HiddifyBot Docker containers are now up and running."
else
    clear
    echo "Failed to start HiddifyBot Docker containers. Please check the logs for more details."
fi
