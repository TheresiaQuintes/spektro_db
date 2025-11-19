import h5py

class H5Object:
    def __init__(self, h5node, writable=False, auto_flush=True):
        self._node = h5node
        self._writable = writable

        # Track welche Keys Attribute vs Datasets sind
        self._attrs_keys = set()
        self._datasets_keys = set()
        self._attrs_to_delete = set()
        self._datasets_to_delete = set()

        self._auto_flush = auto_flush

        # Rekursiv Gruppen/Datasets laden
        for key, item in h5node.items():
            if isinstance(item, h5py.Group):
                setattr(self, key, H5Object(item, writable=writable))
            else:
                setattr(self, key, item[()])  # Dataset laden
                self._datasets_keys.add(key)

        # Attribute der Gruppe
        for key, value in h5node.attrs.items():
            setattr(self, key, value)
            self._attrs_keys.add(key)

    def set_attr(self, key, value):
        setattr(self, key, value)
        self._attrs_keys.add(key)
        if key in self._datasets_keys:
            self._datasets_keys.remove(key)


    def set_dataset(self, key, value):
        setattr(self, key, value)
        self._datasets_keys.add(key)
        if key in self._attrs_keys:
            self._attrs_keys.remove(key)

    def delete_attr(self, key):
        """Markiert ein Attribut zum Löschen beim nächsten sync."""
        self._attrs_to_delete.add(key)
        self._attrs_keys.discard(key)
        if hasattr(self, key):
            delattr(self, key)

    def delete_dataset(self, key):
        """Markiert ein Dataset zum Löschen beim nächsten sync."""
        self._datasets_to_delete.add(key)
        self._datasets_keys.discard(key)
        if hasattr(self, key):
            delattr(self, key)

    def sync(self):
        if not self._writable:
            raise RuntimeError("Objekt ist nicht schreibbar.")

        # Erst löschen
        for key in self._attrs_to_delete:
            if key in self._node.attrs:
                del self._node.attrs[key]
        self._attrs_to_delete.clear()

        for key in self._datasets_to_delete:
            if key in self._node:
                del self._node[key]
        self._datasets_to_delete.clear()

        # Attribute speichern
        for key in self._attrs_keys:
            value = getattr(self, key)
            if key in self._node.attrs:
                del self._node.attrs[key]
            self._node.attrs[key] = value

        # Datasets speichern
        for key in self._datasets_keys:
            value = getattr(self, key)

            if key in self._node:
                del self._node[key]
            self._node.create_dataset(key, data=value)

        # Rekursiv Untergruppen syncen
        for key, value in self.__dict__.items():
            if isinstance(value, H5Object):
                value.sync()

                # Datei flushen, falls aktiviert
        if self._auto_flush:
            self._node.file.flush()



def load_h5(filename, mode="r"):
    """
    Lädt ein HDF5-File als H5Object.
    mode: "r" readonly, "a" read/write
    """
    f = h5py.File(filename, mode)
    return H5Object(f, writable=(mode != "r")), f
