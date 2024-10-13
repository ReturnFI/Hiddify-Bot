# Hiddify Bot

Hiddify Bot is a Telegram bot for managing Hiddify users, providing server information, backing up data, and managing admin roles. This bot enables easy user management and control over a Hiddify server via simple Telegram commands.

## Features
- **Add and Show Users**: Easily add and view users on your Hiddify server.
- **Server Information**: Retrieve real-time server statistics and usage information.
- **Backup**: Backup server configurations and user data directly from Telegram.
- **Admin Management**: Manage admin roles, delete users, and reset user data.
- **Help Command**: Get help on how to use the bot and its features.

## Requirements

To use the bot , you will need the following information:
1. **Chat ID:** You need to obtain this from the [@userinfobot](https://t.me/userinfobot).
2. **Admin uuid:** Enter your admin uuid.
3. **Admin url:** Enter your panel url.(https://example.com/DfLECy9v8KwA09nAYifGEO9T/)
4. **Sublink url:** Enter your panel sublink.(https://sublink.example.com/cR4sh1oudvx12NaZOg603/)
5. **Bot Token:** You need to obtain this from the [@botfather](https://t.me/BotFather).

## Installation

```shell
bash <(curl https://raw.githubusercontent.com/ReturnFI/Hiddify-Bot/main/install.sh)
```

## Usage

Once the bot is running, you can interact with it via Telegram commands.

### Main Commands:
- `/start`: Start the bot and display the main menu.
- **Add User**: Add a new user to the Hiddify server.
- **Show Users**: View existing users and manage them (delete, reset data).
- **Server Info**: Get real-time server information (e.g., traffic, load).
- **Backup**: Create a backup of the server.
- **Admin**: Manage admin users (list, delete admins).

### Admin Commands:
Only authorized users can access administrative commands like:
- **Delete Admin**: Remove a user from the admin list.
- **Reset Traffic**: Reset a user’s traffic usage.
- **Reset Days**: Reset the remaining days of a user’s package.
  
### Inline Queries:
Use inline queries in any chat to search for users by their UUID and perform actions such as deleting or resetting them.

## Customization

The bot currently supports multiple languages (default: Persian). You can add or modify languages by editing the `lang.json` file in the `language` directory and .

## Contribution

Contributions are welcome! Feel free to submit issues and pull requests to enhance the bot.

## Disclaimer
This project is only for personal learning and communication, please do not use it for illegal purposes, please do not use it in a production environment

---
