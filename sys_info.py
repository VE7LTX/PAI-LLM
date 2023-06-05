import datetime
import logging
import psutil
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

def get_system_info():
    # Fetch system info
    try:
        time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        system_info = {
            "time_stamp": time_stamp,
            "year": datetime.datetime.now().year,
            "month": datetime.datetime.now().month,
            "day": datetime.datetime.now().day,
            "hour": datetime.datetime.now().hour,
            "minute": datetime.datetime.now().minute,
            "second": datetime.datetime.now().second,
            "microsecond": datetime.datetime.now().microsecond,
            "timezone": datetime.datetime.now().tzinfo,
            "system": sys.platform,
            "cpu_count": psutil.cpu_count(),
            "cpu_freq": psutil.cpu_freq(),
            "cpu_percent": psutil.cpu_percent(),
            "virtual_memory": psutil.virtual_memory(),
            "swap_memory": psutil.swap_memory(),
            "disk_usage": psutil.disk_usage("/"),
            "disk_partitions": psutil.disk_partitions(),
            "net_io_counters": psutil.net_io_counters(),
            "net_connections": psutil.net_connections(),
            "net_if_addrs": psutil.net_if_addrs(),
            "net_if_stats": psutil.net_if_stats()
        }
        return system_info

    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise
