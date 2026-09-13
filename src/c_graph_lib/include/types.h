#ifndef TYPES_h
#define TYPES_h
#include <stdint.h>

typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
typedef unsigned _BitInt (128) u128;

typedef int8_t i8;
typedef int16_t i16;
typedef int32_t i32;
typedef int64_t i64;

/*
 * The current data type can store tournament graphs (TGs) of up to order 16.
 * This is because there are 120 edges on TGs of order 16 while there are 136
 * on TGs of order 17 and we encode each edge into our 128 bit number.
 */
typedef struct _unnamedtg
{
    u128 graph;
    /*
     * This encoding uses the fact that the only difference between two TGs of
     * the same order is the (binary) direction of the edges. So each edge is
     * represented by a single bit.
     *
     * We encode this as so:
     * for vertices v_i, v_j, let a = max(i,j), b = min(i,j).
     * Then find the bit at a(a - 1)/2 + b.
     * If this bit is 1 then team v_a beat team v_b, otherwise the opposite is
     * true.
     */
    u8 order;
} UnnamedTG;

typedef struct _tournomentgraph
{
    UnnamedTG tg;
    char *team_names[4]; // VLAs are allowed at the ends of structs as of c11
    /*
     * For a team v_i this array stores the team name of v_i at i
     * Teams must be stored as their 3 letter shorthand (the extra character is
     * for the null terminator).
     *
     * For example:
     * Chicago White Sox |-> "CWC".
     * LA Rams |-> "LAR".
     * Chicago Bears |-> "Chi".
     * Manchester City |-> "MCI".
     * Here is a link for reference:
     * https://www.interestingfootball.com/2025/10/sports-teams-codes-3-letter-short-name.html
     */
} TournomentGraph;

#endif /* ifndef TYPES_h */
