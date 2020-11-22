import aiofiles
import asyncio
import logging
import os
from aiohttp import web

LOGGING = bool(int(os.getenv("LOGGING")))
PHOTOS_DIR_PATH = os.getenv("PHOTOS_DIR_PATH")
INTERVAL_SECS = float(os.getenv('INTERVAL_SECS'))
CHUNK_SIZE_KB = int(os.getenv("CHUNK_SIZE_KB"))

if LOGGING:
    logging.basicConfig(
        level=logging.INFO,
        format="\n%(asctime)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )


async def send_archive(request):
    """- Handles request;
       - Checks directory path;
       - Prepares headers;
       - Streams compression."""
    archive_hash = request.match_info.get('archive_hash')
    if archive_hash is None:
        raise web.HTTPBadRequest(reason="Archive hash was not provided.")

    if os.path.exists(f"{PHOTOS_DIR_PATH}/{archive_hash}") is False:
        raise web.HTTPNotFound(reason="Archive does not exist or was deleted.")

    response = web.StreamResponse()
    response.headers['Content-Type'] = 'application/zip'
    response.headers['Content-Disposition'] = f'attachment; filename="{archive_hash}.zip"'

    # Sending HTTP headers
    await response.prepare(request)
    # Streaming archive
    await _compress_and_stream(archive_hash, response)

    return response


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


async def _compress_and_stream(dirname, response,
                               chunk_size=CHUNK_SIZE_KB * 1000):
    """Spawns subprocess that compresses given directory and sends
       bytes of the result by chunks."""
    # change CWD and compress recursively specific photo directory
    cmd = f"cd {PHOTOS_DIR_PATH} && zip -r - {dirname}"
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE
    )
    try:
        while True:
            if proc.stdout.at_eof():
                break
            # read 250kb by default from the buffer
            data = await proc.stdout.read(chunk_size)
            logging.info(f"Sending {dirname} archive chunk ...")
            await response.write(data)
            # network throttling
            await asyncio.sleep(INTERVAL_SECS)
        logging.info("Download is completed.")

    # handle errors to kill subprocesses
    except (SystemExit, Exception, RuntimeError):
        raise
    except asyncio.CancelledError:
        logging.info("Download was interrupted.")
    finally:
        # prevent process leak
        try:
            proc.kill()
            await proc.communicate()
            logging.info(f"Zip process {proc.pid} was killed.")
        # the process doesn't exists anymore
        except OSError:
            pass


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', send_archive),
    ])
    web.run_app(app)
