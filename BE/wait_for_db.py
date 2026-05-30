import time

import pymysql

import config


def wait_for_db(timeout_seconds: int = 60) -> None:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None

    while time.time() < deadline:
        try:
            connection = pymysql.connect(
                host=config.DB_HOST,
                port=int(config.DB_PORT),
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                database=config.DB_NAME,
            )
            connection.close()
            return
        except pymysql.Error as error:
            last_error = error
            time.sleep(2)

    raise RuntimeError("Database not ready") from last_error


if __name__ == "__main__":
    wait_for_db()
    print("Database is ready")
