#!/usr/bin/env python3
"""
AWS Prefix List IP Address Updater

This script updates an AWS Managed Prefix List with the current public IP address.
It checks if the current entry exists and updates it if it differs from the current IP.
"""

import os
import sys
import requests
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv


def get_current_ip():
    """Get the current public IP address using ifconfig.me"""
    try:
        response = requests.get("https://ifconfig.me", timeout=5)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Error retrieving current IP address: {e}")
        sys.exit(1)


def update_prefix_list(prefix_list_id, current_ip, description):
    """Update AWS Managed Prefix List with current IP address"""
    # Initialize AWS EC2 client
    ec2 = boto3.client(
        'ec2',
        region_name=os.environ.get('AWS_REGION'),
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )

    try:
        # Get current entries in the prefix list
        response = ec2.get_managed_prefix_list_entries(
            PrefixListId=prefix_list_id,
            MaxResults=100  # Adjust as needed
        )

        entries = response.get('Entries', [])

        # Format current IP for CIDR notation
        current_ip_cidr = f"{current_ip}/32"

        # Check if our IP is already in the list
        existing_entry = None
        for entry in entries:
            if entry.get('Description') == description:
                existing_entry = entry
                break

        if existing_entry:
            # If entry exists but IP differs, update it
            if existing_entry.get('Cidr') != current_ip_cidr:
                print(f"Updating existing entry from {
                      existing_entry.get('Cidr')} to {current_ip_cidr}")

                # Get current version
                prefix_list_info = ec2.describe_managed_prefix_lists(
                    PrefixListIds=[prefix_list_id]
                )
                current_version = prefix_list_info['PrefixLists'][0]['Version']

                # Modify the prefix list
                ec2.modify_managed_prefix_list(
                    PrefixListId=prefix_list_id,
                    CurrentVersion=current_version,
                    AddEntries=[
                        {
                            'Cidr': current_ip_cidr,
                            'Description': description
                        }
                    ],
                    RemoveEntries=[
                        {
                            'Cidr': existing_entry.get('Cidr'),
                            'Description': description
                        }
                    ]
                )
                print(f"Successfully updated prefix list with new IP: {
                      current_ip_cidr}")
            else:
                print(f"No update needed. Current IP {
                      current_ip_cidr} already in prefix list.")
        else:
            # If no entry with our description exists, add a new one
            prefix_list_info = ec2.describe_managed_prefix_lists(
                PrefixListIds=[prefix_list_id]
            )
            current_version = prefix_list_info['PrefixLists'][0]['Version']

            ec2.modify_managed_prefix_list(
                PrefixListId=prefix_list_id,
                CurrentVersion=current_version,
                AddEntries=[
                    {
                        'Cidr': current_ip_cidr,
                        'Description': description
                    }
                ]
            )
            print(f"Added new entry to prefix list with IP: {current_ip_cidr}")

    except ClientError as e:
        print(f"AWS Error: {e}")
        sys.exit(1)


def main():
    """Main function"""
    # Load environment variables from .env file
    load_dotenv()

    # Check required environment variables
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_REGION',
        'PREFIX_LIST_ID'
    ]

    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        print(f"Missing required environment variables: {
              ', '.join(missing_vars)}")
        print("Please set these in your .env file")
        sys.exit(1)

    # Get prefix list ID from environment
    prefix_list_id = os.environ.get('PREFIX_LIST_ID')

    # Optional description from environment
    description = os.environ.get('PREFIX_ENTRY_DESCRIPTION')

    # Get current public IP
    current_ip = get_current_ip()
    print(f"Current public IP address: {current_ip}")

    print(f"Prefix list id: {prefix_list_id}")
    print(f"IP description: {description}")

    # Update prefix list
    update_prefix_list(prefix_list_id, current_ip, description)


if __name__ == "__main__":
    main()
