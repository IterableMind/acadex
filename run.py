# from acadex import create_app

# # run app
# if __name__ == '__main__':
#   create_app()
  
from . import create_app

# run app
if __name__ == '__main__':
    app = create_app()  # Create the app
    app.run(debug=True)  # Run the app
