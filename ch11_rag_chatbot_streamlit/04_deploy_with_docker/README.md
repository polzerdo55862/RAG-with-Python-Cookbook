# Streamlit App Deployment with Docker

This project demonstrates how to deploy a Streamlit application using Docker. It includes all necessary files to build and run the application in a containerized environment.

## Project Structure

```
11_04_deploy_with_docker
├── Dockerfile
├── entrypoint.sh
├── requirements.txt
├── streamlit_app.py
└── README.md
```

## Getting Started

To get started with this project, follow the steps below:

### Prerequisites

- Ensure you have Docker installed on your machine. You can download it from [Docker's official website](https://www.docker.com/get-started).

### Building the Docker Image

1. Open a terminal and navigate to the project directory:

   ```
   cd C:\Users\z004j58u\repos\others\rag-oreily-book\code\11_building_rag_apps\11_04_deploy_with_docker
   ```

2. Build the Docker image using the following command:

   ```
   docker build -t my-streamlit-app .
   ```

### Running the Docker Container

After building the image, you can run the Docker container with the following command:

```
docker run -p 8501:8501 my-streamlit-app
```

This command maps port 8501 on your host machine to port 8501 in the container, allowing you to access the Streamlit app in your web browser.

### Accessing the Application

Once the container is running, open your web browser and go to:

```
http://localhost:8501
```

You should see your Streamlit application running.

## Additional Information

- **Dockerfile**: Contains instructions for building the Docker image.
- **entrypoint.sh**: Script executed when the Docker container starts.
- **requirements.txt**: Lists all Python packages required for the application.
- **streamlit_app.py**: Main Python file for the Streamlit application.

Feel free to modify the application as needed and rebuild the Docker image to see your changes.