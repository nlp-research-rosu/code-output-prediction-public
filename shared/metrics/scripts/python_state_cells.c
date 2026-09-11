#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <limits.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    PyObject **items;
    size_t capacity;
    size_t size;
} ObjectBuffer;

typedef struct {
    PyObject **items;
    size_t capacity;
    size_t size;
} SeenSet;

static PyObject *deque_type = NULL;

#define FLAT_CACHE_MIN_ITEMS 256

typedef enum {
    FLAT_CACHE_NONE = 0,
    FLAT_CACHE_LIST = 1,
    FLAT_CACHE_TUPLE = 2,
    FLAT_CACHE_DICT = 3,
} FlatCacheKind;

typedef struct {
    PyObject *identity;
    FlatCacheKind kind;
    Py_ssize_t length;
    PyObject **items;
    size_t item_capacity;
    int valid;
    int watched;
} FlatCacheEntry;

static FlatCacheEntry *flat_cache = NULL;
static size_t flat_cache_capacity = 0;
static size_t flat_cache_size = 0;
static int dict_watcher_id = -1;
static unsigned long long dict_mutation_generation = 0;
static unsigned long long dict_last_inexact_generation = 0;
static long long dict_scalar_cell_delta = 0;

static size_t pointer_hash(PyObject *value) {
    uintptr_t bits = ((uintptr_t)value) >> 4;
    bits ^= bits >> 23;
    bits *= (uintptr_t)0x2127599bf4325c37ULL;
    bits ^= bits >> 47;
    return (size_t)bits;
}

static int flat_cache_resize(size_t capacity) {
    FlatCacheEntry *replacement = calloc(capacity, sizeof(FlatCacheEntry));
    if (replacement == NULL) {
        PyErr_NoMemory();
        return -1;
    }
    for (size_t index = 0; index < flat_cache_capacity; index++) {
        FlatCacheEntry entry = flat_cache[index];
        if (entry.identity == NULL) {
            continue;
        }
        size_t slot = pointer_hash(entry.identity) & (capacity - 1);
        while (replacement[slot].identity != NULL) {
            slot = (slot + 1) & (capacity - 1);
        }
        replacement[slot] = entry;
    }
    free(flat_cache);
    flat_cache = replacement;
    flat_cache_capacity = capacity;
    return 0;
}

static FlatCacheEntry *flat_cache_find(PyObject *identity) {
    if (flat_cache_capacity == 0) {
        return NULL;
    }
    size_t slot = pointer_hash(identity) & (flat_cache_capacity - 1);
    while (flat_cache[slot].identity != NULL) {
        if (flat_cache[slot].identity == identity) {
            return &flat_cache[slot];
        }
        slot = (slot + 1) & (flat_cache_capacity - 1);
    }
    return NULL;
}

static FlatCacheEntry *flat_cache_get(PyObject *identity, FlatCacheKind kind) {
    if (flat_cache_capacity == 0) {
        if (flat_cache_resize(1024) < 0) {
            return NULL;
        }
    } else if ((flat_cache_size + 1) * 10 >= flat_cache_capacity * 7) {
        if (flat_cache_resize(flat_cache_capacity * 2) < 0) {
            return NULL;
        }
    }
    size_t slot = pointer_hash(identity) & (flat_cache_capacity - 1);
    while (flat_cache[slot].identity != NULL) {
        if (flat_cache[slot].identity == identity) {
            FlatCacheEntry *entry = &flat_cache[slot];
            if (entry->kind != kind) {
                free(entry->items);
                entry->items = NULL;
                entry->item_capacity = 0;
                entry->kind = kind;
                entry->length = 0;
                entry->valid = 0;
                entry->watched = 0;
            }
            return entry;
        }
        slot = (slot + 1) & (flat_cache_capacity - 1);
    }
    flat_cache[slot].identity = identity;
    flat_cache[slot].kind = kind;
    flat_cache_size++;
    return &flat_cache[slot];
}

