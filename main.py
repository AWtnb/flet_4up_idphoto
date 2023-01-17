from pathlib import Path

from PIL import Image
import flet as ft


def with_stem_tail(path:str, tail:str) -> str:
    target = Path(path)
    return str(target.stem + tail + target.suffix)

def allocate(path:str, out_dir:str, photo_width_mm:int=30, max_frame_width:int=2000):
    out_path = Path(out_dir, with_stem_tail(path, "_print"))
    img = Image.open(path)
    img_width, img_height = img.size
    frame_width = int(img_width * 89 / int(photo_width_mm))
    frame_height = int(frame_width * 1.43)
    frame = Image.new("RGB", (frame_width, frame_height), (255,255,255))
    margin_x = int(frame_width * 0.05)
    margin_y = int(frame_height * 0.05)
    for x in (margin_x, (frame_width - img_width - margin_x)):
        for y in (margin_y, frame_height - img_height - margin_y):
            frame.paste(img, (x, y))
    if frame.width > max_frame_width:
        frame = frame.resize((max_frame_width, int(frame.height * max_frame_width / frame_width)))
    frame.save(out_path, quality=95)



def main(page: ft.Page):
    page.title = "4up"
    page.theme_mode = "light"

    target_file = ft.Ref[ft.Text]()
    output_folder = ft.Ref[ft.Text]()
    result_message = ft.Ref[ft.Text]()
    photo_width_mm = ft.Ref[ft.TextField]()
    max_frame_width = ft.Ref[ft.TextField]()

    image_extensions = ["jpeg", "jpg", "png"]
    ui_rows = []


    ###################################
    # file picker
    ###################################

    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files:
            target_file.current.value = e.files[0].path
            output_folder.current.value = str(Path(target_file.current.value).parent)
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)

    def show_file_picker(_: ft.ControlEvent):
        file_picker.pick_files(
            allow_multiple=False,
            file_type="custom",
            allowed_extensions=image_extensions
        )

    ui_rows.append(ft.Row(controls=[
        ft.ElevatedButton("Select File", on_click=show_file_picker),
        ft.Text(ref=target_file)
    ]))


    ###################################
    # folder picker
    ###################################

    def on_folder_picked(e: ft.FilePickerResultEvent):
        if e.path:
            output_folder.current.value = e.path
            page.update()

    folder_picker = ft.FilePicker(on_result=on_folder_picked)
    page.overlay.append(folder_picker)

    def show_pick_folder(_: ft.ControlEvent):
        folder_picker.get_directory_path()

    ui_rows.append(ft.Row(controls=[
        ft.ElevatedButton("Select Output Folder", on_click=show_pick_folder),
        ft.Text(ref=output_folder)
    ]))


    ###################################
    # execute button
    ###################################

    def execute(_: ft.ControlEvent):
        if not target_file.current.value or not output_folder.current.value:
            return
        result_message.current.value = ""
        page.update()
        if str(Path(target_file.current.value).suffix)[1:] in image_extensions:
            ui_controls.disabled = True
            allocate(
                target_file.current.value,
                output_folder.current.value,
                photo_width_mm.current.value,
                max_frame_width.current.value,
            )
            ui_controls.disabled = False
            result_message.current.value = "FINISHED!"
        else:
            result_message.current.value = "incorrect file..."
        page.update()


    ui_rows.append(ft.Row(controls=[
        ft.TextField(ref=max_frame_width, label="max image width (px)", width=200, keyboard_type="number", border_color="#aaaaaa", value=1500),
        ft.TextField(ref=photo_width_mm, label="photo width (mm)", width=200, keyboard_type="number", value=30),
    ]))
    ui_rows.append(ft.Row(controls=[
        ft.FilledButton("GO!", on_click=execute),
        ft.Text(ref=result_message)
    ]))


    ###################################
    # render page
    ###################################

    ui_rows = [ft.Text(
        "github.com/AWtnb/flet_4up_idphoto",
        style="labelSmall",
        weight="bold",
        color=ft.colors.BLUE_900,
    )] + ui_rows
    ui_controls = ft.Column(controls=ui_rows)
    page.add(ui_controls)


ft.app(target=main)