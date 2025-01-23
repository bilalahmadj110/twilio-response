# Twilio Bulk SMS Sender

A robust Python application for sending bulk SMS messages using Twilio with parallel processing, retry mechanism, and detailed reporting.

## Features

- Parallel message sending using thread pooling
- Progress bar visualization
- Exponential backoff retry mechanism
- Detailed success/failure reporting
- CSV-based contact management
- Customizable message templates

## Prerequisites

- Python 3.8 or higher
- Twilio account (Account SID and Auth Token)
- Valid Twilio phone number

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd twilio-response
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```

2. Update the `.env` file with your Twilio credentials:
```properties
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=your_twilio_phone_number_here
MAX_PARALLEL_MESSAGES=10
MAX_RETRY_ATTEMPTS=3
RETRY_DELAY_SECONDS=5
```

## Preparing Contact List

Create a CSV file named `contacts.csv` with the following format:
```csv
name,phone
John Doe,+1234567890
Jane Smith,+1987654321
```

## Message Template

Edit `message_template.txt` to customize your message. Use `%s` as a placeholder for the recipient's name:
```
Hi %s, welcome to our service! We're excited to have you on board.
```

## Usage

Run the script:
```bash
python send_sms.py
```

The script will:
1. Load contacts from CSV
2. Send messages in parallel
3. Show progress with a progress bar
4. Retry failed messages automatically
5. Generate a detailed report

## Reports

After execution, a report file will be generated with the format `sms_report_YYYYMMDD_HHMMSS.txt` containing:
- Total messages sent
- Success/failure counts
- Success rate
- Total time taken
- List of failed messages with retry attempts

## Error Handling

The application includes:
- Exponential backoff for failed attempts
- Detailed error logging
- CSV validation
- Twilio API error handling

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| TWILIO_ACCOUNT_SID | Twilio Account SID | Required |
| TWILIO_AUTH_TOKEN | Twilio Auth Token | Required |
| TWILIO_PHONE_NUMBER | Twilio Phone Number | Required |
| MAX_PARALLEL_MESSAGES | Number of parallel threads | 10 |
| MAX_RETRY_ATTEMPTS | Maximum retry attempts | 3 |
| RETRY_DELAY_SECONDS | Initial retry delay | 5 |

## Best Practices

1. Always test with a small sample first
2. Monitor your Twilio credit usage
3. Respect rate limits
4. Keep phone numbers in E.164 format
5. Regularly backup your contact lists

## Troubleshooting

Common issues:
- Invalid phone numbers: Ensure E.164 format
- Rate limiting: Adjust MAX_PARALLEL_MESSAGES
- Connection issues: Check internet connectivity
- Authentication errors: Verify Twilio credentials

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Created by: Bilal Ahmad  
Last Updated: October 2023
