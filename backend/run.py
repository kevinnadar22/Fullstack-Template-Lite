"""
Application entry point for running the Hair Try-On backend server.

This module configures the Python path and provides a CLI command to start
the Uvicorn development server with customizable host, port, and
reload options.
"""

import click
import uvicorn


@click.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
@click.option("--workers", default=1, help="Number of worker processes")
def run(host, port, reload, workers):
    """Run the development server"""
    uvicorn.run(
        "app.__main__:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
    )


if __name__ == "__main__":
    run()
