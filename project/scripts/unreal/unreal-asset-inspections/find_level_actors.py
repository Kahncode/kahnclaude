"""
Find all actors of a given class in the current editor world.
Run via UE5 Python remote execution.

Set CLASS_FILTER before executing, e.g.:
    CLASS_FILTER = "Character"

Matches any actor whose class name contains the filter string (case-sensitive).
"""

import re
import unreal

# ── Configure this before running ──
CLASS_FILTER = "Character"

# Base AActor attributes to skip (noisy defaults).
_ACTOR_SKIP = {
    "actor_guid", "actor_instance_guid", "always_relevant",
    "auto_destroy_when_finished", "can_be_damaged", "content_bundle_guid",
    "custom_time_dilation", "enable_auto_lod_generation",
    "find_camera_component_when_view_target",
    "generate_overlap_events_during_level_streaming", "hidden",
    "initial_life_span", "instigator", "is_spatially_loaded", "life_span",
    "min_net_update_frequency", "net_cull_distance_squared", "net_dormancy",
    "net_priority", "net_update_frequency", "net_use_owner_relevancy",
    "on_actor_begin_overlap", "on_actor_end_overlap", "on_actor_hit",
    "on_actor_touch", "on_actor_un_touch", "on_begin_cursor_over",
    "on_clicked", "on_destroyed", "on_end_cursor_over", "on_end_play",
    "on_input_touch_begin", "on_input_touch_end", "on_input_touch_enter",
    "on_input_touch_leave", "on_released", "on_take_any_damage",
    "on_take_point_damage", "on_take_radial_damage", "only_relevant_to_owner",
    "pivot_offset", "replicate_using_registered_sub_object_list", "replicates",
    "root_component", "runtime_grid", "spawn_collision_handling_method",
    "sprite_scale", "tags",
    # Deprecated aliases
    "life_span", "on_actor_touch", "on_actor_un_touch",
}

# Base USceneComponent / UActorComponent attributes to skip.
_COMP_SKIP = {
    "absolute_location", "absolute_rotation", "absolute_scale",
    "auto_activate", "can_ever_affect_navigation",
    "component_tags", "component_velocity", "detail_mode",
    "hidden_in_game", "is_editor_only", "mobility",
    "on_component_activated", "on_component_deactivated",
    "on_component_hit", "on_component_begin_overlap",
    "on_component_end_overlap", "on_component_sleep",
    "on_component_wake", "physics_volume_changed_delegate",
    "primary_component_tick", "relative_location",
    "relative_rotation", "relative_scale3d",
    "should_update_physics_volume", "use_attach_parent_bound",
    "visible",
    # Deprecated aliases
    "b_absolute_translation", "modify_frequency", "relative_translation",
}


def parse_tags(container):
    """Extract tag names from a FGameplayTagContainer via export_text()."""
    text = container.export_text()
    return re.findall(r'TagName="([^"]+)"', text) if text else []


def _get_attrs(obj):
    """Get non-dunder, non-callable attribute names on obj, suppressing deprecation warnings."""
    import warnings
    out = []
    for a in dir(obj):
        if a.startswith("_"):
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                v = getattr(obj, a, None)
        except Exception:
            continue
        if not callable(v):
            out.append(a)
    return out


def format_val(val):
    """Pretty-print a UPROPERTY value."""
    type_name = type(val).__name__
    if type_name == "GameplayTagContainer":
        tags = parse_tags(val)
        return ", ".join(tags) if tags else "(none)"
    return val


def dump_properties(obj, indent="    ", skip=None):
    """Print all readable UPROPERTY values on obj, skipping base-class noise."""
    skip = skip or set()
    for name in sorted(_get_attrs(obj)):
        if name in skip:
            continue
        try:
            val = obj.get_editor_property(name)
            unreal.log(f"{indent}{name}: {format_val(val)}")
        except Exception:
            pass


def main():
    editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = editor_subsystem.get_editor_world()
    if world is None:
        unreal.log_error("No editor world found.")
        return

    unreal.log(f"World: {world.get_name()}")
    unreal.log(f"Filter: \"{CLASS_FILTER}\"\n")

    all_actors = unreal.EditorLevelLibrary.get_all_level_actors()
    matches = [a for a in all_actors if CLASS_FILTER in a.get_class().get_name()]

    if not matches:
        unreal.log_warning(f"No actors matching \"{CLASS_FILTER}\" found.")
        return

    unreal.log(f"Found {len(matches)} actor(s):\n")

    for i, actor in enumerate(matches):
        loc = actor.get_actor_location()
        rot = actor.get_actor_rotation()
        label = actor.get_actor_label()
        class_name = actor.get_class().get_name()

        unreal.log("=" * 70)
        unreal.log(f"[{i}] {label}  ({class_name})")
        unreal.log(f"    Location: X={loc.x:.1f}  Y={loc.y:.1f}  Z={loc.z:.1f}")
        unreal.log(f"    Rotation: P={rot.pitch:.1f}  Y={rot.yaw:.1f}  R={rot.roll:.1f}")
        unreal.log(f"  Properties:")
        dump_properties(actor, indent="    ", skip=_ACTOR_SKIP)

        # Dump components (skip pure base types)
        components = actor.get_components_by_class(unreal.ActorComponent)
        for comp in components:
            comp_class = comp.get_class().get_name()
            if comp_class in ("SceneComponent", "BillboardComponent"):
                continue
            unreal.log(f"  --- {comp.get_name()} ({comp_class}) ---")
            dump_properties(comp, indent="      ", skip=_COMP_SKIP)

    unreal.log("=" * 70)
    unreal.log(f"Total: {len(matches)}")


main()
