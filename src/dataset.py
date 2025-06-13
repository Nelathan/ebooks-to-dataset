import os
import pyarrow as pa
import pyarrow.ipc as ipc

def update_dataset(book_entry, dataset_path):
    """
    Overwrite any existing entry for the same book (by link) in the Arrow IPC dataset.
    """
    fields = ["link", "title", "author", "text", "language"]
    arr = {k: [book_entry.get(k, "")] for k in fields}
    new_table = pa.table(arr)

    if os.path.exists(dataset_path):
        with open(dataset_path, 'rb') as f:
            reader = ipc.RecordBatchFileReader(f)
            old_table = reader.read_all()
        mask = [val != book_entry["link"] for val in old_table.column("link").to_pylist()]
        filtered_table = old_table.filter(mask)
        table = pa.concat_tables([filtered_table, new_table])
    else:
        table = new_table

    with open(dataset_path, 'wb') as f:
        writer = ipc.RecordBatchFileWriter(f, table.schema)
        writer.write_table(table)
        writer.close()

def read_dataset(dataset_path):
    """
    Read the Arrow IPC dataset and return a pyarrow Table.
    """
    if not os.path.exists(dataset_path):
        return None
    with open(dataset_path, 'rb') as f:
        reader = ipc.RecordBatchFileReader(f)
        return reader.read_all()
