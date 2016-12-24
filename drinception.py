# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    'name': 'Dr. Inception',
    'author': 'Bassam Kurdali,',
    'version': (0, 0, 1),
    "blender": (2, 7, 8),
    'location': 'View3D > OSKey-shift-D, Help->Dr Inception',
    'description': 'Dr Inception will BLOW YOUR MIIIIIIIIND',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Doctors'}

import bpy
from mathutils import Vector

# following data from grab_data.py
link_data = [{'to_node': {'name': 'dr_inception_out'}, 'from_socket': {'name': 'Image', 'index': 0}, 'to_socket': {'name': 'Image', 'index': 0}, 'from_node': {'name': 'dr_inception_in'}}]
node_data = {'dr_inception_in': {'select': False, 'width': 140.0, 'mute': False, 'label': '', 'width_hidden': 42.0, 'height': 100.0, 'location': Vector((18.404338836669922, 86.67772674560547)), 'bl_idname': 'CompositorNodeImage', 'hide': False}, 'dr_inception_out': {'select': True, 'width': 140.0, 'mute': False, 'label': '', 'width_hidden': 42.0, 'height': 100.0, 'location': Vector((289.0699462890625, 97.14015197753906)), 'bl_idname': 'CompositorNodeViewer', 'hide': False}}


def build_nodes(scene, image):
    if not scene.node_tree or not scene.use_nodes:
        scene.use_nodes = True
    nodes = scene.node_tree.nodes
    links = scene.node_tree.links
    if all(node in scene.node_tree.nodes for node in node_data):
        return

    for name, node in node_data.items():
        scene_node = nodes.new(type=node['bl_idname'])
        scene_node.name = name
        if name == 'dr_inception_out':
            nodes.active = scene_node
        for property, value in node.items():
            if not property == 'bl_idname':
                setattr(scene_node, property, value)
        if name == 'dr_inception_in':
            scene_node.image = image
    for link in link_data:
        input = nodes[
            link['from_node']['name']].outputs[link['from_socket']['index']]
        output = nodes[
            link['to_node']['name']].inputs[link['to_socket']['index']]
        scene_link = links.new(input, output)


def type_hack(theme):
    """
    Too stupid to figure out the right types in advance, we get them
    from theme properties we know in advance are colors
    """
    color_array = {
        'type': type(theme.view_3d.face_select),
        'len':len(theme.view_3d.face_select)}
    color = {
        'type': type(theme.view_3d.wire),
        'len': len(theme.view_3d.wire)}
    return color, color_array


def recursive_theme_color_getter(
        theme, theme_str, color, color_array, recursion):
    recursion +=1
    if recursion > 100:
        return {}
    retval = {theme_str:[]}
    legals = (
        a for a in dir(theme) if not a.startswith('__')
        and not a.startswith('bl_') and not a == 'data'
        and not a.startswith('rna') and not callable(getattr(theme, a))
        and not type(getattr(theme, a)) in (int, float, str))

    for attr in legals:
        prop = getattr(theme, attr)
        if (
                (
                    type(prop) == color_array['type']
                    and len(prop) == color_array['len'])
                or (type(prop) == color['type'])):
            retval[theme_str].append((attr))
        else:
            result = recursive_theme_color_getter(
                prop, attr, color, color_array, recursion)
            # result = {}
            if result and any(v for v in result.values()):
                retval[theme_str].append(result)
    return retval


def recursive_length(thing):
    current = 0
    for itm in thing:
        if type(thing) == dict:
            if type(thing[itm]) == str:
                current += 1
            else:
                current += recursive_length(thing[itm])
        elif type(thing) == list:
            if type(itm) == str:
                current += 1
            else:
                current += recursive_length(itm)
    return current


def recursive_pixel_color(image, stored, active, index):
    for item in stored:
        if type(stored) == dict:
            if type(stored[item]) == str:
                col = getattr(active, stored[item])
                for i, val in enumerate(col):
                    image.pixels[index + i] = val
                index += 4
            else:
                index = recursive_pixel_color(
                    image, stored[item], getattr(active,stored[item]), index)
        elif type(stored) == list:
            if type(item) == str:
                col = getattr(active, item)
                for i, val in enumerate(col):
                    image.pixels[index + i] = val
                index += 4
            elif type(item) == dict:
                for prop in item:
                    index = recursive_pixel_color(
                        image, item[prop], getattr(active, prop), index)
    return index


