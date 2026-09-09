#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "./include/types.h"
#include "exports.h"
#include "methodobject.h"
#include "modsupport.h"
#include "object.h"
#include "pyerrors.h"
#include "pytypedefs.h"
#include <stdio.h>

// DO NOT CHANGE INCLUDES ORDER THIS MUST ALWAYS BE AT THE BOTTOM BECAUSE THIS
// PROJECT IS A UNITY BUILD
#include "./include/functions.c"

typedef struct
{
    PyObject_HEAD UnnamedTG TG;
} PyUnamedTG;

/*
 * Returns the pair representations of the edges as a list
 */
static PyObject *
PyTGToTupples (PyUnamedTG *self)
{
    u64 order          = self->TG.order;
    PyObject *list_out = PyList_New ((Py_ssize_t)(order * (order - 1) / 2));

    for (u8 a = 1; a < order; a++)
        {
            for (u8 b = 0; b < a; b++)
                {
                    bool a_wins             = unsafeReadByte (a, b, &self->TG);
                    PyObject *current_tuple = PyTuple_New (2);
                    PyList_SetItem (list_out, a * (a - 1) / 2 + b,
                                    current_tuple);
                    if (a_wins)
                        {
                            PyTuple_SetItem (current_tuple, 0,
                                             PyLong_FromLong ((long)a));
                            PyTuple_SetItem (current_tuple, 1,
                                             PyLong_FromLong ((long)b));
                        }
                    else
                        {
                            PyTuple_SetItem (current_tuple, 0,
                                             PyLong_FromLong ((long)b));
                            PyTuple_SetItem (current_tuple, 1,
                                             PyLong_FromLong ((long)a));
                        }
                }
        }
    return list_out;
}

static PyObject *
PyUTGNext (PyUnamedTG *self)
{
    self->TG.graph++;
    return Py_NewRef (self);
}

static PyMethodDef PyTournomentMethods[]
    = { { "to_tuple", (PyCFunction)PyTGToTupples, METH_NOARGS,
          "Returns the tournoment graph as a list of tuples of edges" },
        { "next", (PyCFunction)PyUTGNext, METH_NOARGS,
          "Iterates to the next tournoment graph" },
        { nullptr } };

static PyObject *
PyTournyNew (PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyUnamedTG *self      = (PyUnamedTG *)type->tp_alloc (type, 1);
    static char *kwlist[] = { "order", nullptr };
    u64 order             = 0;
    if (!PyArg_ParseTupleAndKeywords (args, kwds, "i", kwlist, &order))
        {
            Py_DECREF (self);
            return nullptr;
        }
    if (order > 16)
        {
            PyErr_SetString (PyExc_ValueError,
                             "Graphs can not be of order greater than 16");
            Py_DECREF (self);
            return nullptr;
        }
    self->TG.order = order;
    self->TG.graph = 0;
    return (PyObject *)self;
}

static PyTypeObject PyTournomentType = {
    PyVarObject_HEAD_INIT (nullptr, 0).tp_name = "tourny.unnamed_TG",
    .tp_doc       = "Representation of a tournoment graph",
    .tp_basicsize = sizeof (PyUnamedTG),
    .tp_itemsize  = 0,
    .tp_flags     = Py_TPFLAGS_DEFAULT,
    .tp_new       = PyTournyNew,
    .tp_methods   = PyTournomentMethods,
    .tp_repr      = nullptr,
    .tp_getset    = nullptr,
};
static PyMethodDef TournyMethods[] = { { nullptr, nullptr, 0, nullptr } };

static struct PyModuleDef TournyModule
    = { PyModuleDef_HEAD_INIT, "tourny", "A module for tournoment graphs.", -1,
        TournyMethods };

PyMODINIT_FUNC
PyInit_tourny (void)
{
    PyObject *mod_out = nullptr;
    if (PyType_Ready (&PyTournomentType))
        {
            fprintf (stderr, "Failed to initialize Tournoment type");
            return nullptr;
        }
    mod_out = PyModule_Create (&TournyModule);
    if (mod_out == nullptr)
        return nullptr;
    if (PyModule_AddObject (mod_out, "unnamed_TG",
                            (PyObject *)&PyTournomentType)
        < 0)
        {
            Py_DECREF (mod_out);
            return nullptr;
        }
    return mod_out;
}
