/**********************************************************************************************************************/
/**
 * @file            vos_custom_platform.h
 *
 * @brief           Minimal platform compatibility types for custom VOS integrations
 *
 * @details         This header exists to let the generic TRDP core compile for custom targets where the application
 *                  provides the actual VOS implementation separately (for example an STM32 BSP using lwIP/FreeRTOS).
 */

#ifndef VOS_CUSTOM_PLATFORM_H
#define VOS_CUSTOM_PLATFORM_H

#include <stddef.h>
#include <stdint.h>

#if defined(__has_include)
# if __has_include(<sys/select.h>)
#  include <sys/select.h>
#  include <sys/time.h>
#  define VOS_CUSTOM_HAS_SYS_SELECT 1
# endif
#endif

#ifdef __cplusplus
extern "C" {
#endif

#ifndef VOS_CUSTOM_HAS_SYS_SELECT
#ifndef VOS_CUSTOM_FD_SET_T
#define VOS_CUSTOM_FD_SET_T
typedef struct vos_custom_fd_set
{
    uint32_t words[8];
} fd_set;
#endif

#ifndef VOS_CUSTOM_TIMEVAL_T
#define VOS_CUSTOM_TIMEVAL_T
struct timeval
{
    long tv_sec;
    long tv_usec;
};
#endif
#endif

#ifndef INADDR_ANY
#define INADDR_ANY      ((uint32_t) 0x00000000u)
#endif

#ifndef INADDR_LOOPBACK
#define INADDR_LOOPBACK ((uint32_t) 0x7f000001u)
#endif

#ifndef FD_ZERO
#define FD_ZERO(setptr)         ((void) (setptr))
#endif
#ifndef FD_SET
#define FD_SET(fd, setptr)      ((void) (fd), (void) (setptr))
#endif
#ifndef FD_CLR
#define FD_CLR(fd, setptr)      ((void) (fd), (void) (setptr))
#endif
#ifndef FD_ISSET
#define FD_ISSET(fd, setptr)    (0)
#endif

#ifdef __cplusplus
}
#endif

#endif /* VOS_CUSTOM_PLATFORM_H */
