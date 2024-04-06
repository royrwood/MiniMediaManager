import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


# Layout:
#
#   +-----------------------------+
#   | +-----------+ +-----------+ |
#   | |  Child 1  | |  Child 2  | |
#   | +-----------+ +-----------+ |
#   | +-------------------------+ |
#   | |         Child 3         | |
#   | +-------------------------+ |
#   +-----------------------------+
#
# Constraints:
#
#   super.start = child1.start - 8
#   child1.width = child2.width
#   child1.end = child2.start - 12
#   child2.end = super.end - 8
#   super.start = child3.start - 8
#   child3.end = super.end - 8
#   super.top = child1.top - 8
#   super.top = child2.top - 8
#   child1.bottom = child3.top - 12
#   child2.bottom = child3.top - 12
#   child3.height = child1.height
#   child3.height = child2.height
#   child3.bottom = super.bottom - 8
#
# Visual format:
#
#   H:|-8-[view1(==view2)-12-[view2]-8-|
#   H:|-8-[view3]-8-|
#   V:|-8-[view1]-12-[view3(==view1)]-8-|
#   V:|-8-[view2]-12-[view3(==view2)]-8-|

class ConstraintLayoutDemoWidget(Gtk.Widget):
    def __init__(self):
        super().__init__(hexpand=True, vexpand=True)

        self.constraint_layout_manager = Gtk.ConstraintLayout()
        self.set_layout_manager(self.constraint_layout_manager)

        self.button_1 = Gtk.Button(name='button1', label='Button 1')
        self.button_1.set_parent(self)
        self.button_2 = Gtk.Button(name='button2', label='Button 2')
        self.button_2.set_parent(self)
        self.button_3 = Gtk.Button(name='button3', label='Button 3')
        self.button_3.set_parent(self)

        vfl_constraints = [
            "H:|-[button1(==button2)]-12-[button2]-|",
            "H:|-[button3]-|",
            "V:|-[button1]-12-[button3(==button1)]-|",
            "V:|-[button2]-12-[button3(==button2)]-|",
        ]
        views = {'button1': self.button_1, 'button2': self.button_2, 'button3': self.button_3}
        self.constraint_layout_manager.add_constraints_from_description(vfl_constraints, hspacing=10, vspacing=10, views=views)

    def __del__(self):
        self.button_1.unparent()
        self.button_2.unparent()
        self.button_3.unparent()


def on_activate(app):
    application_window = Gtk.ApplicationWindow(application=app)

    constraint_widget = ConstraintLayoutDemoWidget()

    box = Gtk.Box()
    box.append(constraint_widget)
    application_window.set_child(box)

    application_window.present()


if __name__ == '__main__':
    # Create a new application
    app = Gtk.Application(application_id='com.example.GtkApplication')
    app.connect('activate', on_activate)

    # Run the application
    app.run(None)
