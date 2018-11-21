CREATE TABLE directory (
    dir_path TEXT PRIMARY KEY,
    dir_name TEXT,
    sub_dir  TEXT,
    sub_file TEXT
    );

CREATE TABLE file (
    file_path TEXT PRIMARY KEY,
    file_name TEXT,
    sub_chunk TEXT
    );

CREATE TABLE chunk (
    chunk_id     TEXT PRIMARY KEY,
    chunk_source TEXT,
    chunk_hash   TEXT,
    chunk_size   TEXT
    );