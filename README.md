# Microservice for downloading files

Microservice helps the work of the main site, that is based on CMS and maintains requests for downloading archives with files.
This service can't do anything but pack files in the archive. Upload files to the server is possible via FTP or CMS.

The ZIP archive is created on the fly on the user's request.
Archives are not saved on the disk; instead, during the compression process binary data is sent in chunks to the user for download.

You can get an archive of the directory with all files inside for download by the hash name of this directory.
For example, `http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/`.
The structure of files for download is following:

```
- photos
    - 3bea29ccabbbf64bdebcc055319c5745
      - 1.jpg
      - 2.jpg
      - 3.jpg
    - af1ad8c76fda2e48ea9aed2937e972ea
      - 1.jpg
      - 2.jpg
```

## Requirements

- [docker](https://docs.docker.com/get-docker/)
- [docker-compose](https://docs.docker.com/compose/install/)

## How to start the service

```bash
docker-compose up --build
```

The server will be running on 8080 port, you can check it out [http://0.0.0.0:8080/](http://0.0.0.0:8080/).

## Config

The project can be configured via `.env` file.

**LOGGING** - enables logging. Possible values are: 0, 1. By default, is enabled.
**INTERVAL_SECS** - limits download speed. Throttling. By default the interval is `0.5`secs.
**PHOTOS_DIR_PATH** - The path of photos directory. By default is `test_photos`.
**CHUNK_SIZE_KB** - the size of data chunk in Kb that will be sent to the user. By default is `250`Kb.

In the result, by default the download speed is limited to 500kb/sec.

## More info

This is an educational project.
