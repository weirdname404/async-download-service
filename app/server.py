import aiofiles
import asyncio
import logging
import os
from typing import Coroutine
from contextlib import suppress
from aiohttp import web, web_request, web_response

# settings
LOGGING = bool(int(os.getenv("LOGGING", 1)))
PHOTOS_DIR_PATH = os.getenv("PHOTOS_DIR_PATH", 'test_photos')
INTERVAL_SECS = float(os.getenv('INTERVAL_SECS', 0.5))
CHUNK_SIZE_KB = int(os.getenv("CHUNK_SIZE_KB", 250))
CHUNK_SIZE_B = CHUNK_SIZE_KB * 1000

logger = logging.getLogger(__name__)


async def send_archive(request: web_request.Request) -> Coroutine:
    """Coroutine that sends file archive as a response to the user's request.

    What it does:
       - Handles request;
       - Checks directory path;
       - Prepares headers;
       - Streams compression.
    """
    archive_hash = request.match_info.get('archive_hash')
    if archive_hash is None:
        raise web.HTTPBadRequest(reason="Archive hash was not provided.")

    if not os.path.exists(f"{PHOTOS_DIR_PATH}/{archive_hash}"):
        raise web.HTTPNotFound(reason="Archive does not exist or was deleted.")

    response = web.StreamResponse()
    response.headers['Content-Type'] = 'application/zip'
    response.headers['Content-Disposition'] = f'attachment; filename="{archive_hash}.zip"'

    # Sending HTTP headers
    await response.prepare(request)
    # Streaming archive
    await _compress_and_stream(archive_hash, response)

    return response


async def handle_index_page(request: web_request.Request) -> Coroutine:
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


async def _compress_and_stream(dirname: str,
                               response: web_response.StreamResponse,
                               chunk_size: int = CHUNK_SIZE_B) -> Coroutine:
    """Support coroutine that streams files compression.

    It spawns a subprocess that compresses the given directory and sends
    bytes of the result by chunks as a response to the user's request.
    """
    # change CWD and compress recursively specific photo directory
    proc = await asyncio.create_subprocess_exec(
        'zip', '-r', '-', dirname,
        cwd=PHOTOS_DIR_PATH,
        stdout=asyncio.subprocess.PIPE
    )
    try:
        while True:
            if proc.stdout.at_eof():
                break
            # read 250kb by default from the buffer
            data = await proc.stdout.read(chunk_size)
            logger.info(f"Sending {dirname} archive chunk ...")
            await response.write(data)
            # network throttling
            await asyncio.sleep(INTERVAL_SECS)
        logger.info("Download is completed.")

    except asyncio.CancelledError:
        logger.info("Download was interrupted.")
        raise
    finally:
        # prevent process leak
        # if the process doesn't exist anymore - OSError will be raised
        with suppress(OSError):
            proc.kill()
            await proc.communicate()
            logger.info(f"Zip process {proc.pid} was killed.")


if __name__ == '__main__':
    # logging setup
    logging.basicConfig(
        format="\n%(asctime)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    if LOGGING:
        logger.setLevel(logging.INFO)
    # web app setup
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', send_archive),
    ])
    web.run_app(app)