static int add_work_bulk(
    unsigned long long *work,
    unsigned long long amount,
    unsigned long long limit
) {
    if (*work > limit || amount > limit - *work) {
        *work = limit == ULLONG_MAX ? ULLONG_MAX : limit + 1;
        return 2;
    }
    *work += amount;
    return 0;
}

static int seen_resize(SeenSet *seen, size_t capacity) {
    PyObject **replacement = calloc(capacity, sizeof(PyObject *));
    if (replacement == NULL) {
        PyErr_NoMemory();
        return -1;
    }
    for (size_t index = 0; index < seen->capacity; index++) {
        PyObject *value = seen->items[index];
        if (value == NULL) {
            continue;
        }
        size_t slot = pointer_hash(value) & (capacity - 1);
        while (replacement[slot] != NULL) {
            slot = (slot + 1) & (capacity - 1);
        }
        replacement[slot] = value;
    }
    free(seen->items);
    seen->items = replacement;
    seen->capacity = capacity;
    return 0;
}

static int seen_add(SeenSet *seen, PyObject *value) {
    if (seen->capacity == 0) {
        if (seen_resize(seen, 1024) < 0) {
            return -1;
        }
    } else if ((seen->size + 1) * 10 >= seen->capacity * 7) {
        if (seen_resize(seen, seen->capacity * 2) < 0) {
            return -1;
        }
    }
    size_t slot = pointer_hash(value) & (seen->capacity - 1);
    while (seen->items[slot] != NULL) {
        if (seen->items[slot] == value) {
            return 0;
        }
        slot = (slot + 1) & (seen->capacity - 1);
    }
    seen->items[slot] = value;
    seen->size++;
    return 1;
}

static int buffer_push(ObjectBuffer *buffer, PyObject *value) {
    if (buffer->size == buffer->capacity) {
        size_t capacity = buffer->capacity == 0 ? 1024 : buffer->capacity * 2;
        PyObject **replacement = realloc(buffer->items, capacity * sizeof(PyObject *));
        if (replacement == NULL) {
            PyErr_NoMemory();
            return -1;
        }
        buffer->items = replacement;
        buffer->capacity = capacity;
    }
    Py_INCREF(value);
    buffer->items[buffer->size++] = value;
    return 0;
}

static void buffer_clear(ObjectBuffer *buffer) {
    while (buffer->size > 0) {
        Py_DECREF(buffer->items[--buffer->size]);
    }
    free(buffer->items);
}

static int push_iterable(ObjectBuffer *pending, PyObject *value) {
    PyObject *iterator = PyObject_GetIter(value);
    if (iterator == NULL) {
        return -1;
    }
    PyObject *item;
    while ((item = PyIter_Next(iterator)) != NULL) {
        int status = buffer_push(pending, item);
        Py_DECREF(item);
        if (status < 0) {
            Py_DECREF(iterator);
            return -1;
        }
    }
    Py_DECREF(iterator);
    return PyErr_Occurred() ? -1 : 0;
}

static int is_excluded_value(PyObject *value) {
    return PyModule_Check(value) || PyFunction_Check(value) ||
           PyCFunction_Check(value) || PyMethod_Check(value) || PyType_Check(value);
}

static int is_scalar_value(PyObject *value) {
    return value == Py_None || Py_IS_TYPE(value, &PyBool_Type) ||
           PyLong_CheckExact(value) || PyFloat_CheckExact(value) ||
           PyComplex_CheckExact(value);
}

static int add_total_bulk(
    unsigned long long *total,
    unsigned long long amount
) {
    if (amount > ULLONG_MAX - *total) {
        PyErr_SetString(PyExc_OverflowError, "state size overflow");
        return -1;
    }
    *total += amount;
    return 0;
}

