# 🔐 Password Wallet CLI

A secure, offline command-line password manager that stores your credentials locally with AES encryption.

## Features

- 🔒 **Strong Encryption**: AES encryption with PBKDF2HMAC key derivation
- 🏠 **Offline First**: All data stored locally, no cloud dependencies
- 🎯 **Simple CLI**: Easy-to-use terminal interface
- 🔍 **Search & Filter**: Find entries quickly by site name
- 🎲 **Password Generator**: Create strong passwords with customizable options
- 💾 **Secure Storage**: Master password protects your entire vault

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the password wallet:

```bash
python password_wallet.py
```

### First Run

- You'll be prompted to create a master password
- Choose a strong password - you'll need it every time you access your vault

### Menu Options

1. **Add New Entry** - Store credentials for a new site/service
2. **View All Entries** - List all stored credentials (passwords hidden)
3. **Search by Site** - Find specific entries and optionally reveal passwords
4. **Generate Password** - Create strong passwords with custom criteria
5. **Exit** - Safely close the application

## Security Features

- **AES Encryption**: Your vault is encrypted with industry-standard AES
- **PBKDF2HMAC**: Master password is processed with 100,000 iterations
- **Salt Storage**: Random salt prevents rainbow table attacks
- **No Plaintext**: Passwords are never stored in plain text

## File Structure

```
data/
├── vault.enc    # Encrypted password entries
└── salt.key     # Salt for key derivation
```

## Requirements

- Python 3.6+
- cryptography>=41.0.7
- tabulate>=0.9.0

## Security Notes

- Keep your master password secure and memorable
- The vault file is encrypted, but keep backups safe
- This tool is designed for local, offline use
- No data is transmitted over the internet
