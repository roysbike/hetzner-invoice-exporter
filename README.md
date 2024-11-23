# Hetzner Invoice CSV Downloader

Automates logging into Hetzner, extracting usage links, and downloading invoices in CSV format.

## Features

- Stealth mode to avoid detection.
- Supports TOTP-based 2FA.
- Configurable company number via `.env`.

## Requirements

- Python 3.8+
- Playwright
- dotenv
- pyotp

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/hetzner-invoice-csv-downloader.git
   cd hetzner-invoice-csv-downloader
   pip install -r requirements.txt
   ````

.env
````
USERNAME=your_hetzner_username
PASSWORD=your_hetzner_password
TWOFA_SECRET=your_totp_secret_key
COMPANY_NUMBER=K011111
USE_2FA=true
````
