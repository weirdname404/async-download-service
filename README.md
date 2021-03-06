# Microservice for downloading files

The microservice is designed to support main CMS platform by maintaining requests for downloading archives with files.
This service can't do anything but pack files in the archive and send it in chunks to the user.
Uploading files to the server is only possible via FTP or CMS.

The ZIP archive is created on the fly on the user's request.
Archives are not saved on the disk; instead, during the compression process binary data is sent in chunks to the user for download.

The structure of files for download on the server is following:

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

You can download an archive of the directory with all files inside by providing the hash name of this directory in GET request.

For example, `http://HOSTNAME.com/archive/3bea29ccabbbf64bdebcc055319c5745/`.

## Requirements

- [docker](https://docs.docker.com/get-docker/)
- [docker-compose](https://docs.docker.com/compose/install/)

After all requirements are successfully installed on your machine, you can fire up the project.

## How to start the service

You can start the service with the default settings.

```bash
docker-compose up
```

The server will be running on 8080 port, you can check it out [http://0.0.0.0:8080/](http://0.0.0.0:8080/).

Note: By default, the download speed is limited to 500kb/sec.

## Config

The project can be configured via `.env` file. Just create it and setup ENV VARS there.

**LOGGING** - enables logging. Possible values are: 0, 1. By default, is enabled.

**INTERVAL_SECS** - limits download speed. Throttling. By default the interval is `0.5`secs.

**PHOTOS_DIR_PATH** - The path of photos directory. By default is `test_photos`.

**CHUNK_SIZE_KB** - the size of data chunk in Kb that will be sent to the user. By default is `250`Kb.

After you've finished with your custom configuration, start the project using special `docker-compose.env.yml`
that will pick up your new `.env` file.

```bash
docker-compose down && docker-compose -f docker-compose.env.yml up
```

## More info

This is an educational project.