static int flat_dict_watcher(
    PyDict_WatchEvent event,
    PyObject *dict,
    PyObject *key,
    PyObject *new_value
) {
    FlatCacheEntry *entry = flat_cache_find(dict);
    if (entry == NULL || entry->kind != FLAT_CACHE_DICT || !entry->watched) {
        return 0;
    }
    dict_mutation_generation++;
    if (!entry->valid) {
        dict_last_inexact_generation = dict_mutation_generation;
        return 0;
    }
    switch (event) {
        case PyDict_EVENT_ADDED:
            if (!is_scalar_value(key) || !is_scalar_value(new_value)) {
                entry->valid = 0;
                dict_last_inexact_generation = dict_mutation_generation;
            } else {
                entry->length++;
                dict_scalar_cell_delta += 2;
            }
            break;
        case PyDict_EVENT_MODIFIED:
            if (!is_scalar_value(new_value)) {
                entry->valid = 0;
                dict_last_inexact_generation = dict_mutation_generation;
            }
            break;
        case PyDict_EVENT_DELETED:
            if (entry->length > 0) {
                entry->length--;
                dict_scalar_cell_delta -= 2;
            } else {
                entry->valid = 0;
                dict_last_inexact_generation = dict_mutation_generation;
            }
            break;
        case PyDict_EVENT_CLEARED:
            dict_scalar_cell_delta -= 2 * (long long)entry->length;
            entry->length = 0;
            break;
        case PyDict_EVENT_CLONED:
            entry->valid = 0;
            dict_last_inexact_generation = dict_mutation_generation;
            break;
        case PyDict_EVENT_DEALLOCATED:
            entry->valid = 0;
            entry->watched = 0;
            dict_last_inexact_generation = dict_mutation_generation;
            break;
    }
    return 0;
}

static int cache_flat_sequence(
    PyObject *value,
    FlatCacheKind kind,
    unsigned long long *work,
    unsigned long long limit,
    unsigned long long *total
) {
    Py_ssize_t length = kind == FLAT_CACHE_LIST
        ? PyList_GET_SIZE(value)
        : PyTuple_GET_SIZE(value);
    FlatCacheEntry *entry = flat_cache_find(value);
    if (entry != NULL && entry->kind == kind && entry->valid &&
        entry->length == length) {
        int unchanged = 1;
        for (Py_ssize_t index = 0; index < length; index++) {
            PyObject *item = kind == FLAT_CACHE_LIST
                ? PyList_GET_ITEM(value, index)
                : PyTuple_GET_ITEM(value, index);
            if (entry->items[index] == item) {
                continue;
            }
            unchanged = 0;
            if (!is_scalar_value(item)) {
                entry->valid = 0;
                return 0;
            }
            entry->items[index] = item;
        }
        (void)unchanged;
        int work_status = add_work_bulk(
            work, (unsigned long long)length, limit
        );
        if (work_status != 0) {
            return work_status;
        }
        if (add_total_bulk(total, 1 + (unsigned long long)length) < 0) {
            return -1;
        }
        return 1;
    }
    if (length < FLAT_CACHE_MIN_ITEMS &&
        (entry == NULL || !entry->valid)) {
        return 0;
    }
    for (Py_ssize_t index = 0; index < length; index++) {
        PyObject *item = kind == FLAT_CACHE_LIST
            ? PyList_GET_ITEM(value, index)
            : PyTuple_GET_ITEM(value, index);
        if (!is_scalar_value(item)) {
            if (entry != NULL) {
                entry->valid = 0;
            }
            return 0;
        }
    }
    entry = flat_cache_get(value, kind);
    if (entry == NULL) {
        return -1;
    }
    if ((size_t)length > entry->item_capacity) {
        PyObject **replacement = realloc(
            entry->items, (size_t)length * sizeof(PyObject *)
        );
        if (replacement == NULL && length != 0) {
            PyErr_NoMemory();
            return -1;
        }
        entry->items = replacement;
        entry->item_capacity = (size_t)length;
    }
    for (Py_ssize_t index = 0; index < length; index++) {
        entry->items[index] = kind == FLAT_CACHE_LIST
            ? PyList_GET_ITEM(value, index)
            : PyTuple_GET_ITEM(value, index);
    }
    entry->length = length;
    entry->valid = 1;
    int work_status = add_work_bulk(work, (unsigned long long)length, limit);
    if (work_status != 0) {
        return work_status;
    }
    if (add_total_bulk(total, 1 + (unsigned long long)length) < 0) {
        return -1;
    }
    return 1;
}

