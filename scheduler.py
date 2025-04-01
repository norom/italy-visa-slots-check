import schedule
import time
import subprocess
import logging
import random
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("appointment_scheduler")

def run_appointment_monitor():
    """Run the appointment_monitor.py script"""
    logger.info(f"Starting scheduled appointment check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run the appointment_monitor.py script
        process = subprocess.Popen(['python3', 'appointment_monitor.py'], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.STDOUT,
                                  universal_newlines=True)
        
        # Log output in real-time
        for line in process.stdout:
            logger.info(line.strip())
            
        process.wait()
        
        logger.info(f"Appointment check completed with exit code {process.returncode}")
        return process.returncode
    except Exception as e:
        logger.error(f"Error running appointment check: {e}")
        return -1

def schedule_next_run():
    """Schedule the next run with random variance of ±10 minutes"""
    # Calculate a random offset between -10 and +10 minutes
    minutes_offset = random.randint(-10, 10)
    next_run = datetime.now() + timedelta(hours=1, minutes=minutes_offset)
    
    # Clear existing jobs and schedule the new one
    schedule.clear()
    schedule.at(next_run.strftime("%H:%M")).do(run_and_reschedule)
    
    logger.info(f"Next check scheduled for {next_run.strftime('%Y-%m-%d %H:%M:%S')} "
                f"(standard hour {minutes_offset:+d} minutes)")
    
def run_and_reschedule():
    """Run the monitor and schedule the next run"""
    run_appointment_monitor()
    schedule_next_run()

def main():
    """Main scheduler function"""
    logger.info("Appointment scheduler starting...")
    
    # Run immediately on startup
    logger.info("Running initial check...")
    run_appointment_monitor()
    
    # Schedule next run
    schedule_next_run()
    
    logger.info("Scheduler active. Will check for appointments approximately every hour (±10 minutes).")
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check for pending tasks every minute

if __name__ == "__main__":
    main()