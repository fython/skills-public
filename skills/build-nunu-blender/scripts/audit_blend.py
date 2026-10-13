"""Collect raw mesh evidence. Run inside Blender; this is not a visual/sewing validator."""
import argparse
import json
import sys
from pathlib import Path
import bpy
import bmesh


def inspect_mesh(obj):
    me = obj.data
    used = set()
    graph = {}
    for edge in me.edges:
        a, b = edge.vertices
        used.update((a, b))
        graph.setdefault(a, []).append(b)
        graph.setdefault(b, []).append(a)
    for face in me.polygons:
        used.update(face.vertices)
    remaining = set(used)
    components = []
    while remaining:
        todo = [remaining.pop()]
        size = 0
        while todo:
            node = todo.pop()
            size += 1
            for other in graph.get(node, []):
                if other in remaining:
                    remaining.remove(other)
                    todo.append(other)
        components.append(size)
    bm = bmesh.new()
    try:
        bm.from_mesh(me)
        boundary = sum(e.is_boundary for e in bm.edges)
        nonmanifold = sum(not e.is_manifold for e in bm.edges)
    finally:
        bm.free()
    points = [obj.matrix_world @ v.co for v in me.vertices]
    bounds = None if not points else {
        'min': [min(p[i] for p in points) for i in range(3)],
        'max': [max(p[i] for p in points) for i in range(3)],
    }
    return {
        'name': obj.name,
        'filled_with_cotton': obj.get('filled_with_cotton'),
        'source_pattern': obj.get('source_pattern'),
        'vertices': len(me.vertices),
        'faces': len(me.polygons),
        'used_vertex_components': sorted(components, reverse=True),
        'loose_vertices': len(me.vertices) - len(used),
        'boundary_edges': boundary,
        'non_manifold_edges': nonmanifold,
        'uv_layers': [u.name for u in me.uv_layers],
        'materials': [m.name if m else None for m in me.materials],
        'modifiers': [{'name': m.name, 'type': m.type, 'render': m.show_render} for m in obj.modifiers],
        'raw_world_bounds': bounds,
    }


def main():
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    options = parser.parse_args(args)
    report = {
        'blender_version': bpy.app.version_string,
        'blend_file': bpy.data.filepath,
        'scope': 'Raw meshes only; excludes modifier evaluation, collision, physical sewing and visual QA.',
        'unit_scale': bpy.context.scene.unit_settings.scale_length,
        'objects': [inspect_mesh(o) for o in bpy.context.scene.objects if o.type == 'MESH'],
        'images': [{'name': i.name, 'size': list(i.size), 'packed': bool(i.packed_file), 'path': i.filepath}
                   for i in bpy.data.images if i.source == 'FILE'],
    }
    out = Path(options.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Wrote raw-mesh evidence:', out)


if __name__ == '__main__':
    main()
