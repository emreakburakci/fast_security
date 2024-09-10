# Fast Security

Fast Security is a project to focus on implementing security features using FastAPI and Python. This README provides an overview of the project structure and setup instructions.

## Project Structure

The repository contains the following key files and directories:

- `main.py`: The main application file
- `database.py`: Database-related functionality
- `security.py`: Security-related implementations
- `requirements.txt`: List of Python dependencies
- `Dockerfile`: Instructions for building a Docker image
- `docker-compose.yml`: Docker Compose configuration file
- `.gitignore`: Specifies intentionally untracked files to ignore

## Setup

### Prerequisites

- Python 3.12
- Docker (optional, for containerized setup)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/emreakburakci/fast_security.git
cd fast_security
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate # On Windows, use venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

To run the application locally:

```bash
python main.py
```

### Docker Setup

To run the application using Docker:

1. Build the Docker image:

```bash
docker build -t fast_security .
```
2. Run the container:

```bash
docker-compose up
```
## Database

The project uses a SQLite database (`student_enrollment.db`). Make sure you have the necessary permissions to read and write to this file.