#include "./functions.h"
#include "./types.h"

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/*
 * Returns number of edges on a TG of order n
 */
[[maybe_unused]] static u8
edgesOrder (u8 n)
{
    return n * (n - 1) / 2;
}

static void
u8Swap (u8 *a, u8 *b)
{
    u8 tmp = *a;
    *a     = *b;
    *b     = tmp;
}

static bool
unsafeReadByte (u8 a, u8 b, UnnamedTG *TG)
{
    u8 bit_index = a * (a - 1) / 2 + b;
    return (TG->graph >> bit_index)
           & (u128)1; // Typecast needed otherwise the bits after the 32nd are
                      // ignored
}

[[maybe_unused]] static bool
readByteSafe (u8 a, u8 b, UnnamedTG *TG)
{
    if (a == b)
        return false;
    if (a < b)
        u8Swap (&a, &b);
    if (TG->order <= a || TG->order <= b)
        {
            fprintf (stderr, "Verticies are too large for graph of order %u\n",
                     TG->order);
            return false;
        }

    return unsafeReadByte (a, b, TG);
}

/*
 * It is the caller's responsibility to ensure both that the provided pointer
 * has enough space allocated and that the memory has been zeroed
 */
void
winVectorReplace (UnnamedTG *TG, u8 *win_vec)
{
    for (u8 a = 1; a < TG->order; a++)
        {
            for (u8 b = 0; b < a; b++)
                {
                    if (unsafeReadByte (a, b, TG))
                        win_vec[a]++;
                    else
                        win_vec[b]++;
                }
        }
}

/*
 * The caller must free the array returned as it is heap allocated
 */
u8 *
winVector (UnnamedTG *TG)
{
    u8 *win_vec = calloc (TG->order, sizeof (u8));
    winVectorReplace (TG, win_vec);
    return win_vec;
}

u8
countUpsetsWithWinVec (UnnamedTG *TG, u8 *win_vec)
{
    u8 num_upsets = 0;

    for (u8 a = 1; a < TG->order; a++)
        {
            for (u8 b = 0; b < a; b++)
                {
                    bool outcome = unsafeReadByte (a, b, TG);
                    if (outcome && win_vec[a] < win_vec[b])
                        num_upsets++;
                    else if (!outcome && win_vec[a] > win_vec[b])
                        num_upsets++;
                }
        }
    return num_upsets;
}

u8
countUpsets (UnnamedTG *TG)
{
    u8 *win_vec = winVector (TG);
    u8 upsets   = countUpsetsWithWinVec (TG, win_vec);
    free (win_vec);
    return upsets;
}

UTGArena *
makeUTGArena (u8 order)
{
    if (order > 16)
        {
            fprintf (stderr,
                     "%s: called with order above 16; returning null\n",
                     __func__);
            return nullptr;
        }
    UTGArena *arena_out = calloc (1, sizeof (UTGArena) + sizeof (u8) * order);
    arena_out->tg.order = order;
    return arena_out;
}

u8
maxUpsets (u8 order)
{
    u8 max_upsets   = 0;
    UTGArena *arena = makeUTGArena (order);

    if (arena == nullptr)
        {
            fprintf (stderr, "%s: makeUTGArena returned a null pointer",
                     __func__);
            return 0;
        }

    u8 edges         = edgesOrder (order);
    u128 upper_bound = 1; // This needs to be done in this order otherwise
                          // wrapping occurs because 1 is treated as an i32
    upper_bound = upper_bound << edges;

    u8 current_upsets = 0;

    for (; arena->tg.graph < upper_bound; ++arena->tg.graph)
        {
            memset (arena->wins, 0,
                    order); // Zero out bytes for winVectorReplace
            winVectorReplace (&arena->tg, arena->wins);
            current_upsets = countUpsetsWithWinVec (&arena->tg, arena->wins);
            if (current_upsets > max_upsets)
                max_upsets = current_upsets;
        }

    free (arena);
    return max_upsets;
}
