""" Main app
"""

import subprocess
from api.main import app
from api.config import config

from helpers.logging_file import Logger


logger = Logger()


if __name__ == '__main__':
    worker_process = subprocess.Popen([
        'rq', 'worker',
        '--name', config.SERVICE_NAME,
        '--with-scheduler',
    ])
    
    logger.info(f"Redis worker scheduler started with process ID {worker_process.pid}")

    app.run(host="0.0.0.0", port=3000)
