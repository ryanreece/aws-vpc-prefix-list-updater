# AWS Prefix List IP Updater

This script automatically updates an AWS Managed Prefix List with your current public IP address. It's particularly useful for maintaining dynamic security group rules that need to reference your changing home or office IP address.

## Purpose

When working with AWS resources that require IP-based access controls (such as security groups, network ACLs, or VPC endpoint policies), maintaining an up-to-date list of allowed IP addresses can be challenging if you have a dynamic IP. This script solves this problem by:

1. Detecting your current public IP address
2. Checking if it exists in a specified AWS Managed Prefix List
3. Updating the prefix list entry if your IP has changed
4. Adding a new entry if no matching entry exists

By using a Managed Prefix List as a single source of truth for your IP, you can reference the prefix list in multiple AWS resources and only need to update in one place.

## Prerequisites

- Python 3.6 or higher
- AWS account with appropriate permissions
- IAM credentials with permissions to modify the target prefix list

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/aws-prefix-list-updater.git
   cd aws-prefix-list-updater
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On Linux/macOS
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file with your credentials and settings:
   ```
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   AWS_REGION=us-east-1
   PREFIX_LIST_ID=pl-08efdb58d1be23fa2
   PREFIX_ENTRY_DESCRIPTION=My home IP
   ```

## Required IAM Permissions

The AWS user or role requires the following permissions to modify the prefix list:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PrefixListModification",
            "Effect": "Allow",
            "Action": [
                "ec2:GetManagedPrefixListEntries",
                "ec2:DescribeManagedPrefixLists",
                "ec2:ModifyManagedPrefixList"
            ],
            "Resource": "arn:aws:ec2:*:*:prefix-list/pl-08efdb58d1be23fa2"
        }
    ]
}
```

## Usage

Run the script:

```bash
python aws_prefix_list_updater.py
```

### Expected Output

When running the script, you'll see output similar to:

```
Current public IP address: 203.0.113.42
Updating existing entry from 198.51.100.17/32 to 203.0.113.42/32
Successfully updated prefix list with new IP: 203.0.113.42/32
```

Or if your IP hasn't changed:

```
Current public IP address: 203.0.113.42
No update needed. Current IP 203.0.113.42/32 already in prefix list.
```

## Automation Tips

For automatic updates when your IP changes, consider:

### Using Cron (Linux/macOS)

Set up a cron job to run the script periodically:

```bash
# Edit crontab
crontab -e

# Add a line to run every hour
0 * * * * cd /path/to/aws-prefix-list-updater && /path/to/aws-prefix-list-updater/venv/bin/python /path/to/aws-prefix-list-updater/aws_prefix_list_updater.py >> /path/to/aws-prefix-list-updater/updater.log 2>&1
```

### Using Task Scheduler (Windows)

1. Create a batch file `run_updater.bat`:
   ```batch
   @echo off
   cd /d C:\path\to\aws-prefix-list-updater
   call venv\Scripts\activate
   python aws_prefix_list_updater.py
   ```

2. Add this batch file to Windows Task Scheduler to run at your desired interval.

## Troubleshooting

### Common Issues:

1. **Authentication Errors**:
   - Check that your AWS credentials are correct in the `.env` file
   - Verify the IAM user/role has the correct permissions

2. **Prefix List Not Found**:
   - Ensure the PREFIX_LIST_ID in your `.env` file is correct
   - Verify the prefix list exists in the specified AWS region

3. **IP Address Retrieval Fails**:
   - Check your internet connection
   - Try an alternative service if ifconfig.me is unavailable

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
