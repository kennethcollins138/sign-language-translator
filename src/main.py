from src.core import logging


def main():
    logger = logging.setup_logger(__name__)
    logger.info("Starting the application")


if __name__ == "__main__":
    main()
