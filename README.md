# artstore
`artstore` (think "artifact store") provides lightweight management of project artifacts to a directory hierarchy via REST api.  The expectation is that this directory hierarchy is then served via an HTTP server (e.g. nginx).

## Dependencies
- Python 3.9
- Flask

## Configuration
`artstore.json` is read at startup time with the following parameters:
- `base_path` - Path to the root of the directory hierarchy managed by artstore
- `temp_path` - Path to a temporary directory for storage of files which have been uploaded but not yet handled

## Project configuration
`projects.json` holds configuration information for projects managed by artstore.  A project has its own directory relative to `base_path`. A project can have one or more artifact "items" of various types. Each item has its own directory relative to the project's directory.

### Item types
- `html` - an `.html` file (presumably `index.html`) can be uploaded to artstore and will be stored the item's directory

- `tgz` - a `.tar.gz` file can be uploaded to artstore and will be extracted to the item's directory.  It is assumed that the directory will include an `index.html` file.

- `zip` - a `.zip` file can be uploaded to artstore and will be extracted to the item's directory. It is assumed that the directory will include an `index.html` file.

- `collection` - a file can be uploaded to artstore and will be stored in the item's directory.  The last `depth` artifact files in the item directory will be retained.  An `index.html` file will be regenerated for the item's directory with links to all artifact files.  It is assumed that the filename will be unique (e.g. containing a version number).


## REST API

`POST artstore/<project>/<item>`		- upload a file with metadata for the specified project and item.  Expected Content-Type header is `multipart/form-data` with key `item`

`GET artstore/` - return list of projects

`POST artstore/<project>` - add a project configured based on the json passed in the request (see above project configuration).  Expected Content-Type header is `application/json`.

`GET artstore/<project>` - get a project's current configuration 

TODO: `PUT artstore/<project>` - update a project's configuration - what would this do to existing artifacts?

`DELETE artstore/<project>` - delete a project