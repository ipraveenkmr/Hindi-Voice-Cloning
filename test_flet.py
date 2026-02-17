import flet as ft

def main(page: ft.Page):
    page.title = "Glassmorphism Test"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.colors.BLUE_GREY_900

    glass_card = ft.Container(
        content=ft.Column([
            ft.Text("Glassmorphism", size=30, weight="bold", color=ft.colors.WHITE),
            ft.Text("This is a glassmorphic card.", color=ft.colors.WHITE70),
            ft.ElevatedButton("Click Me")
        ]),
        padding=40,
        width=300,
        border_radius=20,
        bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
        blur=ft.Blur(10, 10, ft.BlurStyle.OUTER),
        border=ft.border.all(1, ft.colors.with_opacity(0.2, ft.colors.WHITE)),
    )
    
    page.add(
        ft.Stack([
            ft.Container(
                content=ft.CircleAvatar(radius=100, bgcolor=ft.colors.PINK_400),
                top=50, left=50
            ),
            ft.Container(
                content=ft.CircleAvatar(radius=80, bgcolor=ft.colors.CYAN_400),
                bottom=50, right=50
            ),
            glass_card
        ])
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)