static int cache_flat_dict(
    PyObject *value,
    unsigned long long *work,
    unsigned long long limit,
    unsigned long long *total
) {
    Py_ssize_t length = PyDict_GET_SIZE(value);
    FlatCacheEntry *entry = flat_cache_find(value);
    if (entry != NULL && entry->kind == FLAT_CACHE_DICT && entry->valid &&
        entry->watched && entry->length == length) {
        int work_status = add_work_bulk(
            work, 2 * (unsigned long long)length, limit
        );
        if (work_status != 0) {
            return work_status;
        }
        if (add_total_bulk(total, 1 + 2 * (unsigned long long)length) < 0) {
            return -1;
        }
        return 1;
    }
    if (length == 0 &&
        (entry == NULL || !entry->valid)) {
        return 0;
    }
    Py_ssize_t position = 0;
    PyObject *key;
    PyObject *item;
    while (PyDict_Next(value, &position, &key, &item)) {
        if (!is_scalar_value(key) || !is_scalar_value(item)) {
            if (entry != NULL) {
                entry->valid = 0;
            }
            return 0;
        }
    }
    entry = flat_cache_get(value, FLAT_CACHE_DICT);
    if (entry == NULL) {
        return -1;
    }
    entry->length = length;
    entry->valid = 1;
    if (!entry->watched) {
        if (dict_watcher_id < 0 || PyDict_Watch(dict_watcher_id, value) < 0) {
            entry->valid = 0;
            return -1;
        }
        entry->watched = 1;
    }
    int work_status = add_work_bulk(
        work, 2 * (unsigned long long)length, limit
    );
    if (work_status != 0) {
        return work_status;
    }
    if (add_total_bulk(total, 1 + 2 * (unsigned long long)length) < 0) {
        return -1;
    }
    return 1;
}

/* Count the common leaf cases without pushing and popping a stack entry. */
static int process_child(
    ObjectBuffer *pending,
    PyObject *value,
    unsigned long long *work,
    unsigned long long limit,
    unsigned long long *total
) {
    if (is_excluded_value(value) || is_scalar_value(value)) {
        (*work)++;
        if (*work > limit) {
            return 2;
        }
        if (is_scalar_value(value)) {
            (*total)++;
        }
        return 0;
    }
    return buffer_push(pending, value) < 0 ? -1 : 0;
}

static int type_module_is_main(PyObject *value) {
    PyObject *module = PyObject_GetAttrString((PyObject *)Py_TYPE(value), "__module__");
    if (module == NULL) {
        return -1;
    }
    int result = PyUnicode_Check(module) && PyUnicode_CompareWithASCIIString(module, "__main__") == 0;
    Py_DECREF(module);
    return result;
}

/*
 * Return (status, state_size, updated_work):
 *   status 0: exact C result
 *   status 1: retry this observation with the Python reference walker
 *   status 2: the pinned traversal-work limit was exceeded
 */