def recursive_color_from_pixel(image, stored, active, index):
    for item in stored:
        if type(stored) == dict:
            if type(stored[item]) == str:
                col = getattr(active, stored[item])
                for i, val in enumerate(col):
                    col[i] = image.pixels[index + i]
                setattr(active, stored[item], col)
                index += 4
            else:
                index = recursive_color_from_pixel(
                    image, stored[item], getattr(active,stored[item]), index)
        elif type(stored) == list:
            if type(item) == str:
                col = getattr(active, item)
                for i, val in enumerate(col):
                    col[i] = image.pixels[index + i]
                setattr(active, item, col)
                index += 4
            elif type(item) == dict:
                for prop in item:
                    index = recursive_color_from_pixel(
                        image, item[prop], getattr(active, prop), index)
    return index


def image_make(theme, struct, color, color_array, image_name):
    color_count = recursive_length(struct)
    i = 10
    while i <= color_count:
        i += 10
    images = (
        im for im in bpy.data.images if im.name.startswith(image_name)
        and im.type == 'UV_TEST'
        and im.generated_width == i/10 and im.generated_height == 10)
    for im in images:
        break
    try:
        im
    except NameError:
        im = bpy.data.images.new(image_name, i/10, 10)
    im.colorspace_settings.name = 'Non-Color'
    recursive_pixel_color(im, struct, theme, 0)
    return im, color_count


def make_updater(theme, struct, color, color_array):
    def dr_inception_update(scene):
        """DR_INCEPTION_UPDATE"""
        recursive_color_from_pixel(
            bpy.data.images['Viewer Node'],
            struct,
            theme,
            0)
    return dr_inception_update


class DrInception(bpy.types.Operator):
    bl_idname = "wm.drinception"
    bl_label = "Dr Inception"

    _updater = None

    @classmethod
    def poll(cls, context):
        for area in context.screen.areas:
            if area.type == 'NODE_EDITOR':
                return True
        return False

    def modal(self, context, event):
        if event.type == 'ESC':
            return self.cancel(context)
        return {'PASS_THROUGH'}

    def execute(self, context):
        image_name = "dr_epilepsy_base"
        scene = context.scene
        theme = context.user_preferences.themes['Default']
        color, color_array = type_hack(theme)
        struct = recursive_theme_color_getter(
            theme, "theme", color, color_array, 0)
        struct = struct["theme"]
        image, color_count = image_make(
            theme, struct, color, color_array, image_name)
        self._updater = make_updater(theme, struct, color, color_array)
        build_nodes(scene, image)
        bpy.app.handlers.scene_update_post.append(self._updater)
        context.window_manager.modal_handler_add(self)
        space = context.space_data
        if not space or not space.type == 'NODE_EDITOR':
            spaces = [
                a.spaces[0] for a in context.screen.areas if a.type == 'NODE_EDITOR']
            if spaces:
                space = spaces[0]
        if space and space.type == 'NODE_EDITOR':
            space.show_backdrop = True
            space.tree_type = 'CompositorNodeTree'
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        if bpy.app.handlers.scene_update_post and self._updater:
            bpy.app.handlers.scene_update_post.remove(self._updater)
        return {'CANCELLED'}


def menu_func(self, context):
    self.layout.operator(
        DrInception.bl_idname, text="Dr Inception: blend blender!")


def register():
    bpy.utils.register_class(DrInception)
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
    kmi = km.keymap_items.new('wm.drinception', 'D', 'PRESS', oskey=True)
    bpy.types.INFO_MT_help.append(menu_func)


def unregister():
    bpy.types.INFO_MT_help.remove(menu_func)
    km = bpy.context.window_manager.keyconfigs.addon.keymaps['Node Editor']
    for kmi in km.keymap_items:
        km.keymap_items.remove(kmi)
    bpy.utils.unregister_class(DrInception)

if __name__ == "__main__":
    register()

