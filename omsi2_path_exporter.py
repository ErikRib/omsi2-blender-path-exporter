bl_info = {
    "name": "OMSI 2 Path / PassengerCabin Exporter",
    "author": "Claude (para Japa Games)",
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Tool Shelf > OMSI 2",
    "description": "Cria e exporta path points e posicoes de passageiros para o OMSI 2",
    "category": "Import-Export",
}

import bpy
from bpy.props import StringProperty, EnumProperty
from bpy.types import Operator, Panel


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_path_objects():
    objs = [o for o in bpy.context.scene.objects if o.name.startswith("PATH_")]
    def key(o):
        try: return int(o.name[5:].split('_')[0])
        except: return 9999
    return sorted(objs, key=key)


def get_passpos_objects():
    objs = [o for o in bpy.context.scene.objects if o.name.startswith("PASSPOS_")]
    def key(o):
        try: return int(o.name[8:].split('_')[0])
        except: return 9999
    return sorted(objs, key=key)


def fmt(v):
    """Formata float sem zeros desnecessarios."""
    s = ("%.6f" % v).rstrip('0').rstrip('.')
    return s if s not in ('', '-') else '0'


# ─── Operadores: Path Points ───────────────────────────────────────────────────

class OMSI_OT_AddPathPoint(Operator):
    bl_idname = "omsi.add_pathpoint"
    bl_label = "Adicionar Path Point"
    bl_description = "Adiciona PATH_N na posicao do cursor 3D"

    def execute(self, context):
        existing = get_path_objects()
        indices = []
        for o in existing:
            try: indices.append(int(o.name[5:].split('_')[0]))
            except: pass
        next_idx = (max(indices) + 1) if indices else 0

        bpy.ops.object.empty_add(type='PLAIN_AXES', location=context.scene.cursor_location)
        obj = context.active_object
        obj.name = "PATH_%d" % next_idx
        obj["omsi_links"] = ""
        obj["omsi_links_oneway"] = ""
        obj.empty_draw_size = 0.1
        self.report({'INFO'}, "PATH_%d adicionado" % next_idx)
        return {'FINISHED'}


class OMSI_OT_AddRoomHeight(Operator):
    bl_idname = "omsi.add_roomheight"
    bl_label = "Adicionar Room Height"
    bl_description = "Adiciona propriedade omsi_roomheight ao PATH_ selecionado"

    def execute(self, context):
        obj = context.active_object
        if obj and obj.name.startswith("PATH_"):
            obj["omsi_roomheight"] = 2.5
            self.report({'INFO'}, "omsi_roomheight = 2.5 adicionado")
        return {'FINISHED'}


class OMSI_OT_ExportPath(Operator):
    bl_idname = "omsi.export_path"
    bl_label = "Exportar Path CFG"
    bl_description = "Exporta objetos PATH_N para arquivo pathUDA.cfg do OMSI 2"

    filepath = StringProperty(subtype='FILE_PATH', default="pathUDA.cfg")

    def execute(self, context):
        objs = get_path_objects()
        if not objs:
            self.report({'WARNING'}, "Nenhum objeto PATH_N encontrado na cena.")
            return {'CANCELLED'}

        lines = [
            "---------------------------",
            "Soundsets:",
            "",
            "0 - Normal:",
            "[stepsoundpack]",
            "5",
            "HH109Step_01.wav",
            "HH109Step_02.wav",
            "HH109Step_03.wav",
            "HH109Step_04.wav",
            "HH109Step_05.wav",
            "",
            "",
            "---------------------------",
            "Pathpoints:",
            "",
        ]

        for obj in objs:
            try: idx = int(obj.name[5:].split('_')[0])
            except: continue
            loc = obj.location
            lines += [str(idx), "[pathpnt]", fmt(loc.x), fmt(loc.y), fmt(loc.z), ""]

        lines += ["", "#########################", "Pathlinks:", "", "[next_stepsound]", "0", ""]

        for obj in objs:
            try: src = int(obj.name[5:].split('_')[0])
            except: continue

            rh = obj.get("omsi_roomheight", None)
            if rh is not None:
                lines += ["[next_roomheight]", fmt(float(rh)), ""]

            links = str(obj.get("omsi_links", "")).strip()
            if links:
                for tgt in links.split(','):
                    tgt = tgt.strip()
                    if tgt:
                        lines += ["[pathlink]", str(src), tgt, ""]

            links_ow = str(obj.get("omsi_links_oneway", "")).strip()
            if links_ow:
                for tgt in links_ow.split(','):
                    tgt = tgt.strip()
                    if tgt:
                        lines += ["[pathlink_oneway]", str(src), tgt, ""]

        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        self.report({'INFO'}, "Exportado: %d pontos -> %s" % (len(objs), self.filepath))
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


