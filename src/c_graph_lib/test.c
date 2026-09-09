#include "./include/types.h"
#include <stdio.h>
#include <stdlib.h>

// DO NOT CHANGE INCLUDES ORDER THIS MUST ALWAYS BE AT THE TOP BECAUSE THIS
// PROJECT IS A UNITY BUILD
#include "./include/functions.c"

int
main (int argc, char *argv[])
{
    u8 order = (u8)atoi (argv[1]);
    u8 edges = edgesOrder (order);
    //    UnnamedTG TG = { .graph = 0, .order = order };
    //    u8 *win_vec  = winVector (&TG);
    //
    //    printf ("[");
    //    for (u8 i = 0; i < TG.order; i++)
    //        {
    //            printf (" %u", win_vec[i]);
    //        }
    //    printf (" ]\n");
    //
    //    printf ("Upsets: %u", countUpsetsWithWinVec (&TG, win_vec));
    //
    //    free (win_vec);
    u8 max_upsets    = 0;
    u128 upper_bound = 1;
    upper_bound      = upper_bound << edges;
    printf ("Calculated upper bound: %llu\n", upper_bound);
    UnnamedTG TG = { .graph = 0, .order = order };
    for (; TG.graph < upper_bound; TG.graph++)
        {
            u8 current_upsets = countUpsets (&TG);
            if (current_upsets > max_upsets)
                max_upsets = current_upsets;
        }
    printf ("Maximum graph value: %llu\n", TG.graph);
    printf ("Max Upsets: %u", max_upsets);
    return 0;
}
