LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

NOISY_LOGGERS: list[str] = [
    'urllib3',
    'boto3',
    'botocore',
    's3transfer',
    'requests',
]
