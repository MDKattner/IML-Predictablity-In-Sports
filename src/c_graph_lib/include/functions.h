#ifndef FUNCTIONS_H
#define FUNCTIONS_H

#include "./types.h"

#include <stdbool.h>

/*
 * Returns number of edges on a TG of order n
 */
[[maybe_unused]]
static u8 edgesOrder (u8 n);
[[maybe_unused]]
static void u8Swap (u8 *a, u8 *b);
[[maybe_unused]]
static bool unsafeReadByte (u8 a, u8 b, UnnamedTG *TG);
[[maybe_unused]]
static bool readByteSafe (u8 a, u8 b, UnnamedTG *TG);
/*
 * The caller must free the array returned as it is heap alocated
 */
u8 *winVector (UnnamedTG *TG);

u8 countUpsetsWithWinVec (UnnamedTG *TG, u8 *win_vec);

u8 countUpsets (UnnamedTG *TG);

/*
 * It is the caller's responsibility to ensure both that the provided pointer
 * has enough space allocated and that the memory has been zeroed
 */
void winVectorReplace (UnnamedTG *TG, u8 *win_vec);

#endif /* ifndef FUNCTIONS_H */
