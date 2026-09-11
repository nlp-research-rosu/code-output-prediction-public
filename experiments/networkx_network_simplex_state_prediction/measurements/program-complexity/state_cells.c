#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <stdlib.h>

typedef struct {
    PyObject **items;
    size_t capacity;
    size_t size;
} SeenSet;

static PyObject *deque_type = NULL;

static size_t pointer_hash(PyObject *value) {
    uintptr_t bits = ((uintptr_t)value) >> 4;
    bits ^= bits >> 23;
    bits *= (uintptr_t)0x2127599bf4325c37ULL;
    bits ^= bits >> 47;
    return (size_t)bits;
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

static int count_value(PyObject *value, SeenSet *seen, Py_ssize_t *total);

static int count_iterable(PyObject *value, SeenSet *seen, Py_ssize_t *total) {
    PyObject *iterator = PyObject_GetIter(value);
    if (iterator == NULL) {
        return -1;
    }
    PyObject *item;
    while ((item = PyIter_Next(iterator)) != NULL) {
        int status = count_value(item, seen, total);
        Py_DECREF(item);
        if (status < 0) {
            Py_DECREF(iterator);
            return -1;
        }
    }
    Py_DECREF(iterator);
    return PyErr_Occurred() ? -1 : 0;
}

static int is_dunder_name(PyObject *name) {
    if (!PyUnicode_Check(name) || PyUnicode_GET_LENGTH(name) < 2) {
        return 0;
    }
    return PyUnicode_READ_CHAR(name, 0) == '_' &&
           PyUnicode_READ_CHAR(name, 1) == '_';
}

static int count_value(PyObject *value, SeenSet *seen, Py_ssize_t *total) {
    if (PyModule_Check(value) || PyFunction_Check(value) ||
        PyCFunction_Check(value) || PyMethod_Check(value) || PyType_Check(value)) {
        return 0;
    }
    if (value == Py_None || PyBool_Check(value) || PyLong_Check(value) ||
        PyFloat_Check(value) || PyComplex_Check(value)) {
        (*total)++;
        return 0;
    }
    if (PyUnicode_Check(value) || PyBytes_Check(value) ||
        PyByteArray_Check(value) || PyMemoryView_Check(value)) {
        Py_ssize_t length = PyObject_Length(value);
        if (length < 0) {
            return -1;
        }
        *total += 1 + length;
        return 0;
    }
    if (Py_IS_TYPE(value, &PyRange_Type)) {
        (*total)++;
        return 0;
    }

    int added = seen_add(seen, value);
    if (added <= 0) {
        return added;
    }
    if (Py_EnterRecursiveCall(" while measuring reachable state")) {
        return -1;
    }

    int status = 0;
    (*total)++;
    if (PyDict_Check(value)) {
        Py_ssize_t position = 0;
        PyObject *key;
        PyObject *item;
        while (PyDict_Next(value, &position, &key, &item)) {
            if (count_value(key, seen, total) < 0 ||
                count_value(item, seen, total) < 0) {
                status = -1;
                break;
            }
        }
    } else if (PyList_Check(value)) {
        Py_ssize_t length = PyList_GET_SIZE(value);
        for (Py_ssize_t index = 0; index < length; index++) {
            if (count_value(PyList_GET_ITEM(value, index), seen, total) < 0) {
                status = -1;
                break;
            }
        }
    } else if (PyTuple_Check(value)) {
        Py_ssize_t length = PyTuple_GET_SIZE(value);
        for (Py_ssize_t index = 0; index < length; index++) {
            if (count_value(PyTuple_GET_ITEM(value, index), seen, total) < 0) {
                status = -1;
                break;
            }
        }
    } else if (PyAnySet_Check(value)) {
        status = count_iterable(value, seen, total);
    } else {
        int is_deque = deque_type == NULL ? 0 : PyObject_IsInstance(value, deque_type);
        if (is_deque < 0) {
            status = -1;
        } else if (is_deque) {
            status = count_iterable(value, seen, total);
        } else {
            PyObject *attributes = PyObject_GenericGetDict(value, NULL);
            if (attributes == NULL) {
                if (PyErr_ExceptionMatches(PyExc_AttributeError)) {
                    PyErr_Clear();
                } else {
                    status = -1;
                }
            } else if (PyDict_Check(attributes)) {
                Py_ssize_t position = 0;
                PyObject *name;
                PyObject *item;
                while (PyDict_Next(attributes, &position, &name, &item)) {
                    if (!is_dunder_name(name) &&
                        count_value(item, seen, total) < 0) {
                        status = -1;
                        break;
                    }
                }
                Py_DECREF(attributes);
            } else {
                Py_DECREF(attributes);
            }
        }
    }
    Py_LeaveRecursiveCall();
    return status;
}

static PyObject *state_cells_count(PyObject *self, PyObject *roots) {
    (void)self;
    PyObject *sequence = PySequence_Fast(roots, "roots must be a sequence");
    if (sequence == NULL) {
        return NULL;
    }
    SeenSet seen = {0};
    Py_ssize_t total = 0;
    Py_ssize_t length = PySequence_Fast_GET_SIZE(sequence);
    PyObject **items = PySequence_Fast_ITEMS(sequence);
    for (Py_ssize_t index = 0; index < length; index++) {
        if (count_value(items[index], &seen, &total) < 0) {
            free(seen.items);
            Py_DECREF(sequence);
            return NULL;
        }
    }
    free(seen.items);
    Py_DECREF(sequence);
    return PyLong_FromSsize_t(total);
}

static PyMethodDef state_cells_methods[] = {
    {"count", (PyCFunction)state_cells_count, METH_O,
     "Count reachable runtime value cells under the benchmark convention."},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef state_cells_module = {
    PyModuleDef_HEAD_INIT,
    "_networkx_state_cells",
    NULL,
    -1,
    state_cells_methods,
};

PyMODINIT_FUNC PyInit__networkx_state_cells(void) {
    PyObject *collections = PyImport_ImportModule("collections");
    if (collections == NULL) {
        return NULL;
    }
    deque_type = PyObject_GetAttrString(collections, "deque");
    Py_DECREF(collections);
    if (deque_type == NULL) {
        return NULL;
    }
    return PyModule_Create(&state_cells_module);
}
