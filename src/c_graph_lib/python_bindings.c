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

///////////////////////////////////
/// General Graph Code
///////////////////////////////////

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

///////////////////////////////////
/// Upset Generator Code
///////////////////////////////////

typedef struct
{
    PyObject_HEAD UTGArena *arena;
} PyUpsetGenerator;

/*
 * Builds the next tournament graph by incrementing the graph
 * the underlying UTGArena and returns the number of upsets in the new graph
 */
static PyObject *
PyUpsetGeneratorNext (PyUpsetGenerator *self)
{
    UTGArena *arena  = self->arena;
    u128 upper_bound = (u128)1 << edgesOrder (arena->tg.order);
    if (arena->tg.graph >= upper_bound)
        {
            PyErr_SetNone (PyExc_StopIteration);
            return nullptr;
        }
    arena->tg.graph++;
    memset (arena->wins, 0, arena->tg.order);
    winVectorReplace (&arena->tg, arena->wins);
    u8 upsets = countUpsetsWithWinVec (&arena->tg, arena->wins);
    return PyLong_FromLong ((long)upsets);
}

/*
 * Needed because the arena is heap allocated
 */
static void
PyUpsetGeneratorDealloc (PyUpsetGenerator *self)
{
    free (self->arena);
    Py_TYPE (self)->tp_free ((PyObject *)self);
}

static PyObject *
PyUpsetGeneratorNew (PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyUpsetGenerator *self = (PyUpsetGenerator *)type->tp_alloc (type, 1);
    static char *kwlist[]  = { "order", "graph", nullptr };
    u32 order              = 0;
    PyObject *graph_obj    = nullptr;
    if (!PyArg_ParseTupleAndKeywords (args, kwds, "IO", kwlist, &order,
                                      &graph_obj))
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
    u128 initial_graph = 0;
    Py_ssize_t n_bytes = PyLong_AsNativeBytes (
        graph_obj, &initial_graph, sizeof (initial_graph),
        Py_ASNATIVEBYTES_LITTLE_ENDIAN | Py_ASNATIVEBYTES_UNSIGNED_BUFFER
            | Py_ASNATIVEBYTES_REJECT_NEGATIVE);
    if (n_bytes < 0)
        {
            Py_DECREF (self);
            return nullptr;
        }
    if (n_bytes > (Py_ssize_t)sizeof (initial_graph))
        {
            PyErr_SetString (PyExc_OverflowError,
                             "Graph initial value does not fit in 128 bits");
            Py_DECREF (self);
            return nullptr;
        }
    self->arena = makeUTGArena ((u8)order);
    if (self->arena == nullptr)
        {
            PyErr_SetString (PyExc_MemoryError, "Failed to allocate UTGArena");
            Py_DECREF (self);
            return nullptr;
        }
    self->arena->tg.graph = initial_graph;
    self->arena->tg.order = (u8)order;
    return (PyObject *)self;
}

static PyObject *
PyCurrentGraph (PyUpsetGenerator *self)
{
    PyUnamedTG *TG_out
        = (PyUnamedTG *)PyTournomentType.tp_alloc (&PyTournomentType, 1);
    TG_out->TG.graph = self->arena->tg.graph;
    TG_out->TG.order = self->arena->tg.order;
    return (PyObject *)TG_out;
}

static PyMethodDef PyUpsetGeneratorMethods[] = {
    { "current_graph", (PyCFunction)PyCurrentGraph, METH_NOARGS,
      "Returns the current tournoment graph of the generator" },
    { nullptr },
};

static PyTypeObject PyUpsetGeneratorType = {
    PyVarObject_HEAD_INIT (nullptr, 0).tp_name = "tourny.upset_generator",
    .tp_doc       = "Generator yielding the number of upsets for each "
                    "successive tournament graph of a given order",
    .tp_basicsize = sizeof (PyUpsetGenerator),
    .tp_itemsize  = 0,
    .tp_methods   = PyUpsetGeneratorMethods,
    .tp_flags     = Py_TPFLAGS_DEFAULT,
    .tp_new       = PyUpsetGeneratorNew,
    .tp_dealloc   = (destructor)PyUpsetGeneratorDealloc,
    .tp_iter      = PyObject_SelfIter,
    .tp_iternext  = (iternextfunc)PyUpsetGeneratorNext,
};

///////////////////////////////////
/// Module Initialization Code
///////////////////////////////////
static PyMethodDef TournyMethods[] = { { nullptr, nullptr, 0, nullptr } };

static struct PyModuleDef TournyModule
    = { .m_base    = PyModuleDef_HEAD_INIT,
        .m_name    = "tourny",
        .m_doc     = "A module for tournoment graphs.",
        .m_size    = -1,
        .m_methods = TournyMethods };

PyMODINIT_FUNC
PyInit_tourny (void)
{
    PyObject *mod_out = nullptr;
    if (PyType_Ready (&PyTournomentType))
        {
            fprintf (stderr, "Failed to initialize Tournoment type\n");
            return nullptr;
        }
    if (PyType_Ready (&PyUpsetGeneratorType))
        {
            fprintf (stderr, "Failed to initialize Upset generator type\n");
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
    if (PyModule_AddObject (mod_out, "upset_generator",
                            (PyObject *)&PyUpsetGeneratorType)
        < 0)
        {
            Py_DECREF (mod_out);
            return nullptr;
        }
    return mod_out;
}
