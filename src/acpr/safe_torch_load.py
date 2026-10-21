"""Read the tensors of a PyTorch checkpoint (zip format) as NumPy arrays without running any code from the file.

torch.load(weights_only=True) refuses the 2019 FCGF checkpoints because their training configuration is stored as an
easydict.EasyDict. This loader resolves only an explicit allow-list of names: tensor and parameter rebuilders (as
NumPy views of the stored bytes), OrderedDict, and EasyDict (as a plain dict). Anything else raises.
"""

from __future__ import annotations

import collections
import pickle
import zipfile

import numpy as np

_DTYPES = {"FloatStorage": np.float32, "DoubleStorage": np.float64, "HalfStorage": np.float16,
           "LongStorage": np.int64, "IntStorage": np.int32, "ShortStorage": np.int16, "CharStorage": np.int8,
           "ByteStorage": np.uint8, "BoolStorage": np.bool_}


class _StorageType:
    def __init__(self, name):
        self.dtype = _DTYPES[name]


def _rebuild_tensor(storage, offset, size, stride, *_):
    item = storage.itemsize
    return np.lib.stride_tricks.as_strided(storage[offset:], shape=tuple(size),
                                           strides=tuple(s * item for s in stride)).copy()


def _rebuild_parameter(data, *_):
    return data


class _EasyDict(dict):
    def __setstate__(self, state):  # EasyDict pickles its attributes as instance state; keep them as items
        if isinstance(state, dict):
            self.update(state)


_ALLOWED = {("torch._utils", "_rebuild_tensor_v2"): _rebuild_tensor,
            ("torch._utils", "_rebuild_parameter"): _rebuild_parameter,
            ("collections", "OrderedDict"): collections.OrderedDict,
            ("easydict", "EasyDict"): _EasyDict}


class _Restricted(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) in _ALLOWED:
            return _ALLOWED[(module, name)]
        if module == "torch" and name in _DTYPES:
            return _StorageType(name)
        raise pickle.UnpicklingError(f"refusing to load {module}.{name}")


def _load_legacy(path: str) -> dict:
    """Pre-1.6 format: magic, protocol, system info, the object pickle (storages as persistent ids), the list of
    storage keys, then every storage as an int64 element count followed by its raw bytes."""
    storages = {}

    class Unpickler(_Restricted):
        def persistent_load(self, pid):  # ('storage', storage_type, key, location, numel, view_metadata)
            _, stype, key, _, numel, view = pid
            if key not in storages:
                storages[key] = [stype.dtype, numel, None]
            if view is not None:
                raise pickle.UnpicklingError("storage views are not supported")
            return _Lazy(storages, key)

    with open(path, "rb") as f:
        for _ in range(3):
            _Restricted(f).load()
        obj = Unpickler(f).load()
        keys = _Restricted(f).load()
        for key in keys:
            dtype, numel, _ = storages[key]
            n = int(np.frombuffer(f.read(8), dtype="<i8")[0])
            assert n == numel, (key, n, numel)
            storages[key][2] = np.frombuffer(f.read(n * np.dtype(dtype).itemsize), dtype=dtype)
    return _resolve(obj)


class _Lazy:
    """A storage whose bytes follow the object pickle in the legacy format; tensors are rebuilt once read."""

    def __init__(self, storages, key):
        self.storages, self.key = storages, key


def _resolve(obj):
    if isinstance(obj, _LazyTensor):
        return _rebuild_tensor(obj.storage.storages[obj.storage.key][2], *obj.args)
    if isinstance(obj, dict):
        out = obj.__class__()
        for k, v in obj.items():
            out[k] = _resolve(v)
        return out
    if isinstance(obj, (list, tuple)):
        return type(obj)(_resolve(v) for v in obj)
    return obj


class _LazyTensor:
    def __init__(self, storage, args):
        self.storage, self.args = storage, args


def _rebuild_any(storage, *args):
    if isinstance(storage, _Lazy):
        return _LazyTensor(storage, args)
    return _rebuild_tensor(storage, *args)


_ALLOWED[("torch._utils", "_rebuild_tensor_v2")] = _rebuild_any


def load(path: str) -> dict:
    if not zipfile.is_zipfile(path):
        return _load_legacy(path)
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        root = names[0].split("/")[0]
        data = {n.split("/")[-1]: n for n in names if "/data/" in n}

        class Unpickler(pickle.Unpickler):
            def find_class(self, module, name):
                if (module, name) in _ALLOWED:
                    return _ALLOWED[(module, name)]
                if module == "torch" and name in _DTYPES:
                    return _StorageType(name)
                raise pickle.UnpicklingError(f"refusing to load {module}.{name}")

            def persistent_load(self, pid):  # ('storage', storage_type, key, location, numel)
                _, stype, key, _, _ = pid
                return np.frombuffer(z.read(data[str(key)]), dtype=stype.dtype)

        with z.open(f"{root}/data.pkl") as f:
            return Unpickler(f).load()