# ─── Operadores: Passenger Cabin ──────────────────────────────────────────────

class OMSI_OT_AddPassPos(Operator):
    bl_idname = "omsi.add_passpos"
    bl_label = "Adicionar PassPos"
    bl_description = "Adiciona PASSPOS_N na posicao do cursor 3D"

    pass_type = EnumProperty(
        name="Tipo",
        items=[
            ('stand', "Em pe  (h=0)",    "Passageiro em pe"),
            ('seat',  "Sentado (h=0.42)", "Passageiro sentado"),
        ],
        default='stand'
    )

    def execute(self, context):
        existing = get_passpos_objects()
        indices = []
        for o in existing:
            try: indices.append(int(o.name[8:].split('_')[0]))
            except: pass
        next_idx = (max(indices) + 1) if indices else 0

        bpy.ops.object.empty_add(type='ARROWS', location=context.scene.cursor_location)
        obj = context.active_object
        obj.name = "PASSPOS_%d" % next_idx
        obj["omsi_h"]   = 0.42 if self.pass_type == 'seat' else 0.0
        obj["omsi_rot"] = 0.0
        obj.empty_draw_size = 0.15
        self.report({'INFO'}, "PASSPOS_%d adicionado" % next_idx)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        self.layout.prop(self, "pass_type")


class OMSI_OT_ExportPassCabin(Operator):
    bl_idname = "omsi.export_passcabin"
    bl_label = "Exportar PassengerCabin CFG"
    bl_description = "Exporta PASSPOS_N, DRIVPOS, ENTRY_N, EXIT_N para passengercabin.cfg"

    filepath = StringProperty(subtype='FILE_PATH', default="passengercabin.cfg")

    def execute(self, context):
        scene_objs = bpy.context.scene.objects
        lines = []

        # Entries
        entries = sorted([o for o in scene_objs if o.name.startswith("ENTRY_")], key=lambda o: o.name)
        for obj in entries:
            lines += ["[entry]", str(int(obj.get("omsi_pathpnt", 0))), ""]

        # Exits
        exits = sorted([o for o in scene_objs if o.name.startswith("EXIT_")], key=lambda o: o.name)
        for obj in exits:
            lines += ["[exit]", str(int(obj.get("omsi_pathpnt", 0))), ""]

        # LinkToPrevVeh / LinkToNextVeh
        for obj in [o for o in scene_objs if o.name.startswith("LINKTOPREV")]:
            lines += ["[linkToPrevVeh]", str(int(obj.get("omsi_pathpnt", 0))), ""]
        for obj in [o for o in scene_objs if o.name.startswith("LINKTONEXT")]:
            lines += ["[linkToNextVeh]", str(int(obj.get("omsi_pathpnt", 0))), ""]

        # Stamper
        for obj in sorted([o for o in scene_objs if o.name.startswith("STAMPER_")], key=lambda o: o.name):
            pnt = int(obj.get("omsi_pathpnt", 0))
            loc = obj.location
            lines += ["[stamper]", str(pnt), fmt(loc.x), fmt(loc.y), fmt(loc.z), ""]

        lines += ["", "###################################", ""]

        # Driver position
        driv = sorted([o for o in scene_objs if o.name.startswith("DRIVPOS")], key=lambda o: o.name)
        for obj in driv:
            loc = obj.location
            lines += [
                "[drivpos]",
                fmt(loc.x), fmt(loc.y), fmt(loc.z),
                fmt(float(obj.get("omsi_h",   0.44))),
                fmt(float(obj.get("omsi_rot", 0))),
                "",
            ]

        lines += ["###################################", "Passenger Positions", "###################################", ""]

        # Passenger positions
        passpos = get_passpos_objects()
        for obj in passpos:
            loc = obj.location
            lines += [
                "[passpos]",
                fmt(loc.x), fmt(loc.y), fmt(loc.z),
                fmt(float(obj.get("omsi_h",   0))),
                fmt(float(obj.get("omsi_rot", 0))),
                "",
            ]

        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        self.report({'INFO'}, "Exportado: %d passpos -> %s" % (len(passpos), self.filepath))
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


