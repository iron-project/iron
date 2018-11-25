CREATE TABLE directory (
    dir_path TEXT PRIMARY KEY,
    dir_name TEXT NOT NULL,
    sub_dir  TEXT NOT NULL,
    sub_file TEXT NOT NULL
);

CREATE TABLE file (
    file_path TEXT PRIMARY KEY,
    file_name TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    sub_chunk TEXT NOT NULL
);

CREATE TABLE chunk (
    chunk_id     TEXT NOT NULL,
    chunk_source TEXT NOT NULL,
    chunk_hash   TEXT NOT NULL,
    PRIMARY KEY(chunk_id, chunk_source)
);