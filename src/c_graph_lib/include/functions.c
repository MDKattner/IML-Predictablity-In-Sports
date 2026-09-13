#include "./functions.h"
#include "./types.h"

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

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
            fprintf (stderr, "Verticies are too large for graph of order %u",
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
