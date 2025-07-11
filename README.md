# Piclean API

An awesome FastAPI-based REST API for interacting with Picrew, the popular avatar creator platform. This API provides endpoints to discover, search, and retrieve detailed information about Picrew image makers.

## Features

- **Discovery**: Browse trending and popular image makers
- **Search**: Find specific image makers with advanced filtering options
- **Image Maker Data**: Get all the information you would ever need about individual image makers.

## Why?
- For fun
- To make archival easier
- To later make an alternative frontend to picrew
- Picrew is making profit when the artists of the platform aren't

## Usage

1. Clone the repository:
```bash
git clone https://github.com/sebastian-92/piclean-api
cd piclean-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the API:
```bash
fastapi run
```

The API will be available at `http://localhost:8000`

## Dependencies

- **FastAPI**: Modern, fast web framework for building APIs
- **requests**: HTTP library for making API calls
- **beautifulsoup4**: HTML parsing library
- **py_mini_racer**: JavaScript engine for Python

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Disclaimer

This API is for educational and development purposes. Please respect Picrew's terms of service and rate limits when using this API. The author is not affiliated with Picrew. Please still obey the individual image creators licenses.

## License
This project is licensed under the GNU AGPL v3.0 or later :)

## Support

If you encounter any issues or have questions, please open an issue on the repository.