# ─── Painel ───────────────────────────────────────────────────────────────────

class OMSI_PT_MainPanel(Panel):
    bl_label = "OMSI 2 Exporter"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category    = "OMSI 2"

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        # ── PATH ──────────────────────────────────────
        box = layout.box()
        box.label("Path Points (pathUDA.cfg):", icon='CURVE_PATH')
        box.operator("omsi.add_pathpoint", icon='ZOOMIN', text="Adicionar PATH_N")
        box.operator("omsi.export_path",   icon='EXPORT',  text="Exportar Path CFG")

        if obj and obj.name.startswith("PATH_"):
            sub = box.box()
            sub.label("Selecionado: " + obj.name, icon='EMPTY_DATA')
            sub.prop(obj, '["omsi_links"]',         text="Links  (ex: 1,2,3)")
            sub.prop(obj, '["omsi_links_oneway"]',   text="One-way (ex: 0)")
            if "omsi_roomheight" in obj:
                sub.prop(obj, '["omsi_roomheight"]', text="Room Height")
            else:
                sub.operator("omsi.add_roomheight",  text="+ Room Height", icon='ZOOMIN')

        n_path = len(get_path_objects())
        layout.label("Total PATH_: %d" % n_path, icon='INFO')

        layout.separator()

        # ── PASSENGERCABIN ────────────────────────────
        box = layout.box()
        box.label("Passenger Cabin (passengercabin.cfg):", icon='ARMATURE_DATA')
        box.operator("omsi.add_passpos",       icon='ZOOMIN', text="Adicionar PASSPOS_N")
        box.operator("omsi.export_passcabin",  icon='EXPORT',  text="Exportar PassengerCabin CFG")

        if obj and obj.name.startswith("PASSPOS_"):
            sub = box.box()
            sub.label("Selecionado: " + obj.name, icon='ARROWS_BACK')
            if "omsi_h"   in obj: sub.prop(obj, '["omsi_h"]',   text="Altura h (0=em pe)")
            if "omsi_rot" in obj: sub.prop(obj, '["omsi_rot"]', text="Rotacao (graus)")

        n_pass = len(get_passpos_objects())
        layout.label("Total PASSPOS_: %d" % n_pass, icon='INFO')

        layout.separator()

        # ── DICA ──────────────────────────────────────
        box = layout.box()
        box.label("Nomes especiais:", icon='QUESTION')
        col = box.column(align=True)
        col.label("DRIVPOS       -> motorista")
        col.label("ENTRY_N       -> [entry]  (omsi_pathpnt)")
        col.label("EXIT_N        -> [exit]   (omsi_pathpnt)")
        col.label("LINKTOPREV    -> [linkToPrevVeh]")
        col.label("LINKTONEXT    -> [linkToNextVeh]")
        col.label("STAMPER_N     -> [stamper]")


# ─── Registro ─────────────────────────────────────────────────────────────────

classes = (
    OMSI_OT_AddPathPoint,
    OMSI_OT_AddRoomHeight,
    OMSI_OT_ExportPath,
    OMSI_OT_AddPassPos,
    OMSI_OT_ExportPassCabin,
    OMSI_PT_MainPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
