from api.main import app

from helpers.logging_file import Logger


logger = Logger()


if __name__ == "__main__":
    # Run the app
    app.run()
