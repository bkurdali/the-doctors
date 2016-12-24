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

import bpy
from mathutils import Vector

def get_console(text, which):
    """
    copy data to bpy.texts text at current cursor position
    which data can be
    'nodes' for scene nodes, or
    'links' for scene links
    """
    node_tree = bpy.context.scene.node_tree
    node_values = [
        'bl_idname', 'height', 'width', 'width_hidden',
        'mute', 'hide', 'label', 'location', 'select']
    if which == 'links':
        things = [{
            'from_socket': {
                'name': link.from_socket.name,
                'index': link.from_socket.getIndex()},
            'from_node': {'name': link.from_node.name},
            'to_socket': {
                'name': link.to_socket.name,
                'index': link.to_socket.getIndex()},
            'to_node':{
                'name': link.to_node.name}} for link in node_tree.links]
    elif which == 'nodes':
        things = {
            node.name: {
                attr: getattr(node, attr)
                for attr in node_values if attr in dir(node)}
            for node in node_tree.nodes}
    text.write(things.__repr__())
