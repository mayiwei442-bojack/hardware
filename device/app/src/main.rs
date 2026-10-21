#![cfg_attr(target_os = "windows", windows_subsystem = "windows")]

fn main() {
    if keyboard_app::status_ipc::run_cli_if_requested() {
        return;
    }
    keyboard_app::gpui_app::run()
}
