import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gio, GObject, GLib


class SimpleGrid(Gtk.Widget):
    def __init__(self):
        super().__init__()

        # foo = self.get_layout_manager_type()
        # layout_manager: Gtk.ConstraintLayout = self.get_layout_manager()
        # self.set_layout_manager_type(Gtk.ConstraintLayout)

        self.button_1 = Gtk.Button(label='Button 1')
        self.button_1.set_parent(self)
        # self.button_2 = Gtk.Button(label='Button 2')
        # self.button_2.set_parent(self)
        # self.button_3 = Gtk.Button(label='Button 3')
        # self.button_3.set_parent(self)

        self.constraint_layout_manager = Gtk.ConstraintLayout()
        self.set_layout_manager(self.constraint_layout_manager)

        # # layout_manager: Gtk.ConstraintLayout = self.get_layout_manager()
        # layout_manager: Gtk.ConstraintLayout = self.get_layout_manager()

        self.build_constraints(self.constraint_layout_manager)

    def build_constraints(self, layout_manager):
        constraint_constant = Gtk.Constraint(target=self.button_1, target_attribute=Gtk.ConstraintAttribute.WIDTH, relation=Gtk.ConstraintRelation.EQ, constant=200.0, strength=Gtk.ConstraintStrength.REQUIRED)
        layout_manager.add_constraint(constraint_constant)

        # gtk_constraint_layout_add_constraint(manager,
        #                                      gtk_constraint_new_constant(GTK_CONSTRAINT_TARGET(self->button1),
        # GTK_CONSTRAINT_ATTRIBUTE_WIDTH,
        # GTK_CONSTRAINT_RELATION_LE,
        # 200.0,
        # GTK_CONSTRAINT_STRENGTH_REQUIRED));



