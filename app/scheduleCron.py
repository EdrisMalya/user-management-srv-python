from crontab import CronTab

my_cron = CronTab(user="root")

job = my_cron.new(
    command="PYTHONPATH=/app /usr/local/bin/python /app/app/check_expiry.py >> /var/log/cron.log 2>&1"
)

job.hour.every(20)

my_cron.write()
