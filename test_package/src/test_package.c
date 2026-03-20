#include "tau_ctrl.h"
#include "tau_dnr.h"
#include "tau_marshall.h"
#include "tau_tti.h"
#include "tau_xml.h"
#include "trdp_if_light.h"

int main(void)
{
    return !(
        tlc_init &&
        tlc_openSession &&
        tlc_closeSession &&
        tlc_terminate &&
        tlp_publish &&
        tlp_subscribe &&
        tau_initMarshall &&
        tau_prepareXmlDoc &&
        tau_initDnr &&
        tau_initTTIaccess &&
        tau_initEcspCtrl);
}
