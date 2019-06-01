CREATE TABLE IF NOT EXISTS directory (
    id TEXT PRIMARY KEY,
    dir_name TEXT NOT NULL,
    directories  TEXT NOT NULL,
    files TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS file (
    id TEXT PRIMARY KEY,
    file_name TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    chunks TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chunk (
    chunk_name   TEXT NOT NULL,
    storage TEXT NOT NULL,
    chunk_hash   TEXT NOT NULL,
    PRIMARY KEY(chunk_name, storage)
);
