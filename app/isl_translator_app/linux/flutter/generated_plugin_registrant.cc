//
//  Generated file. Do not edit.
//

// clang-format off

#include "generated_plugin_registrant.h"

#include <hand_detection/hand_detection_plugin.h>

void fl_register_plugins(FlPluginRegistry* registry) {
  g_autoptr(FlPluginRegistrar) hand_detection_registrar =
      fl_plugin_registry_get_registrar_for_plugin(registry, "HandDetectionPlugin");
  hand_detection_plugin_register_with_registrar(hand_detection_registrar);
}
