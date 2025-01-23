import os
import pandas as pd
from dotenv import load_dotenv
from twilio.rest import Client
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Dict
import logging
from tqdm import tqdm
from datetime import datetime
import time
from functools import wraps
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def exponential_backoff(max_attempts: int, initial_delay: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt == max_attempts:
                        raise e
                    
                    # Calculate delay with exponential backoff and jitter
                    delay = (initial_delay * (2 ** (attempt - 1))) + random.uniform(0, 1)
                    logger.info(f"Retry attempt {attempt}/{max_attempts} after {delay:.2f} seconds")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

class SMSSender:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize Twilio client
        self.client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
        self.max_workers = int(os.getenv('MAX_PARALLEL_MESSAGES', 10))
        self.max_retry_attempts = int(os.getenv('MAX_RETRY_ATTEMPTS', 3))
        self.retry_delay = int(os.getenv('RETRY_DELAY_SECONDS', 5))
        
        # Load message template
        with open('message_template.txt', 'r') as file:
            self.message_template = file.read().strip()
        
        self.results: Dict[str, list] = {
            'success': [],
            'failed': [],
            'retry_attempts': {}  # Track retry attempts per contact
        }

    def load_contacts(self, csv_path: str) -> List[Tuple[str, str]]:
        """Load contacts from CSV file."""
        try:
            df = pd.read_csv(csv_path)
            return list(zip(df['name'].tolist(), df['phone'].tolist()))
        except Exception as e:
            logger.error(f"Error loading CSV file: {e}")
            raise

    @exponential_backoff(max_attempts=lambda self: self.max_retry_attempts, 
                        initial_delay=lambda self: self.retry_delay)
    def send_message_with_retry(self, name: str, phone: str) -> bool:
        """Send single SMS with retry mechanism."""
        message = self.message_template % name
        self.client.messages.create(
            body=message,
            from_=self.from_number,
            to=phone
        )
        return True

    def send_single_message(self, contact: Tuple[str, str]) -> Tuple[bool, Tuple[str, str], int]:
        """Send SMS to a single contact with retry tracking."""
        name, phone = contact
        retry_count = 0
        
        try:
            success = self.send_message_with_retry(name, phone)
            logger.info(f"Successfully sent message to {name} at {phone}")
            return True, contact, retry_count
        except Exception as e:
            logger.error(f"Failed to send message to {name} at {phone} after {self.max_retry_attempts} attempts: {e}")
            return False, contact, retry_count

    def generate_report(self, successful: int, failed: int, total_time: float) -> str:
        """Generate a detailed report including retry information."""
        report = f"""
SMS Sending Report
=================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
--------
Total Messages: {successful + failed}
Successful: {successful}
Failed: {failed}
Success Rate: {(successful/(successful + failed)*100):.2f}%
Total Time: {total_time:.2f} seconds
Average Time per Message: {total_time/(successful + failed):.2f} seconds

Failed Messages (After {self.max_retry_attempts} retry attempts):
-----------------------------------------
"""
        for name, phone in self.results['failed']:
            retry_count = self.results['retry_attempts'].get((name, phone), 0)
            report += f"- {name} ({phone}) - Retries: {retry_count}\n"
        
        return report

    def send_bulk_messages(self, csv_path: str) -> None:
        """Send messages in parallel using thread pool with progress bar."""
        contacts = self.load_contacts(csv_path)
        successful = 0
        failed = 0
        start_time = datetime.now()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.send_single_message, contact) for contact in contacts]
            
            # Create progress bar
            with tqdm(total=len(contacts), desc="Sending messages") as pbar:
                for future in as_completed(futures):
                    success, contact, retries = future.result()
                    self.results['retry_attempts'][contact] = retries
                    
                    if success:
                        successful += 1
                        self.results['success'].append(contact)
                    else:
                        failed += 1
                        self.results['failed'].append(contact)
                    pbar.update(1)

        total_time = (datetime.now() - start_time).total_seconds()
        
        # Generate and save report
        report = self.generate_report(successful, failed, total_time)
        report_filename = f"sms_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_filename, 'w') as f:
            f.write(report)
        
        logger.info(f"Completed sending messages. Success: {successful}, Failed: {failed}")
        logger.info(f"Detailed report saved to {report_filename}")

def main():
    try:
        sender = SMSSender()
        sender.send_bulk_messages('contacts.csv')
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main()
