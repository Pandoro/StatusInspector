#!/usr/bin/env python
# -*- coding:utf-8 -*-


##
# Python function for reading linux utmp/wtmp file
# http://www.likexian.com/
#
# Copyright 2014, Kexian Li
# Released under the Apache License, Version 2.0
#
# Changes:
# Commented out example executions at the end of the file
# and added the status definitions.
##


import struct

# /* Values for ut_type field, below */

# #define EMPTY         0 /* Record does not contain valid info
#                           (formerly known as UT_UNKNOWN on Linux) */
# #define RUN_LVL       1 /* Change in system run-level (see
#                           init(8)) */
# #define BOOT_TIME     2 /* Time of system boot (in ut_tv) */
# #define NEW_TIME      3 /* Time after system clock change
#                           (in ut_tv) */
# #define OLD_TIME      4 /* Time before system clock change
#                           (in ut_tv) */
# #define INIT_PROCESS  5 /* Process spawned by init(8) */
# #define LOGIN_PROCESS 6 /* Session leader process for user login */
# #define USER_PROCESS  7 /* Normal process */
# #define DEAD_PROCESS  8 /* Terminated process */
# #define ACCOUNTING    9 /* Not implemented */
#
# #define UT_LINESIZE      32
# #define UT_NAMESIZE      32
# #define UT_HOSTSIZE     256
#
# struct exit_status {              /* Type for ut_exit, below */
#    short int e_termination;      /* Process termination status */
#    short int e_exit;             /* Process exit status */
# };
#
# struct utmp {
#    short   ut_type;              /* Type of record */
#    pid_t   ut_pid;               /* PID of login process */
#    char    ut_line[UT_LINESIZE]; /* Device name of tty - "/dev/" */
#    char    ut_id[4];             /* Terminal name suffix,
#                                     or inittab(5) ID */
#    char    ut_user[UT_NAMESIZE]; /* Username */
#    char    ut_host[UT_HOSTSIZE]; /* Hostname for remote login, or
#                                     kernel version for run-level
#                                     messages */
#    struct  exit_status ut_exit;  /* Exit status of a process
#                                     marked as DEAD_PROCESS; not
#                                     used by Linux init(8) */
#    /* The ut_session and ut_tv fields must be the same size when
#       compiled 32- and 64-bit.  This allows data files and shared
#       memory to be shared between 32- and 64-bit applications. */
# #if __WORDSIZE == 64 && defined __WORDSIZE_COMPAT32
#    int32_t ut_session;           /* Session ID (getsid(2)),
#                                     used for windowing */
#    struct {
#        int32_t tv_sec;           /* Seconds */
#        int32_t tv_usec;          /* Microseconds */
#    } ut_tv;                      /* Time entry was made */
# #else
#     long   ut_session;           /* Session ID */
#     struct timeval ut_tv;        /* Time entry was made */
# #endif
#
#    int32_t ut_addr_v6[4];        /* Internet address of remote
#                                     host; IPv4 address uses
#                                     just ut_addr_v6[0] */
#    char __unused[20];            /* Reserved for future use */
# };
XTMP_STRUCT = 'hi32s4s32s256shhiii4i20x'
XTMP_STRUCT_SIZE = struct.calcsize(XTMP_STRUCT)


def read_xtmp(fname):
    result = []

    fp = open(fname, 'rb')
    while True:
        bytes = fp.read(XTMP_STRUCT_SIZE)
        if not bytes:
            break

        data = struct.unpack(XTMP_STRUCT, bytes)
        data = [(lambda s: str(s).split("\0", 1)[0])(i) for i in data]
        if data[0] != '0':
            result.append(data)

    fp.close()
    result.reverse()

    return result


# print 'reading data from utmp'
# data = read_xtmp('/var/run/utmp')
# for i in data:
#     print i

# print
# print 'reading data from wtmp'
# data = read_xtmp('/var/log/wtmp')
# for i in data:
#     print i
