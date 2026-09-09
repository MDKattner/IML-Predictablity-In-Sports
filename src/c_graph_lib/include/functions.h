#ifndef FUNCTIONS_H
#define FUNCTIONS_H

#include "./types.h"

#include <stdbool.h>

/*
 * Returns number of edges on a TG of order n
 */
static u8 edgesOrder (u8 n);

static void u8Swap (u8 *a, u8 *b);
static bool unsafeReadByte (u8 a, u8 b, UnnamedTG *TG);
static bool readByte (u8 a, u8 b, UnnamedTG *TG);
/*
 * The caller must free the array returned as it is heap alocated
 */
u8 *winVector (UnnamedTG *TG);
u8 countUpsetsWithWinVec (UnnamedTG *TG, u8 *win_vec);
u8 countUpsets (UnnamedTG *TG);

#endif /* ifndef FUNCTIONS_H */
