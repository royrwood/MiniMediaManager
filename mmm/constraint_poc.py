import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, Gio, GObject, GLib


class ConstraintLayoutDemo(Gtk.Widget):
    def __init__(self):
        super().__init__()

        self.constraint_layout_manager = Gtk.ConstraintLayout()
        self.set_layout_manager(self.constraint_layout_manager)

        # self.left_constraint_guide = Gtk.ConstraintGuide(name='leftGuide', min_width=10, max_width=2000, min_height=10, max_height=2000, nat_width=200, nat_height=100, strength=Gtk.ConstraintStrength.STRONG)
        self.left_constraint_guide = Gtk.ConstraintGuide(name='leftGuide', strength=Gtk.ConstraintStrength.STRONG)
        self.constraint_layout_manager.add_guide(self.left_constraint_guide)

        self.button_1 = Gtk.Button(label='Button 1')
        self.button_1.set_parent(self)
        # self.button_2 = Gtk.Button(label='Button 2')
        # self.button_2.set_parent(self)
        # self.button_3 = Gtk.Button(label='Button 3')
        # self.button_3.set_parent(self)

        # # layout_manager: Gtk.ConstraintLayout = self.get_layout_manager()
        # layout_manager: Gtk.ConstraintLayout = self.get_layout_manager()

        self.build_constraints()

    def build_constraints(self):
        # vfl_constraints = [
        #     "H:|-[button1(==button2)]-12-[button2]-|",
        #     "H:|-[button3]-|",
        #     "V:|-[button1]-12-[button3(==button1)]-|",
        #     "V:|-[button2]-12-[button3(==button2)]-|"
        # ]

        vfl_constraints = [
            "H:|-[leftGuide][button1(<=200)]-|",
            "V:|-[leftGuide]-|",
            "V:|-[button1(<=100)]-|",
        ]
        views = {'button1': self.button_1, 'leftGuide': self.left_constraint_guide}
        self.constraint_layout_manager.add_constraints_from_description(vfl_constraints, hspacing=10, vspacing=10, views=views)

        #   gtk_constraint_layout_add_constraints_from_description (manager, vfl, G_N_ELEMENTS (vfl),
        #                                                           8, 8,
        #                                                           &error,
        #                                                           "button1", self->button1,
        #                                                           "button2", self->button2,
        #                                                           "button3", self->button3,
        #                                                           NULL);