static PyObject *state_cells_count(PyObject *self, PyObject *args) {
    (void)self;
    PyObject *roots;
    unsigned long long work;
    unsigned long long limit;
    if (!PyArg_ParseTuple(args, "OKK:count", &roots, &work, &limit)) {
        return NULL;
    }
    PyObject *sequence = PySequence_Fast(roots, "roots must be a sequence");
    if (sequence == NULL) {
        return NULL;
    }

    ObjectBuffer pending = {0};
    SeenSet seen = {0};
    unsigned long long total = 0;
    int status = 0;
    Py_ssize_t root_count = PySequence_Fast_GET_SIZE(sequence);
    PyObject **root_items = PySequence_Fast_ITEMS(sequence);
    for (Py_ssize_t index = root_count; index > 0; index--) {
        if (buffer_push(&pending, root_items[index - 1]) < 0) {
            status = -1;
            break;
        }
    }

    while (status == 0 && pending.size > 0) {
        PyObject *value = pending.items[--pending.size];
        work++;
        if (work > limit) {
            Py_DECREF(value);
            status = 2;
            break;
        }

        if (is_excluded_value(value)) {
            Py_DECREF(value);
            continue;
        }
        if (is_scalar_value(value)) {
            total++;
            Py_DECREF(value);
            continue;
        }

        int added = seen_add(&seen, value);
        if (added < 0) {
            Py_DECREF(value);
            status = -1;
            break;
        }
        if (added == 0) {
            Py_DECREF(value);
            continue;
        }

        if (PyUnicode_Check(value) || PyBytes_Check(value) ||
            PyByteArray_Check(value) || Py_IS_TYPE(value, &PyRange_Type)) {
            Py_ssize_t length = PyObject_Length(value);
            if (length < 0) {
                Py_DECREF(value);
                status = -1;
                break;
            }
            if (total == ULLONG_MAX ||
                (unsigned long long)length > ULLONG_MAX - total - 1) {
                Py_DECREF(value);
                PyErr_SetString(PyExc_OverflowError, "state size overflow");
                status = -1;
                break;
            }
            total += 1 + (unsigned long long)length;
            Py_DECREF(value);
            continue;
        }

        if (PyIter_Check(value)) {
            total++;
            Py_DECREF(value);
            continue;
        }

        int cache_status = 0;
        if (PyList_CheckExact(value)) {
            cache_status = cache_flat_sequence(
                value, FLAT_CACHE_LIST, &work, limit, &total
            );
        } else if (PyTuple_CheckExact(value)) {
            cache_status = cache_flat_sequence(
                value, FLAT_CACHE_TUPLE, &work, limit, &total
            );
        } else if (PyDict_Check(value)) {
            cache_status = cache_flat_dict(value, &work, limit, &total);
        }
        if (cache_status != 0) {
            Py_DECREF(value);
            if (cache_status == 1) {
                continue;
            }
            status = cache_status;
            break;
        }

        total++;
        if (PyDict_Check(value)) {
            Py_ssize_t position = 0;
            PyObject *key;
            PyObject *item;
            while (PyDict_Next(value, &position, &key, &item)) {
                int item_status = process_child(
                    &pending, item, &work, limit, &total
                );
                int key_status = item_status == 0 ? process_child(
                    &pending, key, &work, limit, &total
                ) : item_status;
                if (item_status != 0 || key_status != 0) {
                    status = item_status != 0 ? item_status : key_status;
                    break;
                }
            }
        } else if (PyList_Check(value)) {
            Py_ssize_t length = PyList_GET_SIZE(value);
            for (Py_ssize_t index = length; index > 0; index--) {
                int child_status = process_child(
                    &pending,
                    PyList_GET_ITEM(value, index - 1),
                    &work,
                    limit,
                    &total
                );
                if (child_status != 0) {
                    status = child_status;
                    break;
                }
            }
        } else if (PyTuple_Check(value)) {
            Py_ssize_t length = PyTuple_GET_SIZE(value);
            for (Py_ssize_t index = length; index > 0; index--) {
                int child_status = process_child(
                    &pending,
                    PyTuple_GET_ITEM(value, index - 1),
                    &work,
                    limit,
                    &total
                );
                if (child_status != 0) {
                    status = child_status;
                    break;
                }
            }
        } else if (PyAnySet_Check(value)) {
            if (push_iterable(&pending, value) < 0) {
                status = -1;
            }
        } else {
            int is_deque = deque_type == NULL ? 0 : PyObject_IsInstance(value, deque_type);
            if (is_deque < 0) {
                status = -1;
            } else if (is_deque) {
                if (push_iterable(&pending, value) < 0) {
                    status = -1;
                }
            } else {
                int is_main = type_module_is_main(value);
                if (is_main < 0) {
                    status = -1;
                } else if (!is_main) {
                    /* Imported-library objects are one opaque reachable cell. */
                } else {
                    PyObject *attributes = PyObject_GenericGetDict(value, NULL);
                    if (attributes == NULL) {
                        if (PyErr_ExceptionMatches(PyExc_AttributeError)) {
                            PyErr_Clear();
                            status = 1;
                        } else {
                            status = -1;
                        }
                    } else if (!PyDict_Check(attributes)) {
                        Py_DECREF(attributes);
                        status = 1;
                    } else {
                        Py_ssize_t position = 0;
                        PyObject *name;
                        PyObject *item;
                        while (PyDict_Next(attributes, &position, &name, &item)) {
                            int child_status = process_child(
                                &pending, item, &work, limit, &total
                            );
                            if (child_status != 0) {
                                status = child_status;
                                break;
                            }
                        }
                        Py_DECREF(attributes);
                    }
                }
            }
        }
        Py_DECREF(value);
    }

    buffer_clear(&pending);
    free(seen.items);
    Py_DECREF(sequence);
    if (status < 0) {
        return NULL;
    }
    if (status == 1) {
        work = 0;
        total = 0;
    }
    return Py_BuildValue("(iKK)", status, total, work);
}

