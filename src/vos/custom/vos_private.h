/**********************************************************************************************************************/
/**
 * @file            custom/vos_private.h
 *
 * @brief           Private definitions for custom VOS integrations
 *
 * @details         Minimal placeholder types that allow the TRDP core to be compiled as a static library while the
 *                  final application provides the concrete VOS implementation for its target platform.
 */

#ifndef VOS_PRIVATE_H
#define VOS_PRIVATE_H

#include <string.h>

#include "vos_types.h"
#include "vos_thread.h"
#include "vos_sock.h"

#ifdef __cplusplus
extern "C" {
#endif

#ifndef VOS_VERSION
#define VOS_VERSION            3u
#define VOS_RELEASE            0u
#define VOS_UPDATE             0u
#define VOS_EVOLUTION          0u
#endif

struct VOS_MUTEX
{
    UINT32  magicNo;
    UINT32  opaque[4];
};

struct VOS_SEMA
{
    UINT32  opaque[4];
};

struct VOS_SHRD
{
    INT32   fd;
    CHAR8   *sharedMemoryName;
};

#define STRING_ERR(pStrBuf)                                 \
    do                                                      \
    {                                                       \
        if ((pStrBuf) != NULL)                              \
        {                                                   \
            (void) strncpy((pStrBuf), "custom-vos", VOS_MAX_ERR_STR_SIZE); \
        }                                                   \
    } while (0)

EXT_DECL VOS_ERR_T vos_mutexLocalCreate (struct VOS_MUTEX *pMutex);
EXT_DECL void vos_mutexLocalDelete (struct VOS_MUTEX *pMutex);
EXT_DECL VOS_ERR_T vos_sockSetBuffer (VOS_SOCK_T sock);

#ifdef __cplusplus
}
#endif

#endif /* VOS_PRIVATE_H */
