# YugiAPI Frontend

## Overview

A Yu-Gi-Oh! REST API frontend interface that allows users to interact with the [Yu-Gi-Oh! Database REST API](https://github.com/man-netcat/yugiapi). This web application provides a user-friendly search interface to explore information about Yu-Gi-Oh! cards, archetypes, and sets.

## Prerequisites

Before running the Yu-Gi-Oh! Web Application, ensure that you have the following prerequisites installed:

- Python 3.11 or higher
- Flask
- Requests
- Requests-cache
- RapidFuzz

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/yugioh-web-app.git
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Running the Web Application

To run the web application, execute the following command:

```bash
python frontend.py [--debug]
```

- `--debug`: Enable debug mode.

### Connecting to the API

The web application depends on the Yu-Gi-Oh! Database REST API. Ensure that the API is running and accessible before starting the web application.

### Accessing the Web Application

Open your web browser and navigate to:

```
http://localhost:3000
```

This will take you to the main page of the Yu-Gi-Oh! Web Application.

## Features

- **Search Interface**: Use the search bar to find cards, archetypes, and sets. The application performs fuzzy matching to provide relevant results.

- **Detailed Results**: Click on a card, archetype, or set to view detailed information, including related cards and support.

## Notes

- The web application communicates with the Yu-Gi-Oh! Database REST API to fetch and display data.
- Debug mode is available for development. Do not use this for production deployments.

## Contributing

Feel free to contribute by opening issues, providing suggestions, or submitting pull requests. Contributions are welcome!