static PyObject *dict_mutation_state(PyObject *self, PyObject *args) {
    (void)self;
    if (!PyArg_ParseTuple(args, ":dict_mutation_state")) {
        return NULL;
    }
    return Py_BuildValue(
        "(KKL)",
        dict_mutation_generation,
        dict_last_inexact_generation,
        dict_scalar_cell_delta
    );
}

static PyMethodDef state_cells_methods[] = {
    {"count", (PyCFunction)state_cells_count, METH_VARARGS,
     "Count exact reachable state cells without recursive Python calls."},
    {"dict_mutation_state", (PyCFunction)dict_mutation_state, METH_VARARGS,
     "Return watched-dictionary mutation generation, inexact generation, and scalar-cell delta."},
    {NULL, NULL, 0, NULL},
};

static void state_cells_free(void *module) {
    (void)module;
    if (dict_watcher_id >= 0) {
        for (size_t index = 0; index < flat_cache_capacity; index++) {
            FlatCacheEntry *entry = &flat_cache[index];
            if (entry->identity != NULL && entry->kind == FLAT_CACHE_DICT &&
                entry->watched) {
                if (PyDict_Unwatch(dict_watcher_id, entry->identity) < 0) {
                    PyErr_Clear();
                }
            }
        }
        if (PyDict_ClearWatcher(dict_watcher_id) < 0) {
            PyErr_Clear();
        }
        dict_watcher_id = -1;
    }
    for (size_t index = 0; index < flat_cache_capacity; index++) {
        free(flat_cache[index].items);
    }
    free(flat_cache);
    flat_cache = NULL;
    flat_cache_capacity = 0;
    flat_cache_size = 0;
    dict_mutation_generation = 0;
    dict_last_inexact_generation = 0;
    dict_scalar_cell_delta = 0;
    Py_CLEAR(deque_type);
}

static struct PyModuleDef state_cells_module = {
    PyModuleDef_HEAD_INIT,
    "_program_state_cells",
    NULL,
    -1,
    state_cells_methods,
    NULL,
    NULL,
    NULL,
    state_cells_free,
};

PyMODINIT_FUNC PyInit__program_state_cells(void) {
    PyObject *collections = PyImport_ImportModule("collections");
    if (collections == NULL) {
        return NULL;
    }
    deque_type = PyObject_GetAttrString(collections, "deque");
    Py_DECREF(collections);
    if (deque_type == NULL) {
        return NULL;
    }
    dict_watcher_id = PyDict_AddWatcher(flat_dict_watcher);
    if (dict_watcher_id < 0) {
        Py_CLEAR(deque_type);
        return NULL;
    }
    PyObject *module = PyModule_Create(&state_cells_module);
    if (module == NULL) {
        PyDict_ClearWatcher(dict_watcher_id);
        dict_watcher_id = -1;
        Py_CLEAR(deque_type);
    }
    return module;
}
