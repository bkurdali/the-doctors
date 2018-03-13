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
    'name': 'Dr. Epilepsy',
    'author': 'Bassam Kurdali, Dalai Felinto, Nathan Letwory, inspired by Bastian Salmela',
    'version': (1, 0, 9),
    "blender": (2, 7, 9),
    'location': 'View3D > OSKey-D, Help->Dr Epilepsy',
    'description': 'Dr Epililepsy will melt your brain',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Doctors'}


import bpy
import time
from random import random, randint
from mathutils import Color
from math import sin
import aud
import math
import bgl


def parseNotes(notes, bpm, basefreq, rate = 44100,
               notechars = "XXXCXDXEFXGXAXHcXdXefXgXaXhp"):
    pos = 0
    sound = None
    fadelength = 60/bpm/10
    halfchars = "#b"
    durationchars = "2345678"

    while pos < len(notes):
        char = notes[pos]
        mod = None
        dur = 1
        pos += 1
        while pos < len(notes) and notes[pos] not in notechars:
            if notes[pos] in halfchars:
                mod = notes[pos]
            elif notes[pos] in durationchars:
                dur = notes[pos]
            pos += 1

        freq = notechars.find(char)
        if mod == '#':
            freq += 1
        elif mod == 'b':
            freq -= 1

        freq = math.pow(2, freq/12)*basefreq
        length = float(dur)*60/bpm

        snd = aud.Factory.sine(freq, rate)
        if char == 'p':
            snd = snd.volume(0)
        else:
            snd = snd.square()
        snd = snd.limit(0, length)
        snd = snd.fadein(0, fadelength)
        snd = snd.fadeout(length - fadelength, fadelength)

        if sound:
            sound = sound.join(snd)
        else:
            sound = snd
    return sound


def tetris(bpm = 300, freq = 220, rate = 44100):
    notes = "e2Hcd2cH A2Ace2dc H3cd2e2 c2A2A4 pd2fa2gf e3ce2dc H2Hcd2e2 c2A2A2p2"
    s11 = parseNotes(notes, bpm, freq, rate)

    notes = "e4c4 d4H4 c4A4 G#4p4 e4c4 d4H4 A2c2a4 g#4p4"
    s12 = parseNotes(notes, bpm, freq, rate)

    notes = "EeEeEeEe AaAaAaAa AbabAbabAbabAbab AaAaAAHC DdDdDdDd CcCcCcCc HhHhHhHh AaAaA2p2"
    s21 = parseNotes(notes, bpm, freq, rate, notechars = "AXHCXDXEFXGXaXhcXdXefXgXp")

    notes = "aeaeaeae g#dg#dg#dg#d aeaeaeae g#dg#dg#2p2 aeaeaeae g#dg#dg#dg#d aeaeaeae g#dg#dg#2p2"
    s22 = parseNotes(notes, bpm, freq/2, rate)

    return s11.join(s12).join(s11).volume(0.5).mix(s21.join(s22).join(s21).volume(0.3))


def play(bpm = 300, freq = 220):
    dev = aud.device()
    h= dev.play(tetris(bpm, freq, dev.rate))
    h.loop_count = -1
    return h


def defilento(self):

    pat = self._pattern

    pat_one = pat << 1
    pat = pat >> 15
    pat |= pat_one & 0xFFFF

    self._pattern = pat

    bgl.glEnable(bgl.GL_LINE_STIPPLE)
    bgl.glLineStipple(55, self._pattern)

    width = abs(math.sin(time.time()) * 11.0)
    bgl.glLineWidth(width)

       # 2D drawing code example
    bgl.glBegin(bgl.GL_LINE_STRIP)
    bgl.glVertex2i(0, 0)
    bgl.glVertex2i(80, 100)
    bgl.glEnd()

class ModalTimerOperator(bpy.types.Operator):
    '''Operator which runs its self from a timer.'''
    bl_idname = "wm.drepilepsy"
    bl_label = "Dr Epilepsy"

    _timer = None
    _handle = None
    _pattern =  0b0011001110011001

    def modal(self, context, event):

        if event.type == 'ESC':
            return self.cancel(context)

        if event.type == 'TIMER':

            for area in context.window_manager.windows[0].screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.grid_scale = 3 + 2*sin(4*time.time())
            # change theme color, silly!
            theme = context.user_preferences.themes[0]
            for buttin in dir(theme.user_interface):
                button = getattr(theme.user_interface,buttin)
                if type(button) == bpy.types.ThemeWidgetColors:
                    for element in dir(button):
                        if element in ['outline','item','inner','inner_sel']:
                            elem = getattr(button,element)
                            #print(element,button)
                            elem[0] = random()
                            elem[1] = random()
                            elem[2] = random()
            context.user_preferences.view.ui_line_width = ('THIN', 'THICK')[randint(0,1)]
            context.user_preferences.view.ui_scale = random() * 3.0
            for vb in dir(theme):
                bov = getattr(theme,vb)
                cols = [
                    thing for thing in dir(bov)
                    if type(getattr(bov,thing))==Color
                    or (
                        type(getattr(bov, thing)) == type(theme.view_3d.face_select)
                        and len(getattr(bov, thing)) == len(theme.view_3d.face_select))]
                for col in cols:
                    color = getattr(bov,col)
                    #tcolor = bov.back
                    for i, val in enumerate(color):
                        color[i] = random()
                    setattr(bov, col, color)
            defilento(self)


        return {'PASS_THROUGH'}

    def execute(self, context):
        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(
            0.001, context.window)
        self._handle = play()
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        self._handle.stop()
        return {'CANCELLED'}


def menu_func(self, context):
    self.layout.operator(
        ModalTimerOperator.bl_idname, text="Dr Epilepsy: help me concentrate!")


def register():
    #kmi.properties.name = 'VIEW3D_MT_copypopup'
    bpy.utils.register_class(ModalTimerOperator)
    kc = bpy.context.window_manager.keyconfigs.addon
    km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new('wm.drepilepsy', 'D', 'PRESS', oskey=True)
    bpy.types.INFO_MT_help.append(menu_func)


def unregister():
    bpy.types.INFO_MT_help.remove(menu_func)
    bpy.utils.unregister_class(ModalTimerOperator)
    km = bpy.context.window_manager.keyconfigs.addon.keymaps["3D View"]
    for kmi in km.keymap_items:
        km.keymap_items.remove(kmi)

if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.wm.modal_timer_operator()
