from main import main  # Import the `main` function from the `main` module

app = main()  # Call the `main` function to do the setup and get the Flask app object

if __name__ == "__main__":
    app.run()
