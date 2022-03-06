# Starling Server - A simplified Starling API

An API for working with a validated subset of
the [Starling Bank API](https://developer.starlingbank.com/docs#api-reference-1).

## Installation

```shell
$ pip install starling-server
```

To configure:

```shell
$ starling-server init
```

After `init`, follow the instructions by adding a token per file in the folder specified.

## Usage

```shell
$ starling-server go
$ # or with uvicorn directly
$ uvicorn starling_server.main:app
```

## Documentation

API
: `http://127.0.0.1:8000/docs`

Package
: `docs/build/html/index.html`

## Testing

```shell
$ pytest tests
```

## License

This project is licensed under the MIT License - see file [LICENSE.md](LICENSE.md) for details.

## Version history

0.1
: Initial